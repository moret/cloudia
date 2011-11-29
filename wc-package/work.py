import re
import os
import argparse
import tempfile
import boto

parser = argparse.ArgumentParser(description='Count words from S3 file')
parser.add_argument('sqs_name', metavar='sqs_name',
        type=unicode, nargs=1,
        help='S3 uri - ex.: s3:/bucket/dir/file')

aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
sqs_name = parser.parse_args().sqs_name[0]

s3_conn = boto.connect_s3()
sqs = boto.connect_sqs().get_queue(sqs_name)

wc = 0

sqs_message = sqs.read()
while sqs_message:
    aws_bucket_uri = sqs_message.get_body()
    bucket_name, bucket_key = re.match('^s3://([\w\d_-]*)/(.*)$',
            aws_bucket_uri).groups()

    key = s3_conn.get_bucket(bucket_name).get_key(bucket_key)

    local_file_handler, local_filename = tempfile.mkstemp()
    key.get_contents_to_filename(local_filename)

    f = open(local_filename)
    for i, l in enumerate(f):
        pass
    wc += i + 1

    sqs.delete_message(sqs_message)
    sqs_message = sqs.read()

print wc
