use rskafka::client::ClientBuilder;
use rskafka::client::partition::{OffsetAt, UnknownTopicHandling, Compression};
use rskafka::record::Record;
use serde::Deserialize;
use std::time::Duration;
use std::env;
use std::collections::BTreeMap;

use opentelemetry::{global, KeyValue};
use opentelemetry::trace::{Tracer, Span, Status};
use opentelemetry::propagation::Extractor;
use opentelemetry_sdk::trace as sdktrace;
use opentelemetry_sdk::Resource;
use opentelemetry_sdk::trace::TracerProvider;
use opentelemetry_otlp::WithExportConfig;

#[derive(Debug, Deserialize)]
#[allow(non_snake_case)]
#[allow(dead_code)]
struct FraudEvent {
    transaction_id: String,
    user_id: Option<String>,
    Time: f64,
    V1: f64, V2: f64, V3: f64, V4: f64, V5: f64, V6: f64, V7: f64,
    V8: f64, V9: f64, V10: f64, V11: f64, V12: f64, V13: f64, V14: f64,
    V15: f64, V16: f64, V17: f64, V18: f64, V19: f64, V20: f64, V21: f64,
    V22: f64, V23: f64, V24: f64, V25: f64, V26: f64, V27: f64, V28: f64,
    Amount: f64,
}

// Extractor to read OpenTelemetry Context from Kafka Headers
struct KafkaHeaderExtractor<'a>(&'a BTreeMap<String, Vec<u8>>);

impl<'a> Extractor for KafkaHeaderExtractor<'a> {
    fn get(&self, key: &str) -> Option<&str> {
        self.0.get(key).and_then(|v| std::str::from_utf8(v).ok())
    }

    fn keys(&self) -> Vec<&str> {
        self.0.keys().map(|k| k.as_str()).collect()
    }
}

fn init_tracer() {
    let endpoint = env::var("OTEL_EXPORTER_OTLP_ENDPOINT")
        .unwrap_or_else(|_| "http://jaeger:4318/v1/traces".to_string());

    let exporter = opentelemetry_otlp::new_exporter()
        .http()
        .with_endpoint(endpoint);

    let _ = opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(exporter)
        .with_trace_config(
            sdktrace::config().with_resource(Resource::new(vec![KeyValue::new(
                "service.name",
                "sentinel-validator",
            )])),
        )
        .install_batch(opentelemetry_sdk::runtime::Tokio)
        .expect("Failed to initialize OTel pipeline");

    global::set_text_map_propagator(opentelemetry_sdk::propagation::TraceContextPropagator::new());
}

#[tokio::main]
async fn main() {
    println!("Sentinel Rust Validator initializing...");

    // Initialize OpenTelemetry
    init_tracer();
    let tracer = global::tracer("sentinel-validator");

    let connection_string = env::var("REDPANDA_BROKER").unwrap_or_else(|_| "localhost:19092".to_string());
    let client = match ClientBuilder::new(vec![connection_string.to_owned()]).build().await {
        Ok(c) => c,
        Err(e) => {
            println!("FATAL: Connection failed. Error: {:?}", e);
            return;
        }
    };

    let raw_partition_client = match client.partition_client("raw-events", 0, UnknownTopicHandling::Retry).await {
        Ok(pc) => pc,
        Err(e) => {
            println!("FATAL: Failed to create raw-events partition client: {:?}", e);
            return;
        }
    };

    let clean_partition_client = match client.partition_client("clean-events", 0, UnknownTopicHandling::Retry).await {
        Ok(pc) => pc,
        Err(e) => {
            println!("FATAL: Failed to create clean-events partition client: {:?}", e);
            return;
        }
    };

    println!("SUCCESS: Connected to Redpanda.");

    let mut current_offset = raw_partition_client.get_offset(OffsetAt::Earliest).await.unwrap_or(0);
    println!("INFO: Validator is actively listening to 'raw-events' from offset {}...", current_offset);

    loop {
        match raw_partition_client.fetch_records(current_offset, 1..1_000_000, 1_000_000).await {
            Ok((records, _high_watermark)) => {
                for record_and_offset in records {
                    current_offset = record_and_offset.offset + 1;

                    // 1. Extract context from incoming Kafka headers
                    let parent_context = global::get_text_map_propagator(|prop| {
                        prop.extract(&KafkaHeaderExtractor(&record_and_offset.record.headers))
                    });

                    // 2. Start a new span linked to the Go API's trace
                    let mut span = tracer.start_with_context("Rust-Validate-Event", &parent_context);

                    if let Some(value) = &record_and_offset.record.value {
                        let payload = String::from_utf8_lossy(value);

                        match serde_json::from_str::<FraudEvent>(&payload) {
                            Ok(valid_event) => {
                                println!("VALID: Event {} passed inspection. Amount: {}", valid_event.transaction_id, valid_event.Amount);

                                let clean_record = Record {
                                    key: record_and_offset.record.key.clone(),
                                    value: Some(value.clone()),
                                    headers: record_and_offset.record.headers.clone(),
                                    timestamp: record_and_offset.record.timestamp,
                                };

                                if let Err(e) = clean_partition_client.produce(vec![clean_record], Compression::NoCompression).await {
                                    println!("ERROR: Failed to forward event {}: {:?}", valid_event.transaction_id, e);
                                    span.set_status(Status::Error { description: format!("Produce Error: {:?}", e).into() });
                                } else {
                                    span.set_status(Status::Ok);
                                }
                            },
                            Err(e) => {
                                println!("INVALID: Trash data blocked. Reason: {}. Payload: {}", e, payload);
                                span.set_status(Status::Error { description: format!("Validation Error: {}", e).into() });
                            }
                        }
                    }
                    // End the span
                    span.end();
                }
            },
            Err(e) => {
                println!("ERROR: Fetching records failed: {:?}", e);
            }
        }

        tokio::time::sleep(Duration::from_millis(100)).await;
    }
}


