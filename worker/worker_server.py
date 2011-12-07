from __future__ import absolute_import

import sys
sys.path = ['.'] + sys.path

import re
import tempfile
import json

import daemon
import tornado.ioloop
import tornado.web
import boto

from boto.sqs.message import Message
from tornado.httpclient import AsyncHTTPClient

from model.group_manager import GroupManager

class WordCounter(object):
    def map(self, bucket, sqs):
        for key in bucket.get_all_keys():
            if key.size > 0:
                key_url = 's3://' + key.bucket.name + '/' + key.name
                sqs.write(Message(body=key_url))

    def process(self, local_filename):
        f = open(local_filename)
        for i, l in enumerate(f):
            pass
        return i + 1

    def reduce(self, results):
        return sum(results)

word_counter = WordCounter()

class Worker(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.__results = []

    def process(self, local_filename):
        self.__results.append(word_counter.process(local_filename))

    def results(self):
        return self.__results

worker = Worker()

class MapHandler(tornado.web.RequestHandler):
    def get(self, group_name, bucket_name):
        self.write('begin mapping...\n')

        s3_conn = boto.connect_s3()
        sqs_conn = boto.connect_sqs()

        sqs = sqs_conn.get_queue(group_name)
        if sqs == None:
            sqs = sqs_conn.create_queue(group_name)

        word_counter.map(s3_conn.get_bucket(bucket_name), sqs)

        self.write('done\n')

class ProcessHandler(tornado.web.RequestHandler):
    def get(self, group_name):
        self.write('begin working...\n')

        s3_conn = boto.connect_s3()
        sqs = boto.connect_sqs().get_queue(group_name)
        sqs_message = sqs.read()
        while sqs_message:
            aws_bucket_uri = sqs_message.get_body()
            bucket_name, bucket_key = re.match('^s3://([\w\d_-]*)/(.*)$',
                    aws_bucket_uri).groups()

            key = s3_conn.get_bucket(bucket_name).get_key(bucket_key)

            local_file_handler, local_filename = tempfile.mkstemp()
            key.get_contents_to_filename(local_filename)

            worker.process(local_filename)

            sqs.delete_message(sqs_message)
            sqs_message = sqs.read()

        self.write('done\n')

class ReduceHandler(tornado.web.RequestHandler):
    def get(self, group_name):
        self.write('begin working...\n')

        group = GroupManager().get_group(None, None, group_name)

        responses = []
        responses_count = 0
        expected_responses = len(group.instances)

        def cb(response):
            responses.append(json.loads(response.body))
            responses_count += 1
            if responses_count == expected_responses:
                self.write(json.dumps(word_counter.reduce(responses)))

        for instance in group.instances:
            http = AsyncHTTPClient()
            http.fetch('http://' + instance.public_dns_name + ':8888/results',
                    cb)

class ResultsHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(worker.results()))

class ResetHandler(tornado.web.RequestHandler):
    def get(self):
        worker.reset()
        self.write('reset\n')

class ShutdownHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('shutting down...\n')
        tornado.ioloop.IOLoop.instance().stop()

def server():
    application = tornado.web.Application([
        (r"/map/([\w\d]*)/([\w\d]*)", MapHandler),
        (r"/process/(.*)", ProcessHandler),
        (r"/reduce/(.*)", ReduceHandler),
        (r"/results", ResultsHandler),
        (r"/reset", ResetHandler),
        (r"/shutdown", ShutdownHandler),
    ], **{
        'cookie_secret': 'not-really-secure-will-read-from-env-later'
    })
    application.listen(8888)
    print(' => Listening on 8888')
    tornado.ioloop.IOLoop.instance().start()

context = daemon.DaemonContext(working_directory='/home/ubuntu',
        detach_process=True)

with context:
    server()
