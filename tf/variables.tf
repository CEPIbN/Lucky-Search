variable "ycr_image_path" {
  description = "Путь к образу в Yandex Container Registry"
  type        = string
  default     = "cr.yandex/crpomfcac4js25e32lcu/lucky-search:latest"
}

variable "sa_id" {
  description = "ID сервисного аккаунта"
  type        = string
}

variable "yc_token" {
  description = "Yandex Cloud OAuth token"
  type        = string
  sensitive   = true
}

variable "cloud_id" {
  description = "Yandex Cloud ID"
  type        = string
}

variable "folder_id" {
  description = "Yandex Cloud Folder ID"
  type        = string
}

variable "use_existing_vpc" {
  description = "Whether to use existing VPC"
  type        = bool
  default     = false
}

variable "existing_vpc_id" {
  description = "ID существующей VPC при use_existing_vpc = true"
  type        = string
  default     = ""
}

variable "ip_address_id" {  
  description = "Static IP address ID"
  type        = string
}

variable "ssl_id" {
  description = "SSL certificate ID"
  type        = string
}

variable "ycr_token" {}
