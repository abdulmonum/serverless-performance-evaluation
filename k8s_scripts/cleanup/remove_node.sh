#!/bin/bash

worker_node="$1"

kubectl drain $worker_node --ignore-daemonsets
kubectl delete node $worker_node
