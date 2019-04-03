import json
import os
import sys
import boto3


def upload_s3(local_path, s3_path):
    s3.upload_file(local_path, S3_BUCKET, s3_path)


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, ".."))

    with open(os.path.join(ROOT_DIRECTORY, 'slang.json'), encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']
    s3 = boto3.client('s3')
    S3_BUCKET = "dankook-hunminjeongeum-data-bucket-test"

    command = sys.argv[1] if sys.argv[1] in ['upload', 'download'] else exit('Choice [upload, download')
    site = sys.argv[2] if sys.argv[2] in ['Inven', 'Clien', 'Ruliweb'] else exit('Site Error')

    for keyword in SLANG:
        file = f'{site}_{keyword}_content.csv'
        local_path = os.path.join(os.path.join(ROOT_DIRECTORY, site), file)
        if os.path.exists(local_path) is False:
            continue

        if command == 'upload':
            upload_s3(local_path, '/'.join([site, file]))