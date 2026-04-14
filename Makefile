.PHONY: fetch preprocess train export pipeline clean


#################################################################
# DATA SCIENCE
#################################################################
fetch:
	python experiments/00_fetch_data.py

preprocess: fetch
	python experiments/01_eda_and_preprocessing.py

train: preprocess
	python experiments/02_model_training.py

export:
	python experiments/03_train_and_export.py

pipeline: fetch preprocess train export
	@echo "==========================================================="
	@echo "SUCCESS: Full Machine Learning Pipeline Completed!"
	@echo "==========================================================="

clean:
	rm -f data/raw/creditcard.csv
	rm -f data/processed/creditcard_scaled.csv
	rm -f models/*.joblib
	rm -f models/*.onnx
	@echo "All generated data and models have been cleaned."
