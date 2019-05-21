#!/usr/bin/env python
import pytest
import os, time
from distutils.util import strtobool
# import pytest_prom as prom


tests_from = os.getenv("TESTS_FROM", "./tests/")
verbose = strtobool(os.getenv("VERBOSE", "False"))
fail_fast = strtobool(os.getenv("FAIL_FAST", "False"))
prom_push = strtobool(os.getenv("PROM_PUSH", "True"))
prom_push_url = os.getenv("PROM_PUSH_URL", "http://localhost:9091")
prom_prefix = os.getenv("PROM_PREFIX", "aaa_")
prom_job = os.getenv("PROM_JOB", "jobname")


if __name__ == "__main__":


    argv = []

    # test_path = str(os.path.abspath(os.path.dirname(tests_from)))
    test_path = str(tests_from)
    argv.append(test_path)

    if verbose:
        argv.append('--verbose')
    if fail_fast:
        argv.append('--exitfirst')
    if prom_push:
        argv.append('--prometheus-pushgateway-url')
        argv.append(prom_push_url)

        argv.append('--prometheus-metric-prefix')
        argv.append(prom_prefix)

        argv.append('--prometheus-job-name')
        argv.append(prom_job)

        argv.append('--prometheus-extra-label')
        argv.append("foo=bar")

        argv.append('--capture=no')


    while True:
        print("launch time")
        print(argv)
        pytest.main(argv, plugins=["prom", "sugar"])
        time.sleep(20)


