import boto3

s3 = boto3.client("s3")


def download_image(bucket_name: str, object_key: str) -> bytes:

    s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)

    return s3_response["Body"].read()


def delete_uploaded_image(bucket_name: str, object_key: str):

    s3.delete_object(Bucket=bucket_name, Key=object_key)
