import asyncio
import time
import random
import subprocess
import threading
import sys
import requests
import numpy as np
from aiohttp import ClientSession, BasicAuth, TCPConnector
import json
import scipy.stats as stats

def generate_poisson_events(rate, time_duration, rng):
    interarrival_times = rng.exponential(scale=1/rate, size=int(rate * time_duration))
    scale_factor = time_duration / np.sum(interarrival_times)
    scaled_interarrival_times = interarrival_times * scale_factor
    return scaled_interarrival_times


# Function to make asynchronous API calls
async def make_async_api_call(session, api_endpoint, json_data):
    async with session.post(api_endpoint, json=json_data, ssl=False) as response:
        resp = await response.text()
        try:
            resp["response"]["result"] = ""
        except:
            pass
        return resp



async def create_containers(api_endpoint, auth, json_data, num):
    headers = {"Content-Type": "application/json"}
    async with ClientSession(headers=headers, auth=BasicAuth(auth[0], auth[1])) as session:
        print("creating tasks")
        tasks = [asyncio.create_task(make_async_api_call(session, api_endpoint, json_data)) for _ in range(num)]
        print("tasks created")
        print("Going to sleep")
        await asyncio.sleep(40)

async def run_workload(inter_arrival_times, api_endpoint, auth, json_data):
    tasks = []
    headers = {"Content-Type": "application/json"}
    connector = TCPConnector(limit=10000)
    start_time = time.time()
    async with ClientSession(headers=headers, auth=BasicAuth(auth[0], auth[1]), connector=connector) as session:
        clock = time.time()
        for iat in inter_arrival_times:
            clock += iat
            tasks.append(asyncio.ensure_future(make_async_api_call(session, api_endpoint, json_data)))
            wait = clock - time.time()
            if wait > 0:
                await asyncio.sleep(wait) 
        end_time = time.time()
        print("Workload invoked, waiting on all responses")
        responses = await asyncio.gather(*tasks)
    return start_time, end_time, responses





if __name__ == "__main__":

    '''USAGE: python3 run_workload.py <timestamp_log> <pod_log> <activation_log>'''
    # Define parameters
    OW_HOST = "https://192.168.173.212:31001"
    timestamp_log = sys.argv[1]
    pod_log = sys.argv[2]
    activation_log = sys.argv[3]
    input_json_path = sys.argv[4]
    arrival_rate = sys.argv[5]
    function_name = sys.argv[6]
    auth = ("23bc46b1-71f6-4ed5-8c54-816aa4f8c502", "123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP") 
    rate_per_second = float(arrival_rate)  # Adjust as needed
    duration_before_measurement = 5 * 60  # 5 minutes (warm-up time)
    duration_measurement = 10 * 60 # 10 minutes (measurement time)
    rng = np.random.default_rng(204)
    
    api_endpoint = f"{OW_HOST}/api/v1/namespaces/guest/actions/{function_name}?blocking=true"
    with open(input_json_path, 'r') as file:
        input_json = file.read().replace('\n', '')
    json_data = json.loads(input_json)

    inter_arrival_times_warm = generate_poisson_events(rate_per_second, duration_before_measurement, rng)
    inter_arrival_times_test = generate_poisson_events(rate_per_second, duration_measurement, rng)


    print("Warm-up period: Running workload for the first duration minutes...")
    print("Starting measurement...")
    start_measurement_time = time.time()
    start_time, end_time, activations = asyncio.run(run_workload(inter_arrival_times_test, api_endpoint, auth, json_data))
    end_measurement_time = time.time()
    print("End of measurement.")
    print("Starting Timestamp:", start_time)
    print("Ending Timestamp:", end_time)
    print("Invocation count: ", len(inter_arrival_times_test))
    with open(timestamp_log, "a") as f:
        f.write(f"Experiment_Start: {start_time}\n")
        f.write(f"Experiment_End: {end_time}\n")
        f.write(f"Invocation_Count: {len(inter_arrival_times_test)}\n")

    with open(activation_log, "a") as f:
        for activation in activations:
            f.write(f"{activation}\n")
