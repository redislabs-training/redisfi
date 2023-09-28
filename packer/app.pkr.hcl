
variable "gcp_credentials_file" {
  type    = string
}
variable "gcp_project" {
  type    = string
}
variable "auth_github" {
  type    = string
}
variable "ssh_user" {
  type    = string
  default = "packer"
}
variable "base_image" {
  type    = string
  default = "ubuntu-2004-focal-v20220419"
}

variable "disk_size" {
  type    = string
  default = "100"
}

variable "image_family_name" {
  type    = string
  default = "redisfi"
}

variable "machine_type" {
  type    = string
  default = "n1-standard-4"
}

variable "packer_source" {
  type    = string
  default = "packer"
}

locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

locals {
  image_name = "redisfi-packer-${local.timestamp}"
}

source "googlecompute" "vm" {
  account_file = "${var.gcp_credentials_file}"
  disk_size    = "${var.disk_size}"
  disk_type    = "pd-ssd"
  image_family = "${var.image_family_name}"
  image_name   = "${local.image_name}"
  machine_type = "${var.machine_type}"
  metadata = {
    enable-oslogin = "false"
  }
  network      = "packer"
  project_id   = "${var.gcp_project}"
  source_image = "${var.base_image}"
  ssh_username = "${var.ssh_user}"
  subnetwork   = "packer-subnet"
  zone         = "us-west3-a"
}

build {
  sources = ["source.googlecompute.vm"]

  provisioner "shell" {
    execute_command = "sudo -s bash -c '{{ .Vars }} {{ .Path }}'"
    inline          = [
      "cp -R redisfi /opt/", 
      "cd /opt", 
      "apt-get update && apt-get install -y docker.io python3-pip", 
      "curl -SL https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose", 
      "chmod +x /usr/local/bin/docker-compose", 
      "pip3 install poetry", 
      "mkdir redisfi-vss", 
      "cd redisfi", 
      "poetry install --no-dev"]
  }

}
