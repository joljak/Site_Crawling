import boto3

def upload(s3, local_file_path, bucket, obj):
	s3.upload_file(local_file_path, bucket, obj)

if __name__ == "__main__":
	bucket = "dankook-hunminjeongeum-data-bucket"
	s3 = boto3.client('s3')
	local_file_path ="./upload.txt"
	upload(s3, local_file_path, bucket, "DC_INSIDE/upload.txt")
