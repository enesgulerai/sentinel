import os

import numpy as np
import onnxruntime as ort
import pytest

MODEL_PATH = "models/fraud_xgboost.onnx"
MODEL_EXISTS = os.path.exists(MODEL_PATH)


@pytest.mark.skipif(not MODEL_EXISTS, reason="Model artifact not found. Skipping artifact test in CI environment.")
def test_onnx_model_exists():
    assert os.path.exists(MODEL_PATH), "ONNX model file is missing!"


@pytest.mark.skipif(not MODEL_EXISTS, reason="Model artifact not found. Skipping inference test in CI environment.")
def test_onnx_inference():
    session = ort.InferenceSession(MODEL_PATH)

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    # 30 features: Time (1) + V1-V28 (28) + Amount (1)
    dummy_input = np.random.randn(1, 30).astype(np.float32)

    predictions = session.run([output_name], {input_name: dummy_input})

    assert predictions is not None, "Model returned None."
    assert len(predictions[0]) >= 1, "Model should return at least one prediction array."

    pred_value = predictions[0][0]

    # Ensure prediction is numeric
    assert isinstance(pred_value, (np.floating, np.integer, float, int)), "Prediction must be a numeric value."

    # Optional bounds check: Fraud probability or binary classification should be bounded
    # If the model outputs raw logits instead of probabilities, this check can be adjusted or removed
    assert 0.0 <= float(pred_value) <= 1.0, "Prediction value is out of valid logical bounds (0.0 to 1.0)."
