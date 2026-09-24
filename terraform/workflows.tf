resource "google_workflows_workflow" "trend_discovery_flow" {
  name            = var.workflow_name
  region          = var.region
  project         = var.project_id
  description     = "Durable Macro Orchestrator with Zero-Compute HTTP Callback Approval Gate"
  service_account = google_service_account.workflow_runner_sa.id
  source_contents = file("${path.module}/../workflows/trend_discovery_flow.yaml")

  user_env_vars = {
    AGENT_RUNNER_URL = google_cloud_run_v2_service.trend_agent_service.uri
    DATA_SERVICE_URL = google_cloud_run_v2_service.data_service.uri
  }
}
