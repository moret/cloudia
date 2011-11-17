# coding: utf-8
from __future__ import absolute_import

import os
import tornado.ioloop
import tornado.web

from model.group_manager import GroupManager


class SignedInHandler(tornado.web.RequestHandler):
    def cookie_data(self):
        access = self.get_secure_cookie('access')
        secret = self.get_secure_cookie('secret')
        signed_in = access != None and secret != None

        return access, secret, signed_in

class HomeHandler(SignedInHandler):
    def get(self):
        access, secret, signed_in = self.cookie_data()

        groups = {}
        if signed_in:
            groups = GroupManager().list_groups(access, secret)

        self.render('home.html', signed_in=signed_in, groups=groups)

class SigninHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_secure_cookie('access', self.get_argument('access'),
                expires_days=None)
        self.set_secure_cookie('secret', self.get_argument('secret'),
                expires_days=None)
        self.redirect('/')

class SignoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie('access')
        self.clear_cookie('secret')
        self.redirect('/')

class GroupStartHandler(SignedInHandler):
    def post(self):
        access, secret, signed_in = self.cookie_data()

        if signed_in:
            group = self.get_argument('group')
            how_many = self.get_argument('how_many')
            GroupManager().start_group(access, secret, group, how_many)
        self.redirect('/')

class GroupHandler(SignedInHandler):
    def get(self, group):
        access, secret, signed_in = self.cookie_data()

        if signed_in:
            group = GroupManager().get_group(access, secret, group)
            self.render('group.html', group=group)
        else:
            self.redirect('/')

class GroupStopHandler(SignedInHandler):
    def get(self, group):
        access, secret, signed_in = self.cookie_data()

        if signed_in:
            GroupManager().stop_group(access, secret, group)
        self.redirect('/')

class GroupCreateJobHandler(SignedInHandler):
    def post(self, group):
        access, secret, signed_in = self.cookie_data()
        bucket = self.get_argument('bucket')

        if signed_in:
            GroupManager().create_job(access, secret, group, bucket)
        self.redirect('/group/%s' % group)


def start():
    application = tornado.web.Application([
        (r"/", HomeHandler),
        (r"/signin", SigninHandler),
        (r"/signout", SignoutHandler),
        (r"/group/start", GroupStartHandler),
        (r"/group/(\w+)", GroupHandler),
        (r"/group/(\w+)/stop", GroupStopHandler),
        (r"/group/(\w+)/create_job", GroupCreateJobHandler),
    ], **{
        'static_path': os.path.join('static'),
        'template_path': os.path.join('templates'),
        'debug': True,
        'cookie_secret': 'not-really-secure-will-read-from-env-later'
    })
    application.listen(8888)
    print(' => Listening on 8888')
    tornado.ioloop.IOLoop.instance().start()
