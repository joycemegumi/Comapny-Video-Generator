import json
from sqlalchemy import create_engine, text
import requests
import psycopg2
import boto3

#Create a connection to RDS PostgreSQL using SQLAlchemy
rds_host = "apan5450-db.c4c9zjbismmc.us-east-1.rds.amazonaws.com"
rds_port = "5432"
rds_dbname = "apan5450"
rds_username = "postgres"
rds_password = "postgres"

connection = None
try:
    conn_url = f"postgresql://{rds_username}:{rds_password}@{rds_host}:{rds_port}/{rds_dbname}"
    engine = create_engine(conn_url)
    connection = engine.connect()
    print("Successfully connected to RDS PostgreSQL using SQLAlchemy!")
except Exception as e:
    print("Error: Unable to connect to RDS PostgreSQL using SQLAlchemy.")
    print(e)

# Function to download external_video_url to S3 bucket
def download_video_s3(video_id, external_video_url):
    # Replace 'YOUR_BUCKET_NAME' with the name of your S3 bucket
    bucket_name = 'generatedvideos'

    # Replace with the desired name for the video in the S3 bucket
    video_name = f'{video_id}.mp4'

    try:
        # Get the MP4 video data from the URL
        response = requests.get(external_video_url)
        if response.status_code == 200:
            # Initialize S3 client
            s3 = boto3.client('s3')

            # Save the video data to S3 bucket
            s3.put_object(Bucket=bucket_name, Key=video_name, Body=response.content)

            # Generate the S3 URL for the uploaded object
            s3_url = f'https://d2es6o3m3r2tsa.cloudfront.net/{video_name}'

            return {
                'statusCode': 200,
                'body': s3_url
            }
        else:
            return {
                'statusCode': response.status_code,
                'body': 'Failed to download video from the URL.'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }


# Function to UPDATE video_url column with generated video_url            
def insert_video_url(video_id, s3_url):
    query = text(""" 
                    UPDATE generated_videos SET video_url = :s3_url
                    WHERE video_id = :video_id;
    """)
    connection.execute(query, parameters=dict(s3_url = s3_url, video_id=video_id))
    connection.commit()

# Function to check video
def check_video_status(video_id):
    print("TEST")
    query = text(""" SELECT external_id, video_url FROM generated_videos WHERE video_id = :video_id;""")
    result = connection.execute(query, parameters=dict(video_id=video_id)).fetchone()
    external_id = 0
    video_url = ""

    if result is None:
        return "No video_id exists"
    
    external_id = result[0]
    video_url = result[1]
        
    if video_url != "" and video_url != None:
        return {
          "status": "done", 
          "message": "", 
          "video_url": video_url
        }
        
    # Get video status and url from JSON2VIDEO endpoint
    # Connect to JSON2VIDEO API
    api_base_path = "https://api.json2video.com/v2"
    api_key = "ba9QXA0B603O6SrEXw5HJ74ApZCFTP6P48YIugrk"
    endpoint = f"{api_base_path}/movies" 
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(endpoint, headers=headers).json()
    # Check if request was successful and get the status and url if available
    for movie in response.get("movies", []):	
        if movie.get("project") == external_id:
            status = movie.get("status")
            external_video_url = movie.get("url")
            message = movie.get("message")
            
            s3_url = ""
            print(external_video_url)
            if external_video_url != None:
                # Download video from external_video_url to S3 bucket
                download_response_dict = download_video_s3(video_id, external_video_url)
                s3_url = download_response_dict['body']
                # Insert s3_url into video_url column of generated_videos table
                insert_video_url(video_id, s3_url)
            
            response_dict = {"status": status, 
                             "message": message, 
                             "video_url": s3_url}
            return response_dict
        else:
            return f"Could not find status of video_id {video_id}"

# Lambda handler
def lambda_handler(event, context):
    video_id = event['pathParameters']['video_id']
    response_dict = check_video_status(video_id)

    return {
        'statusCode': 200,
        'body': json.dumps(response_dict),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    }