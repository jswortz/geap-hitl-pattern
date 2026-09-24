resource "google_service_account" "workflow_runner_sa" {
  account_id   = "workflow-runner-sa"
  display_name = "Brand Building HITL Approval Example Workflow Runner Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "workflow_runner_roles" {
  for_each = toset([
    "roles/run.invoker",
    "roles/workflows.invoker",
    "roles/aiplatform.user",
    "roles/alloydb.client",
    "roles/datastore.user",
    "roles/logging.logWriter",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.workflow_runner_sa.email}"
}
