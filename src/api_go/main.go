package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/gin-contrib/pprof"
	"github.com/gin-gonic/gin"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"
)

var (
	redisClient *redis.Client
	kafkaWriter *kafka.Writer
)

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func initServices() {
	log.Println("Starting Sentinel ML API Gateway (Go/Gin)...")

	redisHost := getEnv("REDIS_HOST", "localhost")
	redisPort := getEnv("REDIS_PORT", "6379")

	// Optimized Redis Pool for high concurrency
	redisClient = redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", redisHost, redisPort),
		DB:           0,
		PoolSize:     250, // Match or exceed max concurrent workers (-c 200)
		MinIdleConns: 50,  // Keep connections alive to prevent dial-up overhead
		DialTimeout:  5 * time.Second,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
		PoolTimeout:  4 * time.Second, // Amount of time client waits for connection if all are busy
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := redisClient.Ping(ctx).Err(); err != nil {
		log.Fatalf("FATAL: Redis connection failed -> %v", err)
	}
	log.Printf("SUCCESS: Connected to Redis at %s:%s", redisHost, redisPort)

	kafkaBroker := getEnv("REDPANDA_BROKER", "localhost:19092")
	topicName := getEnv("KAFKA_TOPIC", "transactions")

	// Optimized Redpanda Writer
	kafkaWriter = &kafka.Writer{
		Addr:         kafka.TCP(kafkaBroker),
		Topic:        topicName,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 5 * time.Millisecond,
		RequiredAcks: kafka.RequireOne,
		Async:        true,
		// Enlarge inner buffers for concurrent writes
		BatchSize:    100,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
	}
	log.Printf("SUCCESS: Connected to Redpanda at %s (Async Mode)", kafkaBroker)
}

func main() {
	initServices()

	// Set Gin to release mode and use a blank instance to disable stdout logging
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Recovery()) // Protects the gateway from panics without disk I/O blocking

	// Profiling toolchain configuration
	pprof.Register(router)

	// Health Check
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "online",
			"service": "Sentinel ML API (Go)",
			"version": "1.1.0",
		})
	})

	// Transactions Endpoint
	router.POST("/api/v1/transactions", ingestTransaction)

	apiPort := getEnv("PORT", "8000")
	srv := &http.Server{
		Addr:    ":" + apiPort,
		Handler: router,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Listen error: %s\n", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down API...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	redisClient.Close()
	kafkaWriter.Close()

	log.Println("Shutdown complete.")
}

// Helper function to retry critical I/O operations gracefully
func executeWithRetry(attempts int, initialDelay time.Duration, operation func() error) error {
	var err error
	for i := 0; i < attempts; i++ {
		if err = operation(); err == nil {
			return nil
		}
		// Wait before retrying (incremental backoff)
		time.Sleep(initialDelay * time.Duration(i+1))
	}
	return err
}

func ingestTransaction(c *gin.Context) {
	var rawData map[string]any
	if err := c.ShouldBindJSON(&rawData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": "Invalid JSON payload format"})
		return
	}

	txID, _ := rawData["transaction_id"].(string)

	var amount float64
	if amt, ok := rawData["Amount"].(float64); ok {
		amount = amt
	} else if amtStr, ok := rawData["Amount"].(string); ok {
		amount, _ = strconv.ParseFloat(amtStr, 64)
	}

	hashData := make(map[string]any)
	for k, v := range rawData {
		if k != "transaction_id" {
			hashData[k] = v
		}
	}

	hashBytes, err := json.Marshal(hashData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Failed to process transaction payload"})
		return
	}

	hash := sha256.Sum256(hashBytes)
	txHash := hex.EncodeToString(hash[:])
	redisKey := fmt.Sprintf("tx:%s", txHash)

	var isNew bool
	var redisErr error

	// 1. Redis Idempotency Check with Retry
	err = executeWithRetry(3, 10*time.Millisecond, func() error {
		isNew, redisErr = redisClient.SetNX(c.Request.Context(), redisKey, "1", 10*time.Second).Result()
		return redisErr
	})

	if err != nil {
		log.Printf("Critical: Redis idempotency check failed after retries: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Internal Server Error"})
		return
	}

	if !isNew {
		c.JSON(http.StatusAccepted, gin.H{
			"status":  "ignored",
			"message": "Duplicate transaction detected",
			"source":  "Redis",
		})
		return
	}

	fullPayload, _ := json.Marshal(rawData)

	// 2. Kafka Write with Retry
	err = executeWithRetry(3, 15*time.Millisecond, func() error {
		return kafkaWriter.WriteMessages(c.Request.Context(), kafka.Message{
			Value: fullPayload,
		})
	})

	if err != nil {
		log.Printf("Critical: Gateway failed to queue transaction to Kafka after retries: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Failed to queue transaction"})
		return
	}

	c.JSON(http.StatusAccepted, gin.H{
		"status":         "success",
		"transaction_id": txID,
		"amount":         amount,
		"source":         "Redpanda",
	})
}
