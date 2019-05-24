#!/usr/bin/env python
import pytest
import os, time
from distutils.util import strtobool
import requests
import subprocess
import logging
import json
from prometheus_client import Summary, Counter
import re


# tests_from = os.getenv("TESTS_FROM", "./tests/")
# verbose = strtobool(os.getenv("VERBOSE", "False"))
# fail_fast = strtobool(os.getenv("FAIL_FAST", "True"))
# prom_push = strtobool(os.getenv("PROM_PUSH", "True"))
# prom_push_url = os.getenv("PROM_PUSH_URL", "http://localhost:9091")
# prom_prefix = os.getenv("PROM_PREFIX", "aaa_")
# prom_job = os.getenv("PROM_JOB", "jobname")


def check_selenium_ready(url):
    """
    validates selenium healthcheck/status has capacity
    :param url: a URL including '/wd/hub' URI
    :return bool: if zalenium is ready

    # we want to target .value.ready == True:
    # EG
    curl -s http://localhost:4444/wd/hub/status | jq .value
    {
      "ready": true,
      "message": "Hub has capacity",
      "build": {
        "revision": "unknown",
        "time": "unknown",
        "version": "3.141.59"
      },
      "os": {
        "arch": "amd64",
        "name": "Linux",
        "version": "5.0.16-200.fc29.x86_64"
      },
      "java": {
        "version": "1.8.0_191"
      }
    }
    """

    # we want the URI to be /wd/hub/status.. so: /wd/hub + /status
    url = url + "/status"
    logging.info("checking if selenium is ready: {}".format(url))
    try:
        req = requests.get(url, timeout=5)
        if req.status_code == 200:
            data = req.json()
            if data['value']['ready']:
                return True
            else:
                logging.error("message: " + data['value']['message'])
                return False
    except:
        logging.error("url: {} is not ready".format(url))
        return False


def subprocess_caller(
        cmd,
        timeout=False,
        logfile="stdout.txt",
        extra_env=None
        ):
    """
    launches a subprocess, returns True/False based on return-code
    :param cmd:
    :param timeout:     timeout if running the command takes longer than this (s)
    :return:
    """

    with open(logfile, "w+") as temp_file:
        kwargs = {}
        if timeout is not False:
            kwargs['timeout'] = int(timeout)

        if extra_env is None:
            extra_env = {}

        # kwargs['env'] = extra_env
        # kwargs['stdout'] = temp_file
        # kwargs['stderr'] = temp_file
        kwargs['shell'] = True
        kwargs['universal_newlines'] = True

        try:
            subprocess.check_call(cmd, **kwargs)
            temp_file.flush()
            return True
        except:
            return False

def json_to_metrics(
        jsonfile,
        metric_session_total,
        # metric_test_failed,
        # metric_test_launched,
        # metric_failed,
        metric_test_sum,
        metric_test_count):


    tests_dir = "tests"
    logging.debug("parsing: " + jsonfile)
    with open(jsonfile) as temp_file:
        data = json.load(temp_file)
        time_in_epoch = data['created']
        duration_total = data['duration']
        exitcode = data['exitcode']
        if exitcode == "0":
            passed = True
        else:
            passed = False
        logging.info("time: {}, duration: {}, passed: {}".format(
            time_in_epoch,
            duration_total,
            passed
        ))
        metric_session_total.observe(duration_total)

        jobs_total = data['summary']['total']
        jobs_failed = data['summary']['failed']
        jobs_passed = data['summary']['passed']
        logging.info("passed: {}, failed: {}, total: {}".format(
            jobs_passed, jobs_failed, jobs_total
        ))

        # metric_test_failed.inc(jobs_failed)
        # metric_test_passed.inc(jobs_passed)
        # metric_test_launched.inc(jobs_total)

        def is_a_class(nodeid):
            if nodeid.count(":") > 2:
                return True
            else:
                return False

        # individual test metrics
        logging.info("== test report ==")
        for t in data['tests']:
            logging.info("----------")
            nodeid = t['nodeid']
            status = t['outcome']
            duration_call = t['call']['duration']
            duration_setup = t['setup']['duration']
            duration_teardown = t['setup']['duration']
            time_total = duration_call + duration_setup + duration_teardown
            logging.info("[ test: {}, status: {}, time: {} ]".format(
                nodeid,
                status,
                time_total
            ))
            # extract the real filename from "nodeid"
            test_file_name = re.sub(r'^{}/'.format(tests_dir), '', nodeid).split("::")[0]
            # everything After the filename (in 'nodeid')
            after_test_file_name = re.sub(r'^{}/'.format(tests_dir), '', nodeid).split("::", 1)[1]

            # strip the test_ from the name of the file
            test_file_name = re.sub(r'^test_', '', test_file_name)
            # remove .py from the end
            test_file_name = re.sub(r'.py$', '', test_file_name)

            logging.debug("file: " + test_file_name)
            if is_a_class(nodeid):
                class_name = after_test_file_name.split("::")[0]
                func_name = after_test_file_name.split("::")[1]
            else:
                func_name = after_test_file_name.split("::")[0]
                class_name = "None"

            # we know all functions are prefixed with test_
            # lets remove those
            func_name = re.sub(r'^test_', '', func_name)
            # we know all Classes are prefixed with Test
            # lets remove those
            class_name = re.sub(r'^Test', '', class_name)
            logging.debug("class: " + class_name)
            logging.debug("func_name: " + func_name)

            # dunno if a Counter or Summary is best
            # lets try both for now
            metric_test_count.labels(
                test_file_name,
                class_name,
                func_name,
                status).inc()

            metric_test_sum.labels(
                test_file_name,
                class_name,
                func_name,
                status).observe(duration_call)
