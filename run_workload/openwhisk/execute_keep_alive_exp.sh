#!/bin/bash

action_name="$1"
action_path="$2"
action_data="$3"
action_runtime="$4"
ow_path="/home/amonum/openwhisk-deploy-kube"
config_file_path="/home/amonum/openwhisk-deploy-kube/helm/openwhisk/templates/invoker-pod.yaml"
experiment_path="/home/amonum/run-serverless-workload/"
ka_line_number_1=194
ka_line_number_2=196
keep_alives=(1 3 5 7 10 12 14 16 18 20 22 24 26 28 30 35 40 45 50 55 60 75 90 120 150)

for keep_alive in ${keep_alives[@]}; do
    # Tear down current openwhisk
    helm uninstall owdev -n openwhisk
    echo "Sleeping until openwhisk tears down (5 mins)"
    sleep 300
    # change keep alive parameter in ow-deploy-kube dir
    sed -i "${ka_line_number_1}s/\(value: \).*/\1\"${keep_alive}s\"/" $config_file_path
    sed -i "${ka_line_number_2}s/\(value: \).*/\1\"${keep_alive}s\"/" $config_file_path
    # Setup openwhisk
    cd $ow_path
    helm install owdev ./helm/openwhisk -n openwhisk --create-namespace -f mycluster.yaml
    # wait for openwhisk to boot up
    echo "Sleeping until openwhisk boots up (10 mins)"
    sleep 600
    cd $experiment_path
    # create ow action
    wsk -i action create $action_name $action_path --kind $action_runtime
    # create dir and log files
    mkdir "${action_name}_${keep_alive}"
    activation_log_path="${action_name}_${keep_alive}/activation.log"
    timestamp_log_path="${action_name}_${keep_alive}/timestamp.log"
    invoker_log_path="${action_name}_${keep_alive}/invoker.log"
    controller_log_path="${action_name}_${keep_alive}/controller.log"
    touch $activation_log_path
    touch $pods_log_path
    touch $timestamp_log_path
    touch $invoker_log_path
    touch $controller_log_path
    # run experiment
    echo "Starting experiment for keep alive ${keep_alive}"
    python3 run_workload.py $timestamp_log_path $pods_log_path $activation_log_path $action_data $action_name
    kubectl logs owdev-controller-0 -n openwhisk > $controller_log_path
    kubectl logs owdev-invoker-0 -n openwhisk > $invoker_log_path
done

echo "All measurements completed"