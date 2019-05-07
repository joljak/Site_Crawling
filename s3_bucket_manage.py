import json
import os
import sys
import boto3


def upload_s3(local_path, s3_path):
    s3.upload_file(local_path, S3_BUCKET, s3_path)


def download_s3(s3_path, local_path):
    s3.download_file(S3_BUCKET, s3_path, local_path)


if __name__ == '__main__':
    ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, ".."))

    with open(os.path.join(ROOT_DIRECTORY, 'slang.json'), encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']

    if len(sys.argv) < 4:
        exit('''
                Argument Error
                Choice Command [upload, download]
                Choice Site [Clien, Inven, Ruliweb]
                Choice Type [link, content, processed, labeled]
                usage) s3_bucket_manage.py [Command] [Site] [Type]
                ''')

    command = sys.argv[1] if sys.argv[1] in [
        'upload', 'download'] else exit('Choice [upload, download')
    site = sys.argv[2] if sys.argv[2] in ['clien', 'dc_inside', 'dog_drip', 'fm_korea', 'ilbe',
                                          'inven', 'ppompu', 'ruliweb'] else exit('Choice [clien, dc_inside, dog_drip, fm_korea, ilbe, inven, ppompu, ruliweb')
    type = sys.argv[3] if sys.argv[3] in ['contents', 'processed'] else exit(
        'Choice [contents, processed]')

    s3 = boto3.client('s3')
    S3_BUCKET = "dankook-hunminjeongeum-data-bucket"
    for keyword in SLANG:
        file = f'{site}_{keyword}_{type}.csv'
        
        local_path = '/'.join([ROOT_DIRECTORY, site, type, file])
        s3_path = '/'.join([site, type, file])
     
        if command == 'upload':
            if os.path.exists(local_path) is True:
                upload_s3(local_path, s3_path)
        elif command == 'download':
            if os.path.exists(local_path) is True:
                os.remove(local_path)
            download_s3(s3_path, local_path)
