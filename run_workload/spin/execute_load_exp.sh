#!/bin/bash

action_name=$1
arrival_rates=(0.5 1 2 3 3.5 4 4.5 5 6 7 8 9)

for rate in ${arrival_rates[@]}; do
    echo "Going to sleep" 
    sleep 60
    echo "Starting experiment for arrival rate ${rate}"
    python3 run_wasm_workload.py $action_name $rate
done

echo "All measurements completed"



