variable "vpc_range" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnets" {
  type    = list(any)
  default = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_subnet_cidr_blocks" {
  type = list(any)
  default = ["10.0.2.0/24", "10.0.3.0/24"]
}

variable "availability_zones" {
  default     = ["us-east-1a", "us-east-1b"]
  type        = list(any)
  description = "List of availability zones"
}

variable "routetable" {
  default = "Public"
}

variable "amiid" {
  default = "ami-05fa00d4c63e32376"
}

variable "instancefamily" {
  default = "t2.large"
}

variable "instancekeypair" {
  default = "jenkins"
}


variable "tags" {
  default = {}
}
