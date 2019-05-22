#!/usr/bin/env python
from distutils.util import strtobool
from tooling import healthcheck_selenium
import os
import pytest
import time
import logging


if __name__ == "__main__":


    logger = logging.getLogger(__name__)

    # wait till selenium/zalenium is ready to do work
    while True:
        if healthcheck_selenium('http://localhost:4444/wd/hub'):
            break
        else:
            logger.info("cannot contact selenium.. sleeping then retrying")
            time.sleep(5)

    # arguments and plugins we're going to call pytest with
    argv = []
    plugins = []

    #                     [tests]
    # test_path is the directory containing pytest "test"..
    # in this case its ./tests/
    tests_from = os.getenv("TESTS_FROM", "./tests/")
    test_path = str(tests_from) #TODO: do we need str() ?
    argv.append(test_path)

    #                     [logging]
    # ensure "pytest-logging" is used.. (TIP: to tweak format.. see pytest.ini)
    plugins.append("logging")
    log_level = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO CRITICAL, ERROR
    argv.append('--log-cli-level={}'.format(log_level))
    argv.append('-o')
    argv.append('log_cli=true')
    # argv.append('log_cli_date_format=%Y-%m-%d %H:%M:%S')
    # argv.append('log_cli_format=%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)')

    argv.append('--disable-warnings')

    #                     [behaviour]
    # if set tests will stop and exit on any failures
    if strtobool(os.getenv("FAIL_FAST", "True")):
        argv.append('--exitfirst')


    #                     [metrics]
    # TODO: make this better..
    prom_job = os.getenv("PROM_JOB", "jobname")
    prom_prefix = os.getenv("PROM_PREFIX", "aaa_")
    prom_push = strtobool(os.getenv("PROM_PUSH", "True"))
    prom_push_url = os.getenv("PROM_PUSH_URL", "http://localhost:9091")
    if prom_push:
        pass
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

        # argv.append('--capture=no')

    # plugins we're going to use..
    # some will be automatically installed and active but lets insist on some

    while True:
        logger.info("launch time")

        print(argv)
        pytest.main(argv, plugins=plugins)
        logger.info("run complete... sleeping a little")
        time.sleep(40)


