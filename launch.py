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

    metric_session_time = Summary('zalenium_session_time', 'How many complete test sessions')
    # metric_failed = Summary('zalenium_failed', 'info about failing tests', ['file', 'class', 'function', 'status'])
    metric_test_sum = Summary('zalenium_test_sum', 'info about passing tests', ['file', 'class', 'function', 'status'])
    metric_test_count = Counter('zalenium_test_count', 'fine grained info about each test', ['file', 'class', 'function', 'status'])


    def business_logic(frequency):
        logging.info("business open")
        # how frequently to run tests?
        hub_url = os.getenv('HUB_URL', "http://localhost:4444/wd/hub")
        # ensure the subprocess will die at least 1 second before we want to schedule another run
        timeout = frequency - 1
        if check_selenium_ready(hub_url):

            # pytest with this flag will generate a report to .json
            cmd = "pytest ./tests --json-report --log-cli-level=INFO"
            # default file that pytest-json writes to
            jsonfile = ".report.json"

            logging.info("running command: {}".format(cmd))
            subprocess_caller(cmd=cmd, timeout=timeout)
            logging.info("completed the test run")
            json_to_metrics(
                jsonfile,
                metric_session_time,
                metric_test_sum,
                metric_test_count)
        else:
            logging.error("darn.. no selenium")


    frequency = int(os.getenv('FREQUENCY', 60))
    schedule.every(frequency).seconds.do(business_logic, frequency)

    while True:
        schedule.run_pending()
        time.sleep(1)

