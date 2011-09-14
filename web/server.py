# coding: utf-8
from __future__ import absolute_import

import tornado.ioloop
import tornado.web

from model import hello_world

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(hello_world.say())

def start():
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    application.listen(8888)
    print(' => Listening on 8888')
    tornado.ioloop.IOLoop.instance().start()
