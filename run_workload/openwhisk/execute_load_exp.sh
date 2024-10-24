#!/bin/bash

action_name="$1"
action_path="$2"
action_data="$3"
action_runtime="$4"
ow_path="/home/amonum/openwhisk-deploy-kube"
experiment_path="/home/amonum/run-serverless-workload/"
arrival_rates=(0.1 0.5 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120 125 130 135 140 145 150 155 160 165 170)

for rate in ${arrival_rates[@]}; do
    # Tear down current openwhisk
    helm uninstall owdev -n openwhisk
    echo "Sleeping until openwhisk tears down (10 mins)"
    sleep 400
    # Setup openwhisk
    cd $ow_path
    helm install owdev ./helm/openwhisk -n openwhisk --create-namespace -f mycluster.yaml
    # wait for openwhisk to boot up
    echo "Sleeping until openwhisk boots up (10 mins)"
    sleep 600
    cd $experiment_path
    # create ow action
    #wsk -i action create $action_name $action_path --kind python:3.11
    wsk -i action create $action_name $action_path --kind $action_runtime
    # create dir and log files
    mkdir "${action_name}_${rate}"
    activation_log_path="${action_name}_${rate}/activation.log"
    timestamp_log_path="${action_name}_${rate}/timestamp.log"
    invoker_log_path="${action_name}_${rate}/invoker.log"
    controller_log_path="${action_name}_${rate}/controller.log"
    touch $activation_log_path
    touch $pods_log_path
    touch $timestamp_log_path
    touch $invoker_log_path
    touch $controller_log_path
    controller_pod="owdev-controller-0"
    echo "Starting experiment for arrival rate ${rate}"
    python3 run_workload.py $timestamp_log_path $pods_log_path $responses_log_path $action_data $rate $action_name
    kubectl logs $controller_pod -n openwhisk > $controller_log_path
    kubectl logs owdev-invoker-0 -n openwhisk > $invoker_log_path
done

echo "All measurements completed"
