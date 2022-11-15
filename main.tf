resource "aws_vpc" "vpc" {
  cidr_block       = var.vpc_range
  instance_tenancy = "default"
}

resource "aws_subnet" "subnet" {
  count      = length(var.subnets)
  vpc_id     = aws_vpc.vpc.id
  cidr_block = var.subnets[count.index]
}

resource "aws_subnet" "private_subnet" {
  count = length(var.private_subnet_cidr_blocks)

    vpc_id     = aws_vpc.vpc.id
  cidr_block        = var.private_subnet_cidr_blocks[count.index]
  availability_zone = var.availability_zones[count.index]
   tags = try(var.tags, null)
  )
}

resource "aws_route_table" "routetable-public" {
  count  = var.routetable == "Public" ? 1 : 0
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}



resource "aws_route_table" "routetable-private" {
  count  = var.routetable == "Private" ? 1 : 0
  vpc_id = aws_vpc.vpc.id
  route {
    cidr_block     = var.vpc_range
    nat_gateway_id = aws_internet_gateway.igw.id
  }

}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_network_interface" "networkinterface" {
  subnet_id       = aws_subnet.subnet[0].id
  security_groups = [aws_security_group.securitygroup.id]
}

resource "aws_instance" "ec2" {
  ami           = var.amiid
  instance_type = var.instancefamily
  key_name      = var.instancekeypair

  network_interface {
    network_interface_id = aws_network_interface.networkinterface.id
    device_index         = 0
  }
}


resource "aws_security_group" "securitygroup" {
  name        = "Allow HTTP"
  description = "Allow TLS inbound traffic"
  vpc_id      = aws_vpc.vpc.id

  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.vpc.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.vpc.cidr_block]
  }
}

resource "aws_nat_gateway" "default" {
  depends_on = aws_internet_gateway.igw

  count = length(var.subnet)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = try(var.tags, null)
  )
}
