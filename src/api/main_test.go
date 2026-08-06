package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redismock/v9"
	"github.com/goccy/go-json"
	"github.com/segmentio/kafka-go"
	"github.com/stretchr/testify/assert"
	"go.uber.org/zap"
)

// Mock Kafka Writer
type MockKafkaWriter struct {
	MessagesWritten int
	ShouldFail      bool
}

func (m *MockKafkaWriter) WriteMessages(ctx context.Context, msgs ...kafka.Message) error {
	if m.ShouldFail {
		return context.DeadlineExceeded
	}
	m.MessagesWritten += len(msgs)
	return nil
}

func (m *MockKafkaWriter) Close() error {
	return nil
}

// Test Environment Setup
func setupTestEnvironment() (*gin.Engine, redismock.ClientMock, *MockKafkaWriter) {
	if logger == nil {
		logger = zap.NewNop()
	}

	gin.SetMode(gin.TestMode)
	router := gin.New()
	router.POST("/api/v1/transactions", ingestTransaction)

	// Inject Redis Mock
	dbMock, redisMock := redismock.NewClientMock()
	redisClient = dbMock

	// Inject Kafka Mock
	kafkaMock := &MockKafkaWriter{}
	kafkaWriter = kafkaMock

	return router, redisMock, kafkaMock
}

func getExpectedRedisKey(payload TransactionPayload) string {
	// main.go ile birebir aynı mantık: Payload'un tamamı üzerinden SHA-256 hash üretilir
	hashBytes, _ := json.Marshal(payload)
	hash := sha256.Sum256(hashBytes)
	return "tx:" + hex.EncodeToString(hash[:])
}

// Test: Valid Transaction
func TestValidTransactionIngestion(t *testing.T) {
	router, redisMock, kafkaMock := setupTestEnvironment()

	payload := TransactionPayload{
		TransactionID: "TEST-1001",
		UserID:        "tester_01",
		Amount:        1500.50,
		V1:            -1.5,
	}
	expectedKey := getExpectedRedisKey(payload)

	redisMock.ExpectSetNX(expectedKey, "1", 10*time.Second).SetVal(true)

	jsonValue, _ := json.Marshal(payload)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/transactions", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusAccepted, w.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(w.Body.Bytes(), &response)

	assert.Equal(t, "success", response["status"])
	assert.Equal(t, 1, kafkaMock.MessagesWritten)
	assert.NoError(t, redisMock.ExpectationsWereMet())
}

// Test: Duplicate Transaction
func TestDuplicateTransactionRejected(t *testing.T) {
	router, redisMock, kafkaMock := setupTestEnvironment()

	payload := TransactionPayload{
		TransactionID: "TEST-1002",
		UserID:        "tester_02",
		Amount:        1500.50,
		V1:            -1.5,
	}
	expectedKey := getExpectedRedisKey(payload)

	redisMock.ExpectSetNX(expectedKey, "1", 10*time.Second).SetVal(false)

	jsonValue, _ := json.Marshal(payload)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/transactions", bytes.NewBuffer(jsonValue))
	req.Header.Set("Content-Type", "application/json")

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusAccepted, w.Code)

	var response map[string]interface{}
	_ = json.Unmarshal(w.Body.Bytes(), &response)

	assert.Equal(t, "ignored", response["status"])
	assert.Equal(t, "Duplicate transaction detected", response["message"])
	assert.Equal(t, 0, kafkaMock.MessagesWritten)
	assert.NoError(t, redisMock.ExpectationsWereMet())
}

// Test: Invalid Payload
func TestInvalidPayloadRejected(t *testing.T) {
	router, _, _ := setupTestEnvironment()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/transactions", bytes.NewBufferString("{invalid-json}"))
	req.Header.Set("Content-Type", "application/json")

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}
