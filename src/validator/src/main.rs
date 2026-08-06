use rskafka::client::ClientBuilder;
use rskafka::client::partition::{Compression, OffsetAt, UnknownTopicHandling};
use serde::Deserialize;
use std::env;
use std::sync::Arc;
use std::time::Duration;
use tokio::task;

#[derive(Debug, Deserialize)]
#[allow(non_snake_case)]
#[allow(dead_code)]
struct FraudEvent<'a> {
    #[serde(borrow)]
    transaction_id: &'a str,
    #[serde(borrow)]
    user_id: Option<&'a str>,
    Time: f64,
    V1: f64,
    V2: f64,
    V3: f64,
    V4: f64,
    V5: f64,
    V6: f64,
    V7: f64,
    V8: f64,
    V9: f64,
    V10: f64,
    V11: f64,
    V12: f64,
    V13: f64,
    V14: f64,
    V15: f64,
    V16: f64,
    V17: f64,
    V18: f64,
    V19: f64,
    V20: f64,
    V21: f64,
    V22: f64,
    V23: f64,
    V24: f64,
    V25: f64,
    V26: f64,
    V27: f64,
    V28: f64,
    Amount: f64,
}

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();
    let is_probe = args
        .iter()
        .any(|arg| arg == "--check-startup" || arg == "--check-live" || arg == "--check-ready");

    let connection_string =
        env::var("REDPANDA_BROKER").unwrap_or_else(|_| "localhost:19092".to_string());

    let client = match ClientBuilder::new(vec![connection_string.to_owned()])
        .build()
        .await
    {
        Ok(c) => c,
        Err(e) => {
            eprintln!("CRITICAL: Failed to build Kafka client: {:?}", e);
            std::process::exit(1);
        }
    };

    let raw_partition_client = client
        .partition_client("raw-events", 0, UnknownTopicHandling::Retry)
        .await
        .unwrap();

    let clean_partition_client = Arc::new(
        client
            .partition_client("clean-events", 0, UnknownTopicHandling::Retry)
            .await
            .unwrap(),
    );

    if is_probe {
        println!("Health check passed successfully.");
        std::process::exit(0);
    }

    let mut current_offset = raw_partition_client
        .get_offset(OffsetAt::Earliest)
        .await
        .unwrap_or(0);

    loop {
        match raw_partition_client
            .fetch_records(current_offset, 1..5_000_000, 5_000_000)
            .await
        {
            Ok((records, _high_watermark)) => {
                if records.is_empty() {
                    tokio::time::sleep(Duration::from_millis(5)).await;
                    continue;
                }

                let mut valid_batch = Vec::with_capacity(records.len());

                for record_and_offset in records.into_iter() {
                    current_offset = record_and_offset.offset + 1;

                    let is_valid = if let Some(value) = &record_and_offset.record.value {
                        match serde_json::from_slice::<FraudEvent>(value) {
                            Ok(_) => true,
                            Err(e) => {
                                let payload_str = String::from_utf8_lossy(value);
                                println!("INVALID: {} - {}", e, payload_str);
                                false
                            }
                        }
                    } else {
                        false
                    };

                    if is_valid {
                        valid_batch.push(record_and_offset.record);
                    }
                }

                if !valid_batch.is_empty() {
                    // 3. EKLENEN KISIM: Arc'ın referans sayacını ucuz bir şekilde artırıyoruz
                    let producer_client = Arc::clone(&clean_partition_client);

                    task::spawn(async move {
                        let _ = producer_client
                            .produce(valid_batch, Compression::NoCompression)
                            .await;
                    });
                }
            }
            Err(_) => {
                tokio::time::sleep(Duration::from_millis(500)).await;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
        }"#
        .to_string()
    }

    #[test]
    fn test_valid_payload_passes() {
        let payload = get_valid_json();
        let result = serde_json::from_str::<FraudEvent>(&payload);
        assert!(result.is_ok());
        let event = result.unwrap();
        assert_eq!(event.transaction_id, "TX-RUST-001");
        assert_eq!(event.Amount, 1505.0);
        assert_eq!(event.user_id, Some("usr_999"));
    }

    #[test]
    fn test_optional_user_id_allowed() {
        let payload = get_valid_json().replace(r#""user_id": "usr_999","#, "");
        let result = serde_json::from_str::<FraudEvent>(&payload);
        assert!(result.is_ok());
        assert_eq!(result.unwrap().user_id, None);
    }

    #[test]
    fn test_missing_required_field_fails() {
        let payload = get_valid_json().replace(r#""Amount""#, r#""MissingAmount""#);
        let result = serde_json::from_str::<FraudEvent>(&payload);
        assert!(result.is_err());
    }

    #[test]
    fn test_type_mismatch_fails() {
        let payload = get_valid_json().replace(r#""Amount": 1505.0"#, r#""Amount": "1505.0""#);
        let result = serde_json::from_str::<FraudEvent>(&payload);
        assert!(result.is_err());
    }
}
