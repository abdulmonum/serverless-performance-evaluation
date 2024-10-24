import time
import requests
import argparse
import json

def measure_average_response_time(api_url, num_runs=10 ):
    # Initialize a list to store response times
    response_times = []

    # Perform the API calls
    for _ in range(num_runs):
        start_time = time.perf_counter()
        response = requests.get(api_url)
        end_time = time.perf_counter()

        # Calculate the response time and add it to the list
        response_time = end_time - start_time
        response_times.append(response_time)

        # Optional: Print the status code to ensure the request was successful
        print(f"Status Code: {response.status_code}, Response Time: {response_time:.4f} seconds")
        time.sleep(1)

    # Calculate the average response time
    average_response_time = sum(response_times) / num_runs
    print(f"\nAverage Response Time: {average_response_time:.4f} seconds")

def measure_average_response_time_post(api_url, json_data, num_runs=10):
    # Initialize a list to store response times
    response_times = []

    # Perform the API calls
    for _ in range(num_runs):
        start_time = time.perf_counter()
        response = requests.get(api_url, json=json_data)
        end_time = time.perf_counter()

        # Calculate the response time and add it to the list
        response_time = end_time - start_time
        response_times.append(response_time)

        # Optional: Print the status code to ensure the request was successful
        print(f"Status Code: {response.status_code}, Response Time: {response_time:.4f} seconds")
        time.sleep(1)

    # Calculate the average response time
    average_response_time = sum(response_times) / num_runs
    print(f"\nAverage Response Time: {average_response_time:.4f} seconds")
    json_data['model_response_time'] = average_response_time
    return json_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure the average response time of an API.")
    parser.add_argument("api_url", type=str, help="The URL of the API endpoint.")
    parser.add_argument("json_file_path", type=str, help="JSON Input.")
    parser.add_argument("function_name", type=str, help="Function name")
    parser.add_argument("--runs", type=int, default=10, help="The number of runs to perform (default: 10).")

    
    args = parser.parse_args()
    with open(args.json_file_path, 'r') as file:
        input_json = file.read().replace('\n', '')
    json_data = json.loads(input_json)
    if args.function_name == "image-thumbnail":
        json_out = measure_average_response_time_post(args.api_url, json_data, args.runs)
    
    json_out = measure_average_response_time(args.api_url, json_data, args.runs)

    with open(args.json_file_path, 'r') as file:
        f.write(json.dumps(json_out))