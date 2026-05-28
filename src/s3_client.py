import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional

def get_s3_client():
    """Create and return a boto3 S3 client using credentials from environment variables.
    Expected variables (loaded via python-dotenv in app.py):
        AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY
        AWS_DEFAULT_REGION
        S3_BUCKET_REGION (optional, overrides AWS_DEFAULT_REGION for bucket operations)
    """
    # Determine the region to use – bucket-specific if provided, otherwise default
    region = os.getenv('S3_BUCKET_REGION') or os.getenv('AWS_DEFAULT_REGION')
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=region,
    )

def upload_file_to_s3(file_obj, bucket_name: str, object_name: str) -> bool:
    """Upload a file-like object to the specified S3 bucket.
    Returns True on success, False otherwise.
    """
    s3 = get_s3_client()
    try:
        s3.upload_fileobj(file_obj, bucket_name, object_name)
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return False
    return True

def generate_presigned_download_url(bucket_name: str, object_name: str, expiration: int = 3600) -> Optional[str]:
    """Generate a presigned URL to download the given S3 object.
    Returns the URL string on success, or None on failure.
    """
    s3 = get_s3_client()
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=expiration)
    except ClientError as e:
        print(f"Presigned URL error: {e}")
        return None
    return response
