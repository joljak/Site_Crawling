import boto3

# Documents
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client


def download(s3, bucket, obj, local_file_path):
    s3.download_file(bucket, obj, local_file_path)


def upload(s3, local_file_path, bucket, obj):
    s3.upload_file(local_file_path, bucket, obj)


def make_public_read(s3, bucket, key):
    s3.put_object_acl(ACL='public-read', Bucket=bucket, Key=key)


if __name__ == "__main__":
    bucket = "Sample"
    obj = "download.jpg"
    local_file_path = "download.jpg"
    s3 = boto3.client('s3')
    download(s3, bucket, obj, local_file_path)
    upload(s3, local_file_path, bucket, "upload.jpg")
    make_public_read(s3, bucket, "upload.jpg")
