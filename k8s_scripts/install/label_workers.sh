#!/bin/bash

worker_node="$1"

kubectl label node $worker_node node-role.kubernetes.io/worker=worker
