# AlloyDB Agentic Database Architecture (PRD Section 11.5)
resource "google_alloydb_cluster" "default" {
  cluster_id = var.alloydb_cluster_id
  location   = var.region
  project    = var.project_id

  network_config {
    network = "projects/${var.project_id}/global/networks/default"
  }
}

# Primary Transactional Instance (For Workflows and System of Record Writes)
resource "google_alloydb_instance" "primary_instance" {
  cluster       = google_alloydb_cluster.default.name
  instance_id   = "primary-instance"
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 4
  }
}

# Ephemeral Agent Instance Pool (For Autonomous Agent Reasoning Reads - Tenets 1, 2, 3)
resource "google_alloydb_instance" "agent_pool_instance" {
  cluster       = google_alloydb_cluster.default.name
  instance_id   = "agent-read-pool"
  instance_type = "READ_POOL"

  read_pool_config {
    node_count = 1 # Scales dynamically from 0 to thousands under agent burst load
  }

  machine_config {
    cpu_count = 8
  }

  database_flags = {
    "alloydb.enable_pgaudit"                   = "on"
    "google_ml_integration.enable_model_armor" = "on"
    "alloydb_ai.enable_ai_functions"           = "on"
  }

  depends_on = [google_alloydb_instance.primary_instance]
}
