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
