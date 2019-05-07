import os

import boto3

BUCKET_NAME = 'dankook-hunminjeongeum-data-bucket'

s3 = boto3.resource('s3')


def simple_s3_downloader():
    # S3에서 contents 안에 있는 CSV만 전체 일괄 다운로드
    bucket = s3.Bucket(BUCKET_NAME)
    for s3_object in bucket.objects.all():
        # Need to split s3_object.key into path and file name, else it will give error file not found.
        if '/contents/' not in s3_object.key or '.csv' not in s3_object.key:
            continue
        path, filename = s3_object.key.split('/contents/')
        if not os.path.exists(path):
            os.mkdir(path)
        bucket.download_file(s3_object.key, filename)
        os.rename(filename, f"{s3_object.key.split('/')[0]}/{filename}")
        # TODO: 사이트별 디렉토리 생성 및 파일 이동


if __name__ == '__main__':
    simple_s3_downloader()
