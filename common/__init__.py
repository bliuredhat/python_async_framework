# encoding: utf-8

from .rest import RESTfulHandler
from .set_prometheus import Registry
from .set_prometheus import SERVER_STATUS

def generate_latest(registry=Registry):
    """Returns the metrics from the registry in latest text format as a string."""

    def sample_line(line, metric_type):
        if line.labels:
            labelstr = '{{{0}}}'.format(','.join(
                ['{0}="{1}"'.format(
                    k, v.replace('\\', r'\\').replace('\n', r'\n').replace('"', r'\"'))
                    for k, v in sorted(line.labels.items())]))
        else:
            labelstr = ''
        timestamp = ''
        if line.timestamp is not None:
            # Convert to milliseconds.
            timestamp = ' {0:d}'.format(int(float(line.timestamp) * 1000))
        name = line.name
        if metric_type == 'counter' and name.endswith('_total'):
            name = name[:-6]
        return '{0}{1} {2}{3}\n'.format(
            name, labelstr, int(line.value), timestamp)

    output = []
    for metric in registry.collect():
        try:
            mname = metric.name
            mtype = metric.type
            # Munging from OpenMetrics into Prometheus format.
            if mtype == 'counter':
                mname = mname
            elif mtype == 'info':
                mname = mname + '_info'
                mtype = 'gauge'
            elif mtype == 'stateset':
                mtype = 'gauge'
            elif mtype == 'gaugehistogram':
                # A gauge histogram is really a gauge,
                # but this captures the structure better.
                mtype = 'histogram'
            elif mtype == 'unknown':
                mtype = 'untyped'
            help_str = '# HELP {0} {1}\n'.format(mname, metric.documentation.replace('\\', r'\\').replace('\n', r'\n'))
            if 'Multiprocess' not in help_str:
                continue
            output.append('# HELP {0} {1}\n'.format(
                mname, metric.documentation.replace('\\', r'\\').replace('\n', r'\n')))
            output.append('# TYPE {0} {1}\n'.format(mname, mtype))

            for s in metric.samples:
                for suffix in ['_created', '_gsum', '_gcount']:
                    if s.name == metric.name + suffix:
                        break
                else:
                    line = sample_line(s, mtype)
                    if not line:
                        continue
                    output.append(line)
        except Exception as exception:
            exception.args = (exception.args or ('',)) + (metric,)
            raise

    return ''.join(output).encode('utf-8')
