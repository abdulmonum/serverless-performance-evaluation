import base64
import json
import sys

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def write_json(image_path, output_path):
    encoded_image = image_to_base64(image_path)
    data = {
        "input_image": encoded_image
    }
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 encode_image.py <image_path> <output_json_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    output_json_path = sys.argv[2]
    write_json(image_path, output_json_path)
    print(f"JSON file with base64 encoded image saved to {output_json_path}")
