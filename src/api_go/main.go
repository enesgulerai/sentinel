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

	// 1. Redis Connection
	redisHost := getEnv("REDIS_HOST", "localhost")
	redisPort := getEnv("REDIS_PORT", "6379")

	redisClient = redis.NewClient(&redis.Options{
		Addr: fmt.Sprintf("%s:%s", redisHost, redisPort),
		DB:   0,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := redisClient.Ping(ctx).Err(); err != nil {
		log.Fatalf("FATAL: Redis connection failed -> %v", err)
	}
	log.Printf("SUCCESS: Connected to Redis at %s:%s", redisHost, redisPort)

	// 2. Redpanda (Kafka) Connection
	kafkaBroker := getEnv("REDPANDA_BROKER", "localhost:19092")
	topicName := getEnv("KAFKA_TOPIC", "transactions")

	// Using segmentio/kafka-go for high performance and no CGO requirement
	kafkaWriter = &kafka.Writer{
		Addr:         kafka.TCP(kafkaBroker),
		Topic:        topicName,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 5 * time.Millisecond, // Reduced for lower latency
		RequiredAcks: kafka.RequireOne,     // Leader acknowledgement
	}
	log.Printf("SUCCESS: Connected to Redpanda at %s", kafkaBroker)
}

func main() {
	// Initialize external connections
	initServices()

	// Set Gin to release mode for maximum performance in production
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	// Profiling: Replaces PyInstrument. Go has built-in pprof.
	// You can access it via /debug/pprof/ to see millisecond-level CPU/Memory profiling.
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

	// Graceful Shutdown Setup (Replaces FastAPI @asynccontextmanager lifespan)
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

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down API...")

	// The context is used to inform the server it has 5 seconds to finish
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	// Close Redis and Kafka
	redisClient.Close()
	kafkaWriter.Close()

	log.Println("Shutdown complete.")
}

func ingestTransaction(c *gin.Context) {
	// Parse incoming JSON into a dynamic map
	var rawData map[string]any
	if err := c.ShouldBindJSON(&rawData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": "Invalid JSON payload format"})
		return
	}

	// Extract values safely
	txID, _ := rawData["transaction_id"].(string)

	var amount float64
	if amt, ok := rawData["Amount"].(float64); ok {
		amount = amt
	} else if amtStr, ok := rawData["Amount"].(string); ok {
		amount, _ = strconv.ParseFloat(amtStr, 64)
	}

	// Optimized Hashing Logic
	hashData := make(map[string]any)
	for k, v := range rawData {
		if k != "transaction_id" {
			hashData[k] = v
		}
	}

	// json.Marshal automatically sorts keys in Go maps, ensuring deterministic hashing
	hashBytes, err := json.Marshal(hashData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Failed to process transaction payload"})
		return
	}

	hash := sha256.Sum256(hashBytes)
	txHash := hex.EncodeToString(hash[:])
	redisKey := fmt.Sprintf("tx:%s", txHash)

	// Redis Atomic Idempotency Check (SET NX EX 10)
	isNew, err := redisClient.SetNX(c.Request.Context(), redisKey, "1", 10*time.Second).Result()
	if err != nil {
		log.Printf("Redis error during idempotency check: %v", err)
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

	// Route to Redpanda
	fullPayload, _ := json.Marshal(rawData)

	err = kafkaWriter.WriteMessages(c.Request.Context(), kafka.Message{
		Value: fullPayload,
	})
	if err != nil {
		log.Printf("Critical Gateway Error (Kafka): %v", err)
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
