terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.5.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_sql_database_instance" "db_instance_pg15" {
  name             = "instancia-db"
  database_version = "POSTGRES_15"

  deletion_protection = false

  settings {
    tier    = "db-custom-1-3840"
    edition = "ENTERPRISE"
  }
}

resource "google_sql_user" "db_usuario" {
  name     = "db_usuario"
  instance = google_sql_database_instance.db_instance_pg15.name
  password = var.db_instance_pg15_password
}

resource "google_sql_database" "db_conversor" {
  name     = "conversor"
  instance = google_sql_database_instance.db_instance_pg15.name
}

resource "google_storage_bucket" "bucket_videos" {
  name                        = "misw4204-202315-grupo21"
  location                    = "US-EAST1"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}