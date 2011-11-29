import re
import os
import argparse
import tempfile
import boto

parser = argparse.ArgumentParser(description='Count words from S3 file')
parser.add_argument('aws_bucket_uris', metavar='aws_bucket_uris',
        type=unicode, nargs='+',
        help='S3 uri - ex.: s3:/bucket/dir/file')

aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']

s3_conn = boto.connect_s3()

wc = 0

for aws_bucket_uri in parser.parse_args().aws_bucket_uris:
    bucket_name, bucket_key = re.match('^s3://([\w\d_-]*)/(.*)$',
            aws_bucket_uri).groups()

    key = s3_conn.get_bucket(bucket_name).get_key(bucket_key)

    local_file_handler, local_filename = tempfile.mkstemp()
    key.get_contents_to_filename(local_filename)

    f = open(local_filename)
    for i, l in enumerate(f):
        pass
    wc += i + 1

print wc
