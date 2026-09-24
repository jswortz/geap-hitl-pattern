.PHONY: setup test eval deploy-gcp trigger-workflow record-gifs

PROJECT_ID ?= wortz-project-352116
REGION ?= us-central1
WORKFLOW_NAME ?= trend_discovery_flow

setup:
	gpkg setup && uv sync

test:
	PYTHONPATH=. uv run pytest -v

eval:
	PYTHONPATH=. uv run python -m antigravity.evaluate \
		--config evals/eval_config.yaml \
		--dataset evals/test_dataset.jsonl \
		--output evals/results/latest_run.json

deploy-gcp:
	gcloud run deploy data-service \
		--source=. \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--service-account=workflow-runner-sa@$(PROJECT_ID).iam.gserviceaccount.com \
		--allow-unauthenticated \
		--set-env-vars="APP_MODULE=services.data_service.main:app,START_EMBEDDED_POSTGRES=true,ENABLE_FIRESTORE_SYNC=true,PROJECT_ID=$(PROJECT_ID),REGION=$(REGION)"
	gcloud run deploy trend-agent-service \
		--source=. \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--service-account=workflow-runner-sa@$(PROJECT_ID).iam.gserviceaccount.com \
		--allow-unauthenticated \
		--set-env-vars="APP_MODULE=services.trend_agent.main:app,ENABLE_FIRESTORE_SYNC=true,PROJECT_ID=$(PROJECT_ID),REGION=$(REGION)"
	gcloud run deploy approval-ui \
		--source=. \
		--region=$(REGION) \
		--project=$(PROJECT_ID) \
		--service-account=workflow-runner-sa@$(PROJECT_ID).iam.gserviceaccount.com \
		--allow-unauthenticated \
		--set-env-vars="APP_MODULE=services.approval_ui.app:app,START_EMBEDDED_POSTGRES=true,ENABLE_FIRESTORE_SYNC=true,PROJECT_ID=$(PROJECT_ID),REGION=$(REGION)"
	gcloud workflows deploy $(WORKFLOW_NAME) \
		--source=workflows/trend_discovery_flow.yaml \
		--location=$(REGION) \
		--project=$(PROJECT_ID) \
		--service-account=workflow-runner-sa@$(PROJECT_ID).iam.gserviceaccount.com

trigger-workflow:
	gcloud workflows run $(WORKFLOW_NAME) \
		--location=$(REGION) \
		--project=$(PROJECT_ID) \
		--data='{"brand_id": "brand_apex", "category": "fabric_care", "search_query": "cold water eco wash consumer trends 2026"}'

record-gifs:
	PYTHONPATH=. uv run python scripts/record_hitl_gifs.py
