#!/bin/bash

sudo kubeadm reset
rm -rf $HOME/.kube/config
sudo rm -rf /etc/cni/net.d
sudo ipvsadm --clear
