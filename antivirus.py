import requests
import json
import time
import os


# Get input a file for Scan

def scan_file(file_path):
    print()
    print("Scanning file:", file_path)
    
    file_name = os.path.basename(file_path)

    # Upload file for Scan

    url = "https://www.virustotal.com/api/v3/files"

    files = { "file": (file_name, open(file_path, "rb"), "application/data") }
    headers = {
        "accept": "application/json",
        "x-apikey": "f24b14192195bb2336356c06c993db2c39c7e10c38c73b025b4b7bd8e3294e67"
    }

    response = requests.post(url, files=files, headers=headers)
    print()
    print("Status:", response.status_code)
    print()

    # Check status okay

    if response.status_code != 200:
        print("Request failed")
        return False
    
    # Parse response

    print("Scanning for malicious code")
    result = json.loads(response.text)
    file_id = result['data']['id']
    # print(file_id)

    # Scan results

    url = f"https://www.virustotal.com/api/v3/analyses/{file_id}"

    headers = {
        "accept": "application/json",
        "x-apikey": "f24b14192195bb2336356c06c993db2c39c7e10c38c73b025b4b7bd8e3294e67"
    }

    # Wait for scan to complete
    print("Awaiting scan")

    for i in range(10):
        for _ in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
        response = requests.get(url, headers=headers)
        # check if response again
        if response.status_code != 200:
            print("Request failed")
            return False
        
        result = json.loads(response.text)
        status = result['data']['attributes']['status']
        print(status,i)
        # print(response.text)
        if status == "completed":
            print (result['data']['attributes']['stats'])
            return True

    print("\nScan not complete!")
    return False

# Recursion for file paths within given folder
# folder_path: full path of given folder

def scan_folder(folder_path):
    for file in os.listdir(folder_path):
        complete_path = os.path.join(folder_path, file)
        if os.path.isdir(complete_path):
            scan_folder(complete_path)
        else:
            scan_file(complete_path)

input_path = input("Enter your desired folder path:")
scan_folder(input_path)
