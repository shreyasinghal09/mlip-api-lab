from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
import json
#config file
config_file_path = "config.json"

try:
    with open(config_file_path, "r") as config_file:
        config_data = json.load(config_file)
        endpoint = config_data.get("VISION_ENDPOINT")
        key = config_data.get("VISION_SUBSCRIPTION_KEY")
except FileNotFoundError:
    raise ValueError(f"Config file not found!")


credentials = CognitiveServicesCredentials(key)

client = ComputerVisionClient(
    endpoint=endpoint,
    credentials=credentials
)

def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10
    print("Line 19")
    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)
    print("Line 22")
    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]
    print("Line 27")
    # SDK call
    result = client.get_read_result(operationId)
    print("Line 30")
    # Try API
    retry = 0
    
    while retry < maxRetries:
        if result.status.lower () not in ['notstarted', 'running']:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)
        
        retry += 1
    
    if retry == maxRetries:
        return "max retries reached"
    print("Line 19")
    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
        return res_text
    else:
        return "error"
