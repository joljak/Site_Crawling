import json
import os
import sys
import boto3

FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, ".."))

with open(os.path.join(FILE_DIRECTORY, 'slang.json'), encoding='utf-8') as slang_file:
    # Open slang.json to read slang words
    # TODO: unordered 또는 축약 버전 쓸지 결정 후 확인
    KEYWORD = json.load(slang_file)['unordered']


def upload_s3(s3, bucket, local_file_path, obj):
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

    # S3 command
    # [upload, download]
    command = sys.argv[1]
    # Site selection
    # [Dog_drip, FM_korea, Ilbe, Clien, Inven, Ruliweb]
    site = sys.argv[2]
    # Keyword selection
    # keyword in slang.json
    keyword = sys.argv[3]
    # Data type
    # [link, content]
    data_type = sys.argv[4]

    # Test S3 bucket
    S3_BUCKET = "dankook-hunminjeongeum-data-bucket-test"

    # local object name to upload or download
    local_obj = f"{site}_{keyword}_{data_type}.csv"

    # S3 object to upload or download
    obj = f"{site}_{keyword}_{data_type}.csv"
    obj_folder = site
    s3 = boto3.client('s3')

    if command not in ['upload', 'download']:
        print('incorrect command input: command')
        print('[upload, download]')
        exit()
    if site not in ['Dog_drip', 'FM_korea', 'Ilbe', 'Clien', 'Inven', 'Ruliweb']:
        print('incorrect command input: site')
        print('[Dog_drip, FM_korea, Ilbe, Clien, Inven, Ruliweb]')
        exit()
    if keyword not in KEYWORD:
        print('incorrect command input: keyword')
        print('keyword in slang.json')
        exit()
    if data_type not in ['link', 'content']:
        print('incorrect command input: data_type')
        print('[link, content]')
        exit()

    if command == 'upload':
        upload_s3(s3, S3_BUCKET, obj, '/'.join([obj_folder, obj]))
    elif command == 'download':
        download_s3(s3, S3_BUCKET, '/'.join([obj_folder, obj]), local_obj)
    else:
        print('Incorrect command input. exit..')