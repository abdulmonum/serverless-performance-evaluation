import requests
import json
import sys

# OpenWhisk configuration details
auth = ("23bc46b1-71f6-4ed5-8c54-816aa4f8c502", "123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP")
host = "https://192.168.173.212:31001"
namespace = "guest"

def get_activation_details(activation_id):
    """Fetches the activation details from OpenWhisk for a given activation ID."""
    url = f"{host}/api/v1/namespaces/{namespace}/activations/{activation_id}"
    try:
        response = requests.get(url, auth=auth, verify=False)  # Disable SSL verification
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def main(input_file, output_file):
    with open(input_file, "r") as f, open(output_file, "w") as out_f:
        for line in f:
            # Parse each line as JSON to extract activation ID
            try:
                activation_info = json.loads(line.strip())
                activation_id = activation_info.get("activationId")
                if not activation_id:
                    continue  # Skip if no activation ID is found
                
                # Fetch the activation details
                details = get_activation_details(activation_id)

                try:
                    details["response"]["result"] = ""
                except:
                    pass
                
                # Log the activation details to the output file
                out_f.write(json.dumps(details) + "\n")
                print(f"Logged details for activation ID: {activation_id}")
                
            except json.JSONDecodeError:
                print(f"Invalid JSON format: {line.strip()}")

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)