import asyncio
import time
import random
import subprocess
import threading
import sys
import os
import numpy as np
from aiohttp import ClientSession, BasicAuth, TCPConnector
from statistics import mean, stdev
import json

def generate_poisson_events(rate, time_duration, rng):
    interarrival_times = rng.exponential(scale=1/rate, size=int(rate * time_duration))
    scale_factor = time_duration / np.sum(interarrival_times)
    scaled_interarrival_times = interarrival_times * scale_factor
    return scaled_interarrival_times

#Flag to indicate end of experiment
measurement_ended = threading.Event()
in_flight_counts = []


async def make_async_api_call(session, api_endpoint):
    s_time = time.time()
    async with session.get(api_endpoint) as response:
        response_data =  await response.text()
        response_time = time.time() - s_time
        return response_data, response_time

async def make_async_api_post_call(session, api_endpoint, json_data):
    s_time = time.time()
    async with session.post(api_endpoint, json=json_data) as response:
        response_data =  await response.text()
        response_time = time.time() - s_time
        return response_data, response_time


async def periodic(interval):
    while True:
        await asyncio.sleep(interval)
        inflight_tasks = [task for task in asyncio.all_tasks() if not task.done()]
        in_flight_counts.append(len(inflight_tasks))




async def run_workload(inter_arrival_times, api_endpoint, interval):
    tasks = []
    start_time = time.time()
    measurement_task = asyncio.create_task(periodic(interval))
    async with ClientSession() as session:
        clock = time.time()
        for iat in inter_arrival_times:
            clock += iat
            tasks.append(asyncio.ensure_future(make_async_api_call(session, api_endpoint)))            
            wait = clock - time.time()
            if wait > 0:
                await asyncio.sleep(wait)
        end_time = time.time()
        measurement_task.cancel()
        responses = await asyncio.gather(*tasks)
    return start_time, end_time, responses

async def run_post_workload(inter_arrival_times, api_endpoint, interval, json_data):
    tasks = []
    start_time = time.time()
    measurement_task = asyncio.create_task(periodic(interval))
    async with ClientSession() as session:
        clock = time.time()
        for iat in inter_arrival_times:
            clock += iat
            tasks.append(asyncio.ensure_future(make_async_api_post_call(session, api_endpoint, json_data)))            
            wait = clock - time.time()
            if wait > 0:
                await asyncio.sleep(wait)
        end_time = time.time()
        measurement_task.cancel()
        responses = await asyncio.gather(*tasks)
    return start_time, end_time, responses




        

if __name__ == "__main__":

    '''USAGE: python3 run_workload.py <timestamp_log> <responses_log>'''
    # Define parameters
    duration_measurement = 10 * 60  # 10 minutes (measurement time)
    function_name = sys.argv[1]
    in_flight_check = 1
    rate_per_second = float(sys.argv[2])
    function_inputs = {"float": "", "whatlang": "?text=The+quick+brown+fox+jumps+over+the+lazy+dog",
                        "matmul": "?dimensions=50", "aes": "?length=20&iterations=2500", 
                        "chameleon": "?num_of_rows=500&num_of_cols=10", "image-thumbnail": ""}
    api_endpoint = f"http://127.0.0.1:3000/{function_name}{function_inputs[function_name]}"
    
    if function_name == "image-thumbnail":
        with open(input_json_path, 'r') as file:
            input_json = file.read().replace('\n', '')
        json_data = json.loads(input_json)
    rng = np.random.default_rng(204)
    inter_arrival_times = generate_poisson_events(rate_per_second, duration_measurement, rng)
    # Start measuring the experiment
    print("Starting measurement...")
    start_measurement_time = time.time()
    loop = asyncio.get_event_loop()
    if function_name == "image-thumbnail":
        start_time, end_time, responses  = loop.run_until_complete(run_post_workload(inter_arrival_times, api_endpoint, in_flight_check, json_data))
    start_time, end_time, responses  = loop.run_until_complete(run_workload(inter_arrival_times, api_endpoint, in_flight_check))   
    end_measurement_time = time.time()
    measurement_ended.set()
    print("End of measurement.")
    print("Starting Timestamp:", start_time)
    print("Ending Timestamp:", end_time)
    print("Invocation count: ",len(inter_arrival_times) )
    exp_inflight_counts = mean(in_flight_counts) - 2 #subtract 2 to remove the measurement coroutines
    print("Avg inflight counts: ", exp_inflight_counts)
    print("inflight counts", len(in_flight_counts))
    
    response_times = [float(resp[1]) for resp in responses]
    print("Avg response time", mean(response_times))
    print("Response std dev", stdev(response_times))

    if not os.path.exists(function_name):
        os.makedirs(function_name)
    
    results_log = os.path.join(function_name, f"{rate_per_second}_results.json")
    result_str = json.dumps({"spin_response_time": mean(response_times),
                  "executors": exp_inflight_counts})
    
    with open(results_log, "a") as f:
        f.write(result_str)
    