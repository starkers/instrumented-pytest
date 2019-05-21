# -*- coding: utf-8 -*-

import pytest


#  def pytest_addoption(parser):
    #  group = parser.getgroup('prom')
    #  group.addoption(
        #  '--foo',
        #  action='store',
        #  dest='dest_foo',
        #  default='2019',
        #  help='Set the value for the fixture "bar".'
    #  )
    #  parser.addini('HELLO', 'Dummy pytest.ini setting')
#  @pytest.fixture
#  def bar(request):
    #  return request.config.option.dest_foo



from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway

def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption(
        '--prometheus-pushgateway-url',
        help='Push Gateway URL to send metrics to'
    )
    group.addoption(
        '--prometheus-metric-prefix',
        help='Prefix for all prometheus metrics'
    )
    group.addoption(
        '--prometheus-extra-label',
        action='append',
        help='Extra labels to attach to reported metrics'
    )
    group.addoption(
        '--prometheus-job-name',
        help='Value for the "job" key in exported metrics'
    )

def pytest_configure(config):
    if config.getoption('prometheus_pushgateway_url') and config.getoption('prometheus_metric_prefix'):
        config._prometheus = PrometheusReport(config)
        config.pluginmanager.register(config._prometheus)

def pytest_unconfigure(config):
    prometheus = getattr(config, '_prometheus', None)

    if prometheus:
        del config._prometheus
        config.pluginmanager.unregister(prometheus)


class PrometheusReport:
    def __init__(self, config):
        self.config = config
        self.prefix = config.getoption('prometheus_metric_prefix')
        self.pushgateway_url = config.getoption('prometheus_pushgateway_url')
        self.job_name = config.getoption('prometheus_job_name')

        self.extra_labels = {item[0]: item[1] for item in [i.split('=', 1) for i in config.getoption('prometheus_extra_label')]}
        print(self.extra_labels)

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            registry = CollectorRegistry()
            name = '{prefix}{funcname}'.format(
                prefix=self.prefix,
                funcname=report.location[2]
            ).replace('.', '_')
            print("reporting: {}".format(name))
            metric = Gauge(name, report.nodeid, self.extra_labels.keys(), registry=registry)
            metric.labels(**self.extra_labels).set(1 if report.outcome == 'passed' else 0)
            pushadd_to_gateway(self.pushgateway_url, registry=registry, job=self.job_name)

