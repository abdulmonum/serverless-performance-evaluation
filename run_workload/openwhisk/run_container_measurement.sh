#!/bin/bash

#functions=("aes" "float" "whatlang" "matmul" "image-thumbnail" "chameleon")
functions = ("aes")
for func in "${functions[@]}"; do
    python3 measure_container_response_time.py "$func" ../thesis-functions/openwhisk/${func}/input.json 10 250 cold
    echo "${func} cold response time done"
done

sleep 250

for func in "${functions[@]}"; do
    python3 measure_container_response_time.py "$func" ../thesis-functions/openwhisk/${func}/input.json 10 2 warm
    echo "${func} warm response time done"
done
