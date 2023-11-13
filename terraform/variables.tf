variable "project" {
  type        = string
  description = "Id del proyecto en GCP"
}

variable "region" {
  type        = string
  description = "Región de GCP donde se crearan los recursos"
  default     = "us-east1"
}

variable "zone" {
  type        = string
  description = "Zona de GCP donde se crearan los recursos"
  default     = "us-east1-c"
}

variable "db_instance_pg15_password" {
  type        = string
  description = "Contraseña del usuario de la instancia SQL"
  sensitive   = true
}