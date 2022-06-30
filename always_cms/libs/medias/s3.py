# -*- coding: utf-8 -*-

import boto3
from botocore.exceptions import ClientError
import os

from always_cms.libs import configurations


class S3:

	def __init__(self):
		self.s3 = boto3.resource(
	    's3',
	    region_name=configurations.get('s3_region_name').value,
	    endpoint_url=configurations.get('s3_endpoint_url').value,
	    use_ssl=configurations.get('s3_use_ssl').value,
	    aws_access_key_id=configurations.get('s3_access_key_id').value,
	    aws_secret_access_key=configurations.get('s3_secret_access_key').value
		)


	def get(self, filename):
		return self.s3.Object(configurations.get('s3_bucket_name').value, str(filename)).get()


	def upload(self, filename, content):
		try:
			obj = self.s3.Object(configurations.get('s3_bucket_name').value, str(filename))
			obj.upload_fileobj(content, ExtraArgs={'ACL': 'public-read'})
			return True
		except ClientError:
			return False


	def upload_from_file(self, filename, file_path):
		try:
			obj = self.s3.Object(configurations.get('s3_bucket_name').value, str(filename))
			obj.upload_file(file_path, ExtraArgs={'ACL': 'public-read'})
			return True
		except ClientError:
			return False


	def download(self, filename, file_path):
		try:
			obj = self.s3.Object(configurations.get('s3_bucket_name').value, str(filename))
			obj.download_file(file_path)
			return True
		except ClientError:
			return False


	def delete(self, filename):
		try:
			obj = self.s3.Object(configurations.get('s3_bucket_name').value, str(filename)).delete()
			return True
		except ClientError:
			return False