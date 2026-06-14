package main

import (
	"context"
	"crypto/sha256"
	"database/sql"
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
	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"

	// --- OTEL IMPORTS ---
	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.17.0"

	// --- PROMETHEUS IMPORTS ---
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type KafkaProducer interface {
	WriteMessages(ctx context.Context, msgs ...kafka.Message) error
	Close() error
}

var (
	redisClient *redis.Client
	kafkaWriter KafkaProducer
	db          *sql.DB

	// --- PROMETHEUS METRICS ---
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

// --- OTEL INITIALIZATION ---
func initTracer() func(context.Context) error {
	jaegerEndpoint := getEnv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4318")

	exporter, err := otlptracehttp.New(context.Background(),
		otlptracehttp.WithEndpoint(jaegerEndpoint),
		otlptracehttp.WithInsecure(),
	)
	if err != nil {
		log.Fatalf("FATAL: Failed to create OTel exporter: %v", err)
	}

	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(resource.NewWithAttributes(
			semconv.SchemaURL,
			semconv.ServiceNameKey.String("sentinel-api"),
		)),
	)

	otel.SetTracerProvider(tp)
	otel.SetTextMapPropagator(propagation.TraceContext{})
	return tp.Shutdown
}

func initServices() {
	log.Println("Starting Sentinel ML API Gateway (Go/Gin)...")

	// --- REDIS CONFIG ---
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
		log.Fatalf("FATAL: Redis connection failed -> %v", err)
	}
	log.Printf("SUCCESS: Connected to Redis at %s:%s", redisHost, redisPort)

	// --- POSTGRESQL CONFIG ---
	pgHost := getEnv("POSTGRES_HOST", "localhost")
	pgPort := getEnv("POSTGRES_PORT", "5432")
	pgUser := getEnv("POSTGRES_USER", "postgres")
	pgPass := getEnv("POSTGRES_PASSWORD", "password")
	pgName := getEnv("POSTGRES_DB", "sentinel")

	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		pgHost, pgPort, pgUser, pgPass, pgName)

	var err error
	db, err = sql.Open("postgres", dsn)
	if err != nil {
		log.Fatalf("FATAL: Failed to open PostgreSQL driver: %v", err)
	}

	db.SetMaxOpenConns(50)
	db.SetMaxIdleConns(10)
	db.SetConnMaxLifetime(5 * time.Minute)

	if err := db.PingContext(ctx); err != nil {
		log.Fatalf("FATAL: PostgreSQL connection failed -> %v", err)
	}
	log.Printf("SUCCESS: Connected to PostgreSQL Pool at %s:%s", pgHost, pgPort)

	// --- KAFKA CONFIG ---
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
	log.Printf("SUCCESS: Connected to Redpanda at %s (Async Mode)", kafkaBroker)
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
	initServices()

	// --- OTEL START ---
	shutdownTracer := initTracer()
	defer func() {
		if err := shutdownTracer(context.Background()); err != nil {
			log.Printf("Error shutting down tracer: %v", err)
		}
	}()
	// --- OTEL END ---

	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Recovery())

	// --- OTEL GIN MIDDLEWARE ---
	router.Use(otelgin.Middleware("sentinel-api"))

	router.Use(metricsMiddleware())

	pprof.Register(router)

	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "online",
			"service": "Sentinel ML API (Go)",
			"version": "1.0.0",
		})
	})

	// --- PROMETHEUS ROUTE ---
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

	if db != nil {
		if err := db.Close(); err != nil {
			log.Printf("Error closing database: %v\n", err)
		}
	}

	if err := redisClient.Close(); err != nil {
		log.Printf("Error closing redis client: %v\n", err)
	}

	if err := kafkaWriter.Close(); err != nil {
		log.Printf("Error closing kafka writer: %v\n", err)
	}

	log.Println("Shutdown complete.")
}

func executeWithRetry(attempts int, initialDelay time.Duration, operation func() error) error {
	var err error
	for i := 0; i < attempts; i++ {
		if err = operation(); err == nil {
			return nil
		}
		time.Sleep(initialDelay * time.Duration(i+1))
	}
	return err
}

func ingestTransaction(c *gin.Context) {
	// --- OTEL SPAN START ---
	tracer := otel.Tracer("sentinel-api")
	ctx, span := tracer.Start(c.Request.Context(), "ingestTransaction")
	defer span.End()

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

	// --- OTEL REDIS SPAN ---
	_, redisSpan := tracer.Start(ctx, "Redis-SetNX")
	err = executeWithRetry(3, 10*time.Millisecond, func() error {
		isNew, redisErr = redisClient.SetNX(ctx, redisKey, "1", 10*time.Second).Result()
		return redisErr
	})
	redisSpan.End()

	if err != nil {
		log.Printf("Critical: Redis idempotency check failed after retries: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Internal Server Error"})
		return
	}

	if !isNew {
		transactionsProcessed.WithLabelValues("BLOCKED").Inc()
		c.JSON(http.StatusAccepted, gin.H{
			"status":  "ignored",
			"message": "Duplicate transaction detected",
			"source":  "Redis",
		})
		return
	}

	fullPayload, _ := json.Marshal(rawData)

	// --- OTEL KAFKA SPAN ---
	_, kafkaSpan := tracer.Start(ctx, "Kafka-Write")

	carrier := propagation.MapCarrier{}
	otel.GetTextMapPropagator().Inject(ctx, carrier)

	var kafkaHeaders []kafka.Header
	for k, v := range carrier {
		kafkaHeaders = append(kafkaHeaders, kafka.Header{
			Key:   k,
			Value: []byte(v),
		})
	}

	err = executeWithRetry(3, 15*time.Millisecond, func() error {
		return kafkaWriter.WriteMessages(ctx, kafka.Message{
			Headers: kafkaHeaders,
			Value:   fullPayload,
		})
	})
	kafkaSpan.End()

	if err != nil {
		log.Printf("Critical: Gateway failed to queue transaction to Kafka after retries: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"detail": "Failed to queue transaction"})
		return
	}

	transactionsProcessed.WithLabelValues("PASSED").Inc()
	c.JSON(http.StatusAccepted, gin.H{
		"status":         "success",
		"transaction_id": txID,
		"amount":         amount,
		"source":         "Redpanda",
	})
}
