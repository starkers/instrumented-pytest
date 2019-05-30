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
        level=logging.INFO,
        format='%(asctime)s:%(name)s:%(funcName)s():%(levelname)s:%(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S'
    )
    start_http_server(9180)
    logging.info("metrics started on port 9180")

    metric_session_time = Summary('zalenium_session', 'How many complete test sessions')
    metric_test_sum = Summary('zalenium_test', 'info about tests', ['file', 'class', 'function', 'status'])
    metric_test_count = Counter('zalenium_test_count', 'test counts', ['file', 'class', 'function', 'status'])

    # how often to run pytest
    frequency = int(os.getenv('FREQUENCY', 30))

    def business_logic(how_often):
        # ensure the subprocess will die at least 1 second before we want to schedule another run
        timeout = how_often - 1

        # lets start a dictionary which we'll fill with some settings
        settings = {}
        # loop over all env vars
        for k, v in os.environ.items():
            # match any starting with "CONF_"
            if re.search("^CONF_", k):
                # strip off the prefix
                k = re.sub(r'^CONF_', '', k)
                # lowercase the key
                k = k.lower()
                # put the key value into the setting dict
                settings[k] = v

        timestamp = datetime.datetime.now()
        timestamp.strftime('%Y-%m-%d %H:%M:%S') + ('-%02d' % (timestamp.microsecond / 100))
        timestamp = str(timestamp)

        hub_url = os.getenv('HUB_URL', "http://localhost:4444/wd/hub")
        name = os.getenv('NAME', "unknown-test-name")

        settings["name"] = name
        settings["timestamp"] = timestamp
        settings["hub_url"] = hub_url


        # TODO: extra labels?
        # write settings to config.yaml
        with open('config.yaml', 'w') as outfile:
            yaml.dump(settings, outfile, default_flow_style=False)
        logging.info("wrote config to config.yaml")

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

