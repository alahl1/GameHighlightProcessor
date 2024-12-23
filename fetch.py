import boto3
import requests
import json

# Constants
API_URL = "https://sport-highlights-api.p.rapidapi.com/basketball/highlights"
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"  # Replace with your RapidAPI key
S3_BUCKET_NAME = "YOUR_S3_BUCKET_NAME_HERE"  # Replace with your S3 bucket name
REGION = "YOUR_AWS_REGION_HERE"  # Replace with your AWS region

# Query parameters for the highlights endpoint
QUERY_PARAMS = {
    "date": "2023-12-01",  # Example: Replace with the desired date in YYYY-MM-DD format
    "leagueName": "NCAA",  # Replace with a league available for the basic tier
    "limit": 10  # Example: Number of highlights to fetch
}

# Headers for the API request
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "sport-highlights-api.p.rapidapi.com"
}

def fetch_highlights():
    """
    Fetch basketball highlights from the API.
    """
    try:
        response = requests.get(API_URL, headers=HEADERS, params=QUERY_PARAMS, timeout=120)
        response.raise_for_status()
        highlights = response.json()
        return highlights
    except requests.exceptions.RequestException as e:
        print(f"Error fetching highlights: {e}")
        return None

def save_to_s3(data, file_name):
    """
    Save data to an S3 bucket.
    """
    try:
        s3 = boto3.client("s3", region_name=REGION)

        # Ensure bucket exists
        try:
            s3.head_bucket(Bucket=S3_BUCKET_NAME)
            print(f"Bucket {S3_BUCKET_NAME} exists.")
        except Exception:
            print(f"Bucket {S3_BUCKET_NAME} does not exist. Creating...")
            s3.create_bucket(Bucket=S3_BUCKET_NAME)

        # Save data to S3
        s3_key = f"highlights/{file_name}.json"
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(data)
        )
        print(f"Highlights saved to S3: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {e}")

def process_highlights():
    """
    Main function to fetch and process basketball highlights.
    """
    print("Fetching highlights...")
    highlights = fetch_highlights()
    if highlights:
        print("Saving highlights to S3...")
        save_to_s3(highlights, "basketball_highlights")

if __name__ == "__main__":
    process_highlights()
