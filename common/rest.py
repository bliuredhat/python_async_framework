# encoding: utf-8

import tornado.web
import json
from tornado.escape import json_encode
from tornado.web import RequestHandler, utf8
from tornado.web import MissingArgumentError
import time

from .set_prometheus import RESPONSES_COUNT, REQUEST_LATENCY, REQUEST_COUNT
#from .set_prometheus import HTTP_CONNECTED_ACCEPTED, CURRENT_REQUESTS, SERVER_CURRENT_REQUESTS
from .set_prometheus import DOWNSTREAM_REQUEST_COUNT, DOWNSTREAM_RESPONSE_COUNT, DOWNSTREAM_LATENCY
from setting import MODULE_NAME

class RESTfulHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(RESTfulHandler, self).__init__(application, request, **kwargs)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'text/json')
        self.finish({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            })
    #*************************************
    def downstream_prometheus(self):
        try:
            DOWNSTREAM_REQUEST_COUNT.labels(self.request.downstream_name).inc()
            error_code = '0'
            if int(self.request.response.code) < 200 or int(self.request.response.code) > 300:
                error_code = '1003'   # downstream error return
            DOWNSTREAM_RESPONSE_COUNT.labels(self.request.downstream_name, self.request.response.code,  error_code).inc()
            DOWNSTREAM_LATENCY.labels().observe(self.request.resp_time)
        except Exception as err:
            pass

    def start_timer(self):
        self.request.start_time = time.time()
        tmp_str = self.request.path
        self.request.method_name = tmp_str.strip('/')
        #HTTP_CONNECTED_ACCEPTED.inc()

        #CURRENT_REQUESTS.labels(MODULE_NAME).inc()
        #SERVER_CURRENT_REQUESTS.inc()

    def stop_timer(self):
        REQUEST_COUNT.labels(MODULE_NAME, self.request.method_name).inc()
        resp_time = time.time() - self.request.start_time
        self.request.resp_time = resp_time
        REQUEST_LATENCY.labels(MODULE_NAME, self.request.method_name).observe(resp_time)
        ec = '0'
        if int(self.get_status()) <200 or int(self.get_status()) > 300:
            ec = '-1'
        RESPONSES_COUNT.labels(MODULE_NAME, self.request.method_name, self.get_status(), ec).inc()

        #CURRENT_REQUESTS.labels(MODULE_NAME).dec()
        #SERVER_CURRENT_REQUESTS.dec()
        if hasattr(self.request, 'response'):
            self.downstream_prometheus()

    def prepare(self):
        if self.request.path != "/metrics":
            self.start_timer()
        uri = self.request.uri
        if "?" in uri:
            self.uri = uri[uri.find("?"):]
        else:
            self.uri = ""
        real_ip = self.request.headers.get("X-Forwarded-For")
        self.ip = real_ip or self.request.remote_ip

    def put(self, resource_id=None):
        raise tornado.web.HTTPError(404)

    def patch(self, resource_id=None):
        raise tornado.web.HTTPError(404)

    def delete(self, resource_id=None):
        raise tornado.web.HTTPError(404)

    def options(self, resource_id=None):
        raise tornado.web.HTTPError(404)


    def get_json_argument(self, name, default=None):

        try:
            args = tornado.escape.json_decode(self.request.body)
            name = tornado.escape.to_unicode(name)
            if name in args:
                return args[name]
            elif default is not None:
                return default
            else:
                raise MissingArgumentError(name)
        except:
            return self.get_argument(name, '')

    def head(self, resource_id=None):
        raise tornado.web.HTTPError(404)

    def finish(self, chunk=None):
        if self.request.path != "/metrics":
            self.stop_timer()
        self._return = chunk
        if chunk is not None:
            try:
                chunk = json_encode(chunk)
                callback = self.get_argument('callback', None)
                if callback is None:
                    # call base class finish method
                    super(RESTfulHandler, self).finish(chunk)
                else:
                    jsonp = "{jsfunc}({json})".format(jsfunc=callback, json=chunk)
                    self.set_header('Content-Type', 'application/javascript')
                    self.write(jsonp)
                    super(RESTfulHandler, self).finish()
            except:
                super(RESTfulHandler, self).finish(chunk)
        else:
            try:
                callback = utf8(self.get_argument('callback', None))
                self._write_buffer.insert(0, callback + '(')
                self._write_buffer.append(')')

                # call base class finish method
                super(RESTfulHandler, self).finish(chunk)
            except:
                super(RESTfulHandler, self).finish(chunk)

