#!/usr/bin/env python
import schedule
# from distutils.util import strtobool
from tooling import check_selenium_ready, subprocess_caller, json_to_metrics
import time
import logging
import json
from prometheus_client import start_http_server, Summary, Counter
from time import sleep
import re
import os
import datetime
import yaml


def wait_for_selenium(url):
    # wait till selenium/zalenium is ready to do work
    while True:
        if check_selenium_ready(url):
            return True
            # break
        else:
            logging.info("cannot contact selenium.. sleeping then retrying")
            time.sleep(5)


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(name)s:%(funcName)s():%(levelname)s:%(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S'
    )
    start_http_server(9180)
    logging.info("metrics started on port 9180")

    metric_session_time = Summary('zalenium_session', 'How many complete test sessions')
    metric_test_sum = Summary('zalenium_test', 'info about tests', ['file', 'class', 'function', 'status'])
    metric_test_count = Counter('zalenium_test_count', 'test counts', ['file', 'class', 'function', 'status'])

    # how often to run pytest
    frequency = int(os.getenv('FREQUENCY', 10))

    def business_logic(how_often):
        timeout = how_often - 1
        ## SETTINGS
        settings = {}
        hub_url = os.getenv('HUB_URL', "http://localhost:4444/wd/hub")
        settings["hub_url"] = hub_url
        # ensure the subprocess will die at least 1 second before we want to schedule another run
        now = datetime.datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S') + ('-%02d' % (now.microsecond / 10000))
        name = os.getenv('NAME', "unknown-test-name")
        settings = dict(
            hub_url=hub_url,
            now=now,
            name=name,
        )
        with open('config.yaml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
        logging.info("time to start doing stuff")
        # tell the subprocess to timeout 1 second before we wanna run again
        if check_selenium_ready(hub_url):
            # pytest with this flag will generate a report to .json
            cmd = "pytest ./tests --json-report --log-cli-level=INFO"
            # default file that pytest-json writes to
            report_file = ".report.json"
            logging.info("running command: {}".format(cmd))
            subprocess_caller(cmd=cmd, timeout=timeout)
            logging.info("completed the test run")
            json_to_metrics(
                report_file,
                metric_session_time,
                metric_test_sum,
                metric_test_count)
        else:
            logging.error("darn.. no selenium")
    schedule.every(frequency).seconds.do(business_logic, frequency)
    while True:
        schedule.run_pending()
        time.sleep(1)

