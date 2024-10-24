#!/bin/bash

echo "Run with sudo"

ip link set cni0 down && ip link set flannel.1 down 
ip link delete cni0 && ip link delete flannel.1
systemctl restart containerd && systemctl restart kubelet


