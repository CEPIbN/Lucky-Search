variable "ycr_token" {
  description = "OAuth-токен для доступа к Yandex Container Registry"
  type        = string
}

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
  description = "Yandex Cloud IAM token"
  type        = string
  sensitive   = true
}

variable "cloud_id" {
  description = "ID Облака"
  type        = string
}

variable "folder_id" {
  description = "ID Каталога"
  type        = string
}

variable "use_existing_vpc" {
  description = "Существует ли VPC сеть"
  type        = bool
  default     = false
}

variable "existing_vpc_id" {
  description = "ID существующей VPC при use_existing_vpc = true"
  type        = string
  default     = ""
}

variable "ip_address_id" {  
  description = "Статический IP-адрес, для ALB"
  type        = string
}

variable "ssl_id" {
  description = "ID SSL-сертификата"
  type        = string
}
