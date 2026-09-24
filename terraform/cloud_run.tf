resource "google_cloud_run_v2_service" "trend_agent_service" {
  name     = "trend-agent-service"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.workflow_runner_sa.email
    containers {
      image = "gcr.io/${var.project_id}/trend-agent-service:latest"
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
    }
  }
}

resource "google_cloud_run_v2_service" "data_service" {
  name     = "data-service"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.workflow_runner_sa.email
    containers {
      image = "gcr.io/${var.project_id}/data-service:latest"
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "ALLOYDB_DATABASE"
        value = "brand_hitl_db"
      }
    }
  }
}

resource "google_cloud_run_v2_service" "approval_ui" {
  name     = "approval-ui"
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.workflow_runner_sa.email
    containers {
      image = "gcr.io/${var.project_id}/approval-ui:latest"
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "DATA_SERVICE_URL"
        value = google_cloud_run_v2_service.data_service.uri
      }
    }
  }
}
