import uuid

from pydantic import BaseModel, ConfigDict, Field


class TransactionRequest(BaseModel):
    transaction_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for idempotency to prevent duplicate transactions.",
    )
    Time: float = Field(
        ...,
        ge=0.0,
        description="Seconds elapsed between this transaction and the first transaction.",
    )
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float = Field(..., ge=0.0, description="Transaction amount. Cannot be negative.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "Time": 0.0,
                "V1": -1.359807,
                "V2": -0.072781,
                "V3": 2.536347,
                "V4": 1.378155,
                "V5": -0.338321,
                "V6": 0.462388,
                "V7": 0.239599,
                "V8": 0.098698,
                "V9": 0.363787,
                "V10": 0.090794,
                "V11": -0.551600,
                "V12": -0.617801,
                "V13": -0.991390,
                "V14": -0.311169,
                "V15": 1.468177,
                "V16": -0.470401,
                "V17": 0.207971,
                "V18": 0.025791,
                "V19": 0.403993,
                "V20": 0.251412,
                "V21": -0.018307,
                "V22": 0.277838,
                "V23": -0.110474,
                "V24": 0.066928,
                "V25": 0.128539,
                "V26": -0.189115,
                "V27": 0.133558,
                "V28": -0.021053,
                "Amount": 149.62,
            }
        }
    )


class TransactionResponse(BaseModel):
    transaction_id: str = Field(..., description="The ID of the processed transaction.")
    is_fraud: bool = Field(..., description="True if the model predicts fraud, False otherwise.")
    fraud_probability: float = Field(..., description="The probability score (0.0 to 1.0) of fraud.")
    processing_time_ms: float = Field(..., description="Time taken to process the request in milliseconds.")