// ==========================================
// UNIT TESTS (Validator Schema & Logic)
// ==========================================
#[cfg(test)]
mod tests {
    use super::*;

    // Helper function to generate a flawless base payload
    fn get_valid_json() -> String {
        r#"{
            "transaction_id": "TX-RUST-001",
            "user_id": "usr_999",
            "Time": 406.0, "V1": -2.3, "V2": 1.9, "V3": -1.6, "V4": 3.9,
            "V5": -0.5, "V6": -1.4, "V7": -2.5, "V8": 1.3, "V9": -2.7,
            "V10": -2.7, "V11": 3.2, "V12": -2.8, "V13": -0.5, "V14": -4.2,
            "V15": 0.3, "V16": -1.1, "V17": -2.8, "V18": -0.01, "V19": 0.4,
            "V20": 0.1, "V21": 0.5, "V22": -0.03, "V23": -0.4, "V24": 0.3,
            "V25": 0.04, "V26": 0.1, "V27": 0.2, "V28": -0.1,
            "Amount": 1505.0
        }"#.to_string()
    }

    #[test]
    fn test_valid_payload_passes() {
        let payload = get_valid_json();
        let result = serde_json::from_str::<FraudEvent>(&payload);

        assert!(result.is_ok(), "Valid JSON should parse without errors");

        let event = result.unwrap();
        assert_eq!(event.transaction_id, "TX-RUST-001");
        assert_eq!(event.Amount, 1505.0);
        assert_eq!(event.user_id, Some("usr_999".to_string()));
    }

    #[test]
    fn test_optional_user_id_allowed() {
        // user_id is Option<String>, so removing it should NOT fail the validation
        let payload = get_valid_json().replace(r#""user_id": "usr_999","#, "");
        let result = serde_json::from_str::<FraudEvent>(&payload);

        assert!(result.is_ok(), "Payload missing optional user_id should pass");
        assert_eq!(result.unwrap().user_id, None);
    }

    #[test]
    fn test_missing_required_field_fails() {
        let payload = get_valid_json().replace(r#""Amount""#, r#""MissingAmount""#);
        let result = serde_json::from_str::<FraudEvent>(&payload);

        assert!(result.is_err(), "Payload missing required field MUST fail");
        let err_msg = result.unwrap_err().to_string();
        assert!(err_msg.contains("missing field `Amount`"), "Error should pinpoint missing field. Actual error: {}", err_msg);
    }

    #[test]
    fn test_type_mismatch_fails() {
        // Changing Amount from float (1505.0) to string ("1505.0")
        let payload = get_valid_json().replace(r#""Amount": 1505.0"#, r#""Amount": "1505.0""#);
        let result = serde_json::from_str::<FraudEvent>(&payload);

        assert!(result.is_err(), "Payload with wrong data type MUST fail");
        let err_msg = result.unwrap_err().to_string();
        assert!(err_msg.contains("invalid type"), "Error should pinpoint type mismatch");
    }
}
