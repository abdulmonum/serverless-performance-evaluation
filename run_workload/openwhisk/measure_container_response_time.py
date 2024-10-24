import requests
import json
import time
import argparse
from urllib3.exceptions import InsecureRequestWarning
import os
# Suppress the warnings from urllib3
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Replace with your OpenWhisk API host, namespace, and AUTH
OW_HOST = 'https://192.168.173.212:31001'
OW_NAMESPACE = 'guest'
OW_AUTH = ("23bc46b1-71f6-4ed5-8c54-816aa4f8c502", "123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP")

def invoke_action(host, namespace, auth, action, params):
    url = f"{host}/api/v1/namespaces/{namespace}/actions/{action}?blocking=true"
    #https://192.168.173.212:31001/api/v1/namespaces/guest/actions/aes

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, auth=auth, verify=False, headers=headers, data=json.dumps(params))
    return response.json()


def calculate_average_response_time(host, namespace, auth, action, num_invocations, params, sleep_time, latency_type):
    total_time = 0

    ##Make containers before so that measurement's first invocation is a warm start
    if latency_type == "warm":
        for i in range(2):
            _ = invoke_action(host, namespace, auth, action, params)
            time.sleep(sleep_time)

    for _ in range(num_invocations):
        result = invoke_action(host, namespace, auth, action, params)
        time.sleep(sleep_time)
        duration = int(result['duration'])/1000
        wait_time = int(result['annotations'][1]['value'])/1000
        response_time = duration + wait_time
        total_time += response_time


    average_response_time = total_time / num_invocations
    return average_response_time

def append_response_time_to_file(average_response_time, file_path, latency_type):
    new_entry = {f"{latency_type}_response_time": average_response_time}
    data = {}

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print("Error: File is not valid JSON. Overwriting the file.")
    
    data = data.update(new_entry)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

    #print("Appended data:", data)


def main():
    parser = argparse.ArgumentParser(description='Invoke OpenWhisk action multiple times and calculate average response time.')
    parser.add_argument('action_name', type=str, help='Name of the action')
    parser.add_argument('param_file', type=str, help='Path to the JSON file containing action parameters')
    parser.add_argument('num_invocations', type=int, help='Number of times to invoke the action')
    parser.add_argument('sleep_time', type=float, help='Time to sleep between invocations in seconds')
    parser.add_argument('latency_type', type=str, help='Type of latency measuring (warm or cold)')


    args = parser.parse_args()

    

    with open(args.param_file, 'r') as file:
        params = json.load(file)

    avg_response_time = calculate_average_response_time(OW_HOST, OW_NAMESPACE, OW_AUTH, args.action_name, args.num_invocations, params, args.sleep_time, args.latency_type)
    print(f"Average response time for {args.num_invocations} invocations: {avg_response_time} s")
    file_path = f"{args.action_name}_container_model_response_time.json"
    append_response_time_to_file(avg_response_time, file_path, args.latency_type)


if __name__ == "__main__":
    main()
