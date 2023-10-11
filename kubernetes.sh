#!/bin/bash

# Install prerequisites
sudo apt-get update
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

# Add Docker's GPG key
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker's APT repository
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify Docker installation
sudo docker run hello-world

# Install Kubernetes Now
# Add Kubernetes Signing Key
sudo apt update && sudo apt install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubeadm kubelet kubectl
#
sudo apt-mark hold kubeadm kubelet kubectl
kubeadm version
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
sudo echo -e "overlay\nbr_netfilter" > /etc/modules-load.d/containerd.conf
sudo modprobe overlay && sudo modprobe br_netfilter
sudo echo -e "net.bridge.bridge-nf-call-ip6tables = 1\nnet.bridge.bridge-nf-call-iptables = 1\nnet.ipv4.ip_forward = 1" > /etc/sysctl.d/kubernetes.conf
sudo sysctl --system
sudo hostnamectl set-hostname master-node
sudo echo -e 'KUBELET_EXTRA_ARGS="--cgroup-driver=cgroupfs"' > /etc/default/kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo echo -e '{\n\t"exec-opts":\n\t ["native.cgroupdriver=systemd"],\n\t"log-driver": "json-file",\n\t"log-opts": {"max-size": "100m"\n},\n\t"storage-driver": "overlay2"\n\t}' > /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo echo -e 'Environment="KUBELET_EXTRA_ARGS=--fail-swap-on=false"' > /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
sudo systemctl daemon-reload
sudo systemctl restart kubelet
sudo kubeadm init --control-plane-endpoint=master-node --upload-certs
mkdir -p $HOME/.kube && sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && sudo chown $(id -u):$(id -g) $HOME/.kube/config
