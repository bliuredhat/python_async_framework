#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import time
import signal
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import options, parse_command_line, parse_config_file, define
import prometheus_client
from common import RESTfulHandler, Registry, SERVER_STATUS
from common import generate_latest
from demo import TestHandler
from setting import LOGGER


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class StatusHandler(tornado.web.RequestHandler):
    def get(self):
        status_file = os.path.join(BASE_DIR, "proc/status")
        if os.path.exists(status_file):
            self.set_status(200)
            self.write("ok")
        else:
            self.set_status(503)
            self.write("")

class MetricsHandler(RESTfulHandler):
    def get(self):
        status_file = os.path.join(BASE_DIR, "proc/status")
        if os.path.exists(status_file):
            SERVER_STATUS.set(0)
        else:
            SERVER_STATUS.set(-1)
        LOGGER.info("Metric pid:%d" % os.getpid())
        self.write(generate_latest(Registry))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/status", StatusHandler),
        (r"/test/?(\S+)?", TestHandler),
        (r"/metrics", MetricsHandler),
    ])


#***************control status**********************
def del_proc():
    status_file = os.path.join(BASE_DIR, "proc/status")
    if os.path.exists(status_file):
        os.unlink(status_file)
    if not os.path.exists(status_file):
        LOGGER.info("remove status sucessfully")
    else:
        LOGGER.error("Failed to remove status file")
    prometheus_dir = os.path.join(BASE_DIR, ".prometheus_multiproc_dir")
    for file_obj in os.listdir(prometheus_dir):
        file_path = os.path.join(prometheus_dir, file_obj)
        os.remove(file_path)
#***************** End status*************************

#**************** handle signal *********************
def sig_handler(sig, frame):
    LOGGER.warn('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    LOGGER.info('Stopping http server')
    server.stop()
 
    LOGGER.info('Will Shutdown in %s seconds ...', 60)
    io_loop = tornado.ioloop.IOLoop.instance()
 
    deadline = time.time() + 60
    # remove status file
    del_proc()
    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            LOGGER.info('Shutdown')
    stop_loop()
#********************End signal*************************

if __name__ == "__main__":
    # ./main.py --port={port}  &
    define("port", default=10089, help="run on the given port", type=int)
    define("status_path", default=os.path.join(BASE_DIR, "proc/status"), help="the abspath of status", type=str)
    define("prometheus_multiproc_dir", default=os.path.join(BASE_DIR, ".prometheus_multiproc_dir"), help="config prometheus_multiproc_dir para", type=str)
    parse_command_line()
    app = make_app()
    server = tornado.httpserver.HTTPServer(app)
    server.bind(options.port)
    proccess_count = tornado.process.cpu_count() # 本机CPU个数
    server.start(proccess_count)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    tornado.ioloop.IOLoop.current().start()


