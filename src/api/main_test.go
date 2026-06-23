package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redismock/v9"
	"github.com/segmentio/kafka-go"
	"github.com/stretchr/testify/assert"
)

// ==========================================
// MOCK KAFKA PRODUCER
// ==========================================
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

// ==========================================
// TEST ENVIRONMENT SETUP
// ==========================================
func setupTestEnvironment() (*gin.Engine, redismock.ClientMock, *MockKafkaWriter) {
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

func getExpectedRedisKey(payload map[string]interface{}) string {
	hashData := make(map[string]interface{})
	for k, v := range payload {
		if k != "transaction_id" {
			hashData[k] = v
		}
	}
	hashBytes, _ := json.Marshal(hashData)
	hash := sha256.Sum256(hashBytes)
	return "tx:" + hex.EncodeToString(hash[:])
}

// ==========================================
// 1. TEST: VALID TRANSACTION
// ==========================================
func TestValidTransactionIngestion(t *testing.T) {
	router, redisMock, kafkaMock := setupTestEnvironment()

	payload := map[string]interface{}{
		"transaction_id": "TEST-1001",
		"Amount":         1500.50,
		"V1":             -1.5,
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

// ==========================================
// 2. TEST: DUPLICATE TRANSACTION
// ==========================================
func TestDuplicateTransactionRejected(t *testing.T) {
	router, redisMock, kafkaMock := setupTestEnvironment()

	payload := map[string]interface{}{
		"transaction_id": "TEST-1002",
		"Amount":         1500.50,
		"V1":             -1.5,
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

// ==========================================
// 3. TEST: INVALID PAYLOAD
// ==========================================
func TestInvalidPayloadRejected(t *testing.T) {
	router, _, _ := setupTestEnvironment()

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/api/v1/transactions", bytes.NewBufferString("{invalid-json}"))
	req.Header.Set("Content-Type", "application/json")

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}
