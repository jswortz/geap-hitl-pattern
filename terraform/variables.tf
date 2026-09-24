variable "project_id" {
  description = "Google Cloud Platform Project ID"
  type        = string
  default     = "wortz-project-352116"
}

variable "region" {
  description = "Google Cloud deployment region"
  type        = string
  default     = "us-central1"
}

variable "alloydb_cluster_id" {
  description = "AlloyDB Cluster ID"
  type        = string
  default     = "brand-hitl-cluster"
}

variable "workflow_name" {
  description = "Google Cloud Workflows state machine name"
  type        = string
  default     = "trend_discovery_flow"
}
