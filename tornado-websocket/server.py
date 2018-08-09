# coding=utf-8
from tornado.web import RequestHandler, url, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import define, options
import os
import tornado.web
from tornado.websocket import WebSocketHandler

define("port", default=8000, type=int)

class IndexHandler(RequestHandler):
    def get(self):
        self.render("webchat.html")

class ChatHandler(WebSocketHandler):
    users = []
    def open(self):
        for user in self.users:
            user.write_message(u"%s 上线了" % self.request.remote_ip)
        self.users.append(self)

    def on_message(self, msg):
        for user in self.users:
            user.write_message(u"%s 说:%s" % (self.request.remote_ip, msg))

    def on_close(self):
        self.users.remove(self)
        for user in self.users:
            user.write_message(u"%s 下线了" % user.request.remote_ip)

class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)


def runserver():
    tornado.options.parse_command_line()
    current_path = os.path.dirname(__file__)
    settings = dict(
        static_path = os.path.join(current_path, "static"),
        template_path = os.path.join(current_path, "template"),
        #base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        cookie_secret = 'Aq6ZxqmtRaKC7KJcV3mKsNYXuRxrXEDakQfF5isGPY0='

        )
    app = Application([
            (r"/", IndexHandler),
            (r"/chat", ChatHandler),

        ], **settings
    )

    httpserver = HTTPServer(app, xheaders=True)
    httpserver.listen(options.port)

    IOLoop.current().start()


if __name__ == "__main__":
    runserver()