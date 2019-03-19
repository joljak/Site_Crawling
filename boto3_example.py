import boto3

# Documents
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#client


def upload(s3, local_file_path, bucket, obj):
    """
    :param s3: AWS 서비스명, 여기서는 S3
    :param local_file_path: 로컬 파일 이름
    :param bucket: 업로드할 버킷 명
    :param obj: 업로드할 경로 ex: FM_Korea/FM_korea_ㄲㅈ_contents.csv
    :return:
    """

    s3.upload_file(local_file_path, bucket, obj)


def download(s3, bucket, obj, local_file_path):
    """
    :param s3: AWS 서비스명, 여기서는 S3
    :param bucket: 다운로드할 버킷 명
    :param obj: 다운로드할 파일 경로 ex: FM_Korea/FM_korea_ㄲㅈ_contents.csv
    :param local_file_path: 로컬 파일 이름
    :return:
    """
    s3.download_file(bucket, obj, local_file_path)


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
