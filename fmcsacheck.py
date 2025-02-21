import json
import requests

FMCSA_API_URL = "https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/"
API_KEY = "cdc33e44d693a3a58451898d4ec9df862c65b954"

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # Log incoming request

    # Extract MC number from query parameters
    mc_number = event.get("queryStringParameters", {}).get("mc_number")
    if not mc_number:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "MC number is required"})
        }

    # Construct API request
    url = f"{FMCSA_API_URL}{mc_number}"  # Append MC number to URL
    params = {"webKey": API_KEY}  # Pass API key in query params

    try:
        response = requests.get(url, params=params)
        print("FMCSA API Response:", response.text)  # Log raw response

        if response.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"FMCSA API Error: {response.status_code}"})
            }

        # Attempt to parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error: Could not decode JSON response")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Invalid JSON response from FMCSA API"})
            }

        # Check if content exists and is a list
        if "content" not in data or not isinstance(data["content"], list) or len(data["content"]) == 0:
            print("Error: 'content' field missing or empty")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Unexpected API response format"})
            }

        # Extract carrier info safely
        carrier_info = data["content"][0].get("carrier", {})
        allowed_to_operate = carrier_info.get("allowedToOperate", "N")  # Default to "N" if missing
        status = "verified" if allowed_to_operate == "Y" else "unverified"

        return {
            "statusCode": 200,
            "body": json.dumps({"status": status})
        }

    except Exception as e:
        print("Unexpected Error:", str(e))  # Log the actual error
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error"})
        }
