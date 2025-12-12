# Создание провайдера для Yandex Cloud
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  token     = var.yc_token
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
}

# Переменные для проверки, существует ли vpc. Создание контейнеров в ВМ.
locals {
  vpc_id = var.use_existing_vpc ? "id-существующей-vpc" : yandex_vpc_network.ls-vpc[0].id
  
  raw_docker_compose = templatefile("${path.module}/docker-compose.tftpl", {
    ycr_image_path  = var.ycr_image_path
  })

  docker_compose = join("\n", [for line in split("\n", local.raw_docker_compose) : "      ${line}"])

  cloud_init = templatefile("${path.module}/cloud-init.tftpl", {
    ycr_token      = var.ycr_token,
    docker_compose = local.docker_compose
  })
  
  
}

# Создание VPC и подсетей
resource "yandex_vpc_network" "ls-vpc" {
  name  = "ls-network"
  count = var.use_existing_vpc ? 0 : 1
}

resource "yandex_vpc_subnet" "ls-subnet-a" {
  name           = "ls-subnet-a"
  zone           = "ru-central1-a"
  network_id     = local.vpc_id
  v4_cidr_blocks = ["10.0.1.0/24"]
}

resource "yandex_vpc_subnet" "ls-subnet-b" {
  name           = "ls-subnet-b"
  zone           = "ru-central1-b"
  network_id     = local.vpc_id
  v4_cidr_blocks = ["10.0.2.0/24"]
}

resource "yandex_vpc_subnet" "ls-subnet-d" {
  name           = "ls-subnet-d"
  zone           = "ru-central1-d"
  network_id     = local.vpc_id
  v4_cidr_blocks = ["10.0.3.0/24"]
}

# Compute Группы ВМ
data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_compute_instance_group" "lucky-search-group" {
  name               = "lucky-search-group"
  service_account_id = var.sa_id
  folder_id          = var.folder_id

  instance_template {
    platform_id = "standard-v2"

    resources {
      cores  = 4
      memory = 4
    }

    boot_disk {
      initialize_params {
        image_id = data.yandex_compute_image.ubuntu.id
        size     = 33 
        type     = "network-ssd"
      }
    }

    network_interface {
      subnet_ids = [
        yandex_vpc_subnet.ls-subnet-a.id,
        yandex_vpc_subnet.ls-subnet-b.id,
        yandex_vpc_subnet.ls-subnet-d.id,
      ]
      nat = true
    }

    metadata = {
      ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
      user-data = local.cloud_init
    }
  }

  scale_policy {
    auto_scale {
      initial_size           = 1
      measurement_duration   = 60
      cpu_utilization_target = 50
      min_zone_size          = 1
      max_size               = 3
      warmup_duration        = 60
      stabilization_duration = 60
    }
  }

  allocation_policy {
    zones = ["ru-central1-d"]
  }
  deploy_policy {
    max_unavailable = 1
    max_expansion   = 1
    max_creating    = 3
    max_deleting    = 3
  }

}

# Создание ALB балансировщика
resource "yandex_alb_target_group" "alb_target_group" {
  name = "alb-target-group"

  target {
    subnet_id  = yandex_vpc_subnet.ls-subnet-d.id
    ip_address = yandex_compute_instance_group.lucky-search-group.instances[0].network_interface[0].ip_address
  }
}

resource "yandex_alb_backend_group" "bg" {
  name = "market-backend-group"

  http_backend {
    name             = "http-backend"
    target_group_ids = [yandex_alb_target_group.alb_target_group.id]
    port             = 80

    load_balancing_config {
      panic_threshold = 50
    }

    healthcheck {
      timeout  = "1s"
      interval = "2s"

      http_healthcheck {
        path = "/"
      }
    }
  }
}

resource "yandex_alb_http_router" "router" {
  name = "market-router"
}

resource "yandex_alb_virtual_host" "vhost" {
  name           = "market-vhost"
  http_router_id = yandex_alb_http_router.router.id

  route {
    name = "default-route"

    http_route {
      http_route_action {
        backend_group_id = yandex_alb_backend_group.bg.id
      }
    }
  }
}

resource "yandex_alb_load_balancer" "alb" {
  name       = "market-alb"
  network_id = local.vpc_id

  allocation_policy {
    location {
      zone_id   = "ru-central1-d"
      subnet_id = yandex_vpc_subnet.ls-subnet-d.id
    }
  }

  listener {
    name = "https-listener"

    endpoint {
      address {
        external_ipv4_address {
          address = var.ip_address_id
        }
      }
      ports = [443]
    }

    tls {
      default_handler {
        certificate_ids = [var.ssl_id]

        http_handler {
          http_router_id = yandex_alb_http_router.router.id
        }
      }
    }
  }

  depends_on = [
    yandex_alb_backend_group.bg,
    yandex_alb_virtual_host.vhost
  ]
}
