#!/usr/bin/env python
import pytest
import os, time
from distutils.util import strtobool
import requests


tests_from = os.getenv("TESTS_FROM", "./tests/")
verbose = strtobool(os.getenv("VERBOSE", "False"))
fail_fast = strtobool(os.getenv("FAIL_FAST", "True"))
prom_push = strtobool(os.getenv("PROM_PUSH", "True"))
prom_push_url = os.getenv("PROM_PUSH_URL", "http://localhost:9091")
prom_prefix = os.getenv("PROM_PREFIX", "aaa_")
prom_job = os.getenv("PROM_JOB", "jobname")


def healthcheck_selenium(url):
    """
    validates selenium healthcheck/status
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
    print("check selenium is ready: {}".format(url))
    try:
        req = requests.get(url, timeout=5)
        if req.status_code == 200:
            data = req.json()
            if data['value']['ready']:
                return True
            else:
                print("message: " + data['value']['message'])
    except:
        print("url: {} is not ready".format(url))
        return False


if __name__ == "__main__":

    # wait till selenium/zalenium is ready to do work
    while True:
        if healthcheck_selenium('http://localhost:4444/wd/hub'):
            break
        else:
            time.sleep(5)



    argv = []

    # test_path = str(os.path.abspath(os.path.dirname(tests_from)))
    test_path = str(tests_from)
    argv.append(test_path)

    if verbose:
        argv.append('--verbose')
    if fail_fast:
        argv.append('--exitfirst')
    if prom_push:
        # argv.append('--prometheus-pushgateway-url')
        # argv.append(prom_push_url)
        #
        # argv.append('--prometheus-metric-prefix')
        # argv.append(prom_prefix)
        #
        # argv.append('--prometheus-job-name')
        # argv.append(prom_job)
        #
        # argv.append('--prometheus-extra-label')
        # argv.append("foo=bar")

        argv.append('--capture=no')


    while True:
        print("launch time")
        print(argv)
        # pytest.main(argv, plugins=["prom"])
        pytest.main(argv)
        print("run complete... sleeping a little")
        time.sleep(20)


