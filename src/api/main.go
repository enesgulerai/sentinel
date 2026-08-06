package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/gin-contrib/pprof"
	"github.com/gin-gonic/gin"
	"github.com/goccy/go-json"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"
	"go.uber.org/zap"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var payloadPool = sync.Pool{
	New: func() interface{} {
		return new(TransactionPayload)
	},
}

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
	logger.Info("Starting Sentinel ML API Gateway - High Throughput (Zero-Allocation) Version...")

	redisHost := getEnv("REDIS_HOST", "localhost")
	redisPort := getEnv("REDIS_PORT", "6379")

	redisClient = redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", redisHost, redisPort),
		DB:           0,
		PoolSize:     500,
		MinIdleConns: 100,
		DialTimeout:  2 * time.Second,
		ReadTimeout:  500 * time.Millisecond,
		WriteTimeout: 500 * time.Millisecond,
		PoolTimeout:  2 * time.Second,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
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
		BatchTimeout: 2 * time.Millisecond,
		RequiredAcks: kafka.RequireNone,
		Async:        true,
		BatchSize:    500,
	}
	logger.Info("Connected to Redpanda (Fire&Forget Async Mode)", zap.String("broker", kafkaBroker))

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

	router.GET("/health/startup", func(c *gin.Context) { c.String(http.StatusOK, "OK") })
	router.GET("/health/live", func(c *gin.Context) { c.String(http.StatusOK, "OK") })
	router.GET("/health/ready", func(c *gin.Context) { c.String(http.StatusOK, "OK") })
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"service":     "sentinel-ml-api-gateway",
			"version":     "v1.0.0",
			"status":      "operational",
			"environment": getEnv("ENVIRONMENT", "development"),
			"timestamp":   time.Now().UTC().Format(time.RFC3339),
		})
	})

	router.POST("/api/v1/transactions", ingestTransaction)

	apiPort := getEnv("PORT", "8000")
	srv := &http.Server{
		Addr:              ":" + apiPort,
		Handler:           router,
		ReadHeaderTimeout: 2 * time.Second,
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

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	_ = srv.Shutdown(shutdownCtx)
	_ = redisClient.Close()
	_ = kafkaWriter.Close()
	logger.Info("Shutdown complete.")
}

func ingestTransaction(c *gin.Context) {
	reqCtx, cancel := context.WithTimeout(c.Request.Context(), 200*time.Millisecond)
	defer cancel()

	bodyBytes, err := c.GetRawData()
	if err != nil || len(bodyBytes) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{Detail: "Invalid payload"})
		return
	}

	payload := payloadPool.Get().(*TransactionPayload)

	defer payloadPool.Put(payload)

	if err := json.Unmarshal(bodyBytes, payload); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{Detail: "Invalid JSON format"})
		return
	}

	hashInput := fmt.Sprintf("%s|%f|%f|%f|%f|%f",
		payload.UserID, payload.Amount, payload.Time, payload.V1, payload.V2, payload.V3) // Tüm V değerlerini buraya ekleyebilirsin

	hash := sha256.Sum256([]byte(hashInput))
	txHash := hex.EncodeToString(hash[:])
	redisKey := "tx:" + txHash

	isNew, redisErr := redisClient.SetNX(reqCtx, redisKey, "1", 10*time.Second).Result()
	if redisErr != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{Detail: "Idempotency check failed"})
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

	kafkaErr := kafkaWriter.WriteMessages(reqCtx, kafka.Message{
		Value: bodyBytes,
	})

	if kafkaErr != nil {
		logger.Error("Redpanda queue failed", zap.Error(kafkaErr))
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
