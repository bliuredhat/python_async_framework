# -*- encoding: utf-8 -*-
"""
name: set_prometheus.py
"""

import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import multiprocess, CollectorRegistry

Registry = CollectorRegistry()
multiprocess.MultiProcessCollector(Registry)

#*********Counter*******************
#HTTP_CONNECTED_ACCEPTED = Counter(
#    'http_connections_accepted', '',
#    registry=Registry,
#)
REQUEST_COUNT = Counter(
    'module_requests', '',
    ['module', 'method'],
    registry=Registry,
)
RESPONSES_COUNT = Counter(
    'module_responses', '',
    ['module', 'method', 'response_code', 'ec'],
    registry=Registry,
)


#********Histogram ****************
REQUEST_LATENCY = Histogram(
    'request_duration_milliseconds', '',
    ['module', 'method'],
    registry=Registry,
)

#*******Gauge*********************

#CURRENT_REQUESTS = Gauge(
#    'module_current_requests', '',
#    ['module'],
#    registry=Registry,
#    multiprocess_mode='livesum',
#)
#SERVER_CURRENT_REQUESTS = Gauge(
#    'server_current_requests', '',
#    registry=Registry,
#    multiprocess_mode='livesum'
#    )

SERVER_STATUS = Gauge(
    'service_status', '',
    registry=Registry,
    multiprocess_mode='livesum'
)

#******DOWNSTREAM********************

DOWNSTREAM_REQUEST_COUNT= Counter(
    'downstream_requests', '',
    ['server',],
    registry=Registry,
)

DOWNSTREAM_RESPONSE_COUNT= Counter(
    'downstream_responses', '',
    ['server', 'response_code', 'error_code'],
    registry=Registry,
)

DOWNSTREAM_LATENCY = Histogram(
    'downstream_request_duration_milliseconds','',
    registry=Registry,
)
"""
DOWNSTREAM_REQUESTS = Gauge(
    'downstream_current_requests', '',
    ['server'],
    registry=Registry,
)
DOWNSTREAM_RECV_BYTS = Counter(
    'downstream_rcvd_bytes', '',
    ['server'],
    registry=Registry,
)
"""
#***************@decorator********
def prometheus_downstream(downstream_name):
    """
    downstream_name: the name for dowstrean server name
    """
    def decorator(func):
        """
        func: the name of function will be runned
        """
        def wrapper(*arg, **kargs):
            #DOWNSTREAM_REQUEST_COUNT.labels(downstream_name).inc()
            #DOWNSTREAM_REQUESTS.labels(downstream_name).inc()
            response = func(*arg, **kargs)
            #DOWNSTREAM_REQUESTS.labels(downstream_name).dec()
            if hasattr(response, 'code'):
               pass
               #DOWNSTREAM_COUNT.labels(downstream_name, response.code).inc()
               if hasattr(response, 'request_time'):
                   pass
                   #DOWNSTREAM_LATENCY.labels(downstream_name).observe(response.request_time)
               if hasattr(response, 'body'):
                   pass
                   #DOWNSTREAM_RECV_BYTS.labels(downstream_name).inc(len(response.body))
            return response

        return wrapper

    return decorator

