Aynchronous Application Python
================================


Usage
--------

## Configuration

The `prometheus_multiproc_dir` environment variable must be set to a directory
that the client library can use for metrics.
setup evn prometheus_multiproc_dir para:

    $ export prometheus_multiproc_dir=$path


To run server with the followed command::

     $ ./main.py --port={port}

    or

     $ cd tools && ./serverctl (start | stop)

How to add personal metrics for prometheus

`Registry` is a collector to registry metrics data in mutil process;
For example:


DOWNSTREAM_RECV_BYTS = Counter(
    'downstream_rcvd_bytes', '',
    ['server'],
    registry=Registry,
)


DOWNSTREAM_LATENCY = Histogram(
    'downstream_request_duration_milliseconds','',
    ['server'],
    registry=Registry,
)


DOWNSTREAM_REQUESTS = Gauge(
    'downstream_current_requests', '',
    ['server'],
    registry=Registry,
)



Reference::
-------

1. Tornado:
     http://www.tornadoweb.org/en/stable/

2. prometheus
    https://github.com/prometheus/client_python


