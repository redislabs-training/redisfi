
variable "base_image" {
  type    = string
  default = "ubuntu-1804-bionic-v20210825"
}

variable "disk_size" {
  type    = string
  default = "20"
}

variable "image_family_name" {
  type    = string
  default = "redisfi-cluster"
}

variable "machine_type" {
  type    = string
  default = "n1-standard-4"
}

variable "packer_source" {
  type    = string
  default = "packer"
}

variable "rs_os_download_file_end" {
  type    = string
  default = "bionic-amd64"
}

variable "rs_release" {
  type    = string
  default = "64"
}

variable "rs_s3_path" {
  type    = string
  default = "redis-enterprise-software-downloads"
}

variable "rs_version" {
  type    = string
  default = "7.2.4"
}

variable "ssh_user" {
  type    = string
  default = "packer"
}


locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

locals {
  image_name = "redisfi-cluster-packer-${local.timestamp}"
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
    environment_vars = ["RS_TMP_DIR=/tmp/rs-download", "RS_DOWNLOAD_BASE_URL=https://s3.amazonaws.com/${var.rs_s3_path}/${var.rs_version}/", "RS_DOWNLOAD_TAR=redislabs-${var.rs_version}-${var.rs_release}-${var.rs_os_download_file_end}.tar"]
    execute_command  = "sudo -s bash -c '{{ .Vars }} {{ .Path }}'"
    inline           = ["apt-get update && apt-get install -y curl", "echo 'DNSStubListener=no' >> /etc/systemd/resolved.conf", "mv /etc/resolv.conf /etc/resolv.conf.orig", "ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf", "service systemd-resolved restart", "mkdir $RS_TMP_DIR && cd $RS_TMP_DIR", "wget -c $${RS_DOWNLOAD_BASE_URL}$${RS_DOWNLOAD_TAR} && tar xvf $RS_DOWNLOAD_TAR", "./install.sh -y ", "timeout 300 bash -c 'until $(curl --output /dev/null --silent --head --fail -k https://localhost:9443/v1/bootstrap); do printf \".\" && sleep 3; done'"]
  }

}
