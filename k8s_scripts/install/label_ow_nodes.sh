#!/bin/bash

worker_node_1="$1"
worker_node_2="$2"

kubectl label node $worker_node_1 openwhisk-role=core
kubectl label node $worker_node_2 openwhisk-role=invoker