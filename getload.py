import json
import boto3
import csv

S3_BUCKET_NAME = "happyrobotczhu225test"
CSV_FILE_KEY = "Load_Data.csv"

s3 = boto3.client("s3")

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")  # Log full event
    
    try:
        # Extract reference_number from query parameters
        query_params = event.get("queryStringParameters") or {}
        reference_number = query_params.get("reference_number")

        if not reference_number:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing reference_number in query parameters"})
            }

        # Fetch CSV file from S3
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=CSV_FILE_KEY)
        lines = response["Body"].read().decode("utf-8-sig").splitlines()  # Fix BOM issue

        # Parse CSV
        reader = csv.DictReader(lines)
        headers = reader.fieldnames  # Get CSV column headers
        print(f"CSV Headers: {headers}")  # Debugging log

        # Search for matching reference_number in CSV
        for row in reader:
            if row.get("reference_number") == reference_number:
                return {
                    "statusCode": 200,
                    "body": json.dumps(row)
                }
        
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Load not found"})
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log error details
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }
