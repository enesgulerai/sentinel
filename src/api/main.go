package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"github.com/gin-contrib/pprof"
	"github.com/gin-gonic/gin"
	"github.com/goccy/go-json"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"
	"go.uber.org/zap"

	// Prometheus Imports
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type KafkaProducer interface {
	WriteMessages(ctx context.Context, msgs ...kafka.Message) error
	Close() error
}

type TransactionPayload struct {
	TransactionID string  `json:"transaction_id"`
	UserID        string  `json:"user_id"`
	Amount        float64 `json:"Amount"`
	Time          float64 `json:"Time"`
	V1            float64 `json:"V1"`
	V2            float64 `json:"V2"`
	V3            float64 `json:"V3"`
	V4            float64 `json:"V4"`
	V5            float64 `json:"V5"`
	V6            float64 `json:"V6"`
	V7            float64 `json:"V7"`
	V8            float64 `json:"V8"`
	V9            float64 `json:"V9"`
	V10           float64 `json:"V10"`
	V11           float64 `json:"V11"`
	V12           float64 `json:"V12"`
	V13           float64 `json:"V13"`
	V14           float64 `json:"V14"`
	V15           float64 `json:"V15"`
	V16           float64 `json:"V16"`
	V17           float64 `json:"V17"`
	V18           float64 `json:"V18"`
	V19           float64 `json:"V19"`
	V20           float64 `json:"V20"`
	V21           float64 `json:"V21"`
	V22           float64 `json:"V22"`
	V23           float64 `json:"V23"`
	V24           float64 `json:"V24"`
	V25           float64 `json:"V25"`
	V26           float64 `json:"V26"`
	V27           float64 `json:"V27"`
	V28           float64 `json:"V28"`
}

type TransactionHashData struct {
	UserID string  `json:"user_id"`
	Amount float64 `json:"Amount"`
	Time   float64 `json:"Time"`
	V1     float64 `json:"V1"`
	V2     float64 `json:"V2"`
	V3     float64 `json:"V3"`
	V4     float64 `json:"V4"`
	V5     float64 `json:"V5"`
	V6     float64 `json:"V6"`
	V7     float64 `json:"V7"`
	V8     float64 `json:"V8"`
	V9     float64 `json:"V9"`
	V10    float64 `json:"V10"`
	V11    float64 `json:"V11"`
	V12    float64 `json:"V12"`
	V13    float64 `json:"V13"`
	V14    float64 `json:"V14"`
	V15    float64 `json:"V15"`
	V16    float64 `json:"V16"`
	V17    float64 `json:"V17"`
	V18    float64 `json:"V18"`
	V19    float64 `json:"V19"`
	V20    float64 `json:"V20"`
	V21    float64 `json:"V21"`
	V22    float64 `json:"V22"`
	V23    float64 `json:"V23"`
	V24    float64 `json:"V24"`
	V25    float64 `json:"V25"`
	V26    float64 `json:"V26"`
	V27    float64 `json:"V27"`
	V28    float64 `json:"V28"`
}

type RootResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
}

type ErrorResponse struct {
	Detail string `json:"detail"`
}

type IgnoredResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Source  string `json:"source"`
}

type SuccessResponse struct {
	Status        string  `json:"status"`
	TransactionID string  `json:"transaction_id"`
	Amount        float64 `json:"amount"`
	Source        string  `json:"source"`
}

var (
	logger      = zap.NewNop()
	redisClient *redis.Client
	kafkaWriter KafkaProducer

	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "sentinel_api_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "path", "status"},
	)
	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "sentinel_api_request_duration_seconds",
			Help:    "Histogram of response latency (seconds)",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "path"},
	)
	transactionsProcessed = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "sentinel_transactions_total",
			Help: "Total number of processed transactions by status",
		},
		[]string{"status"},
	)
)

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

func initServices() {
	logger.Info("Starting Sentinel ML API Gateway (Go/Gin) - Max Performance Version (OTel Disabled)...")

	redisHost := getEnv("REDIS_HOST", "localhost")
	redisPort := getEnv("REDIS_PORT", "6379")

	redisClient = redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", redisHost, redisPort),
		DB:           0,
		PoolSize:     250,
		MinIdleConns: 50,
		DialTimeout:  5 * time.Second,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
		PoolTimeout:  4 * time.Second,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := redisClient.Ping(ctx).Err(); err != nil {
		logger.Fatal("Redis connection failed", zap.Error(err))
	}
	logger.Info("Connected to Redis", zap.String("host", redisHost), zap.String("port", redisPort))

	kafkaBroker := getEnv("REDPANDA_BROKER", "localhost:19092")
	topicName := getEnv("KAFKA_TOPIC", "raw-events")

	kafkaWriter = &kafka.Writer{
		Addr:         kafka.TCP(kafkaBroker),
		Topic:        topicName,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 5 * time.Millisecond,
		RequiredAcks: kafka.RequireOne,
		Async:        true,
		BatchSize:    100,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
	}
	logger.Info("Connected to Redpanda (Async Mode)", zap.String("broker", kafkaBroker))
}

func metricsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		duration := time.Since(start).Seconds()
		status := strconv.Itoa(c.Writer.Status())

		httpRequestsTotal.WithLabelValues(c.Request.Method, c.FullPath(), status).Inc()
		httpRequestDuration.WithLabelValues(c.Request.Method, c.FullPath()).Observe(duration)
	}
}

func main() {
	logger, _ = zap.NewProduction()
	defer func() { _ = logger.Sync() }()

	initServices()

	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Recovery())

	router.Use(metricsMiddleware())
	pprof.Register(router)

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, RootResponse{
			Status:  "online",
			Service: "Sentinel ML API (Go)",
			Version: "1.16.2-max-performance",
		})
	})

	// Health and Readiness endpoints for Kubernetes
	router.GET("/healthz", func(c *gin.Context) {
		c.String(http.StatusOK, "OK")
	})
	router.GET("/readyz", func(c *gin.Context) {
		c.String(http.StatusOK, "OK")
	})

	router.GET("/metrics", gin.WrapH(promhttp.Handler()))
	router.POST("/api/v1/transactions", ingestTransaction)

	apiPort := getEnv("PORT", "8000")
	srv := &http.Server{
		Addr:              ":" + apiPort,
		Handler:           router,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Listen error", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logger.Info("Shutting down API...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		logger.Fatal("Server forced to shutdown", zap.Error(err))
	}

	if err := redisClient.Close(); err != nil {
		logger.Error("Error closing redis client", zap.Error(err))
	}

	if err := kafkaWriter.Close(); err != nil {
		logger.Error("Error closing kafka writer", zap.Error(err))
	}

	logger.Info("Shutdown complete.")
}

func executeWithRetry(ctx context.Context, attempts int, initialDelay time.Duration, operation func() error) error {
	var err error
	for i := 0; i < attempts; i++ {
		if ctx.Err() != nil {
			return ctx.Err()
		}

		if err = operation(); err == nil {
			return nil
		}

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(initialDelay * time.Duration(i+1)):
		}
	}
	return err
}

func ingestTransaction(c *gin.Context) {
	reqCtx, cancel := context.WithTimeout(c.Request.Context(), 2*time.Second)
	defer cancel()

	bodyBytes, err := io.ReadAll(c.Request.Body)
	if err != nil || len(bodyBytes) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{Detail: "Invalid payload"})
		return
	}

	var payload TransactionPayload
	if err := json.Unmarshal(bodyBytes, &payload); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Detail: "Invalid JSON format"})
		return
	}

	hashData := TransactionHashData{
		UserID: payload.UserID,
		Amount: payload.Amount,
		Time:   payload.Time,
		V1:     payload.V1,
		V2:     payload.V2,
		V3:     payload.V3,
		V4:     payload.V4,
		V5:     payload.V5,
		V6:     payload.V6,
		V7:     payload.V7,
		V8:     payload.V8,
		V9:     payload.V9,
		V10:    payload.V10,
		V11:    payload.V11,
		V12:    payload.V12,
		V13:    payload.V13,
		V14:    payload.V14,
		V15:    payload.V15,
		V16:    payload.V16,
		V17:    payload.V17,
		V18:    payload.V18,
		V19:    payload.V19,
		V20:    payload.V20,
		V21:    payload.V21,
		V22:    payload.V22,
		V23:    payload.V23,
		V24:    payload.V24,
		V25:    payload.V25,
		V26:    payload.V26,
		V27:    payload.V27,
		V28:    payload.V28,
	}

	hashBytes, err := json.Marshal(hashData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Detail: "Hash generation failed"})
		return
	}

	hash := sha256.Sum256(hashBytes)
	txHash := hex.EncodeToString(hash[:])
	redisKey := fmt.Sprintf("tx:%s", txHash)

	var isNew bool
	var redisErr error

	err = executeWithRetry(reqCtx, 3, 10*time.Millisecond, func() error {
		isNew, redisErr = redisClient.SetNX(reqCtx, redisKey, "1", 10*time.Second).Result()
		return redisErr
	})

	if err != nil {
		logger.Error("Redis idempotency check failed", zap.Error(err))
		c.JSON(http.StatusInternalServerError, ErrorResponse{Detail: "Internal Server Error"})
		return
	}

	if !isNew {
		transactionsProcessed.WithLabelValues("BLOCKED").Inc()
		c.JSON(http.StatusAccepted, IgnoredResponse{
			Status:  "ignored",
			Message: "Duplicate transaction detected",
			Source:  "Redis",
		})
		return
	}

	// OTel kaldirildigi icin artik header'lara trace_id basmiyoruz.
	// Sadece payload'u gonderiyoruz.
	err = executeWithRetry(reqCtx, 3, 15*time.Millisecond, func() error {
		return kafkaWriter.WriteMessages(reqCtx, kafka.Message{
			Value: bodyBytes,
		})
	})

	if err != nil {
		logger.Error("Kafka queue failed", zap.Error(err))
		c.JSON(http.StatusInternalServerError, ErrorResponse{Detail: "Failed to queue transaction"})
		return
	}

	transactionsProcessed.WithLabelValues("PASSED").Inc()
	c.JSON(http.StatusAccepted, SuccessResponse{
		Status:        "success",
		TransactionID: payload.TransactionID,
		Amount:        payload.Amount,
		Source:        "Redpanda",
	})
}
