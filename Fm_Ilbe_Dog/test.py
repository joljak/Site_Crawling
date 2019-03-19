import os
import json
from pathlib import Path

import boto3

from requests_html import HTMLSession

p = Path(__file__).parents[0]

print(p)

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, "../.."))

bach = os.path.abspath(os.path.join(__file__, "../.."))


def upload(s3, local_file_path, bucket, obj):
    """
    :param s3: AWS 서비스명, 여기서는 S3
    :param local_file_path: 로컬 파일 이름
    :param bucket: 업로드할 버킷 명
    :param obj: 업로드할 경로 ex: FM_Korea/FM_korea_ㄲㅈ_contents.csv
    :return:
    """

    s3.upload_file(local_file_path, bucket, obj)


def download_s3(s3, bucket, obj, local_file_path):
    """
    :param s3: AWS 서비스명, 여기서는 S3
    :param bucket: 다운로드할 버킷 명
    :param obj: 다운로드할 파일 경로 ex: FM_Korea/FM_korea_ㄲㅈ_contents.csv
    :param local_file_path: 로컬 파일 이름
    :return:
    """
    s3.download_file(bucket, obj, local_file_path)


if __name__ == '__main__':
    # with open(os.path.join(FILE_DIRECTORY, 'slang.json')) as slang_file:
    #     # Open slang.json to read slang words
    #     KEYWORD = json.load(slang_file)['namu_wiki'][156]
    #     # print(KEYWORD)
    # bach()

    bucket = "dankook-hunminjeongeum-data-bucket"
    obj = "FM_korea_ㄲㅈ_contents.csv"
    obj_folder = "FM_Korea"
    s3 = boto3.client('s3')
    # join을 써서 경로 지정하여 obj 파일 업로드
    upload(s3, obj, bucket, '/'.join([obj_folder, obj]))

    local_obj = "local_FM_korea_ㄲㅈ_contents.csv"
    download_s3(s3, bucket, '/'.join([obj_folder, obj]), local_obj)
