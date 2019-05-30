# from selenium.common.exceptions import WebDriverException
# import datetime
from os import getenv, path
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pytest
import requests
import time
import yaml
import logging


@pytest.fixture(scope='session')
def driver(request):
    """

    :type request: object
    """

    # read some config from 'config.yaml'
    # typically launch.py will put some handy things in there
    with open('config.yaml', 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)

    hub_address = cfg['hub_url']

    # zalenium session name
    session_name = "{}-{}".format(
        cfg['timestamp'],
        cfg['name'],
    )

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['name'] = "{}".format(
        session_name
    )
    browser = webdriver.Remote(
        command_executor=hub_address,
        desired_capabilities=capabilities
    )
    # always open ANY page so setting cookie on teardown isn't raised as an error
    browser.get("https://www.cloudflarestatus.com/")
    logging.debug("===== main browser init done====")
    # this yield passes the browser object out to any tests asking for 'driver'
    # think is this as where a 'return' would normally be but for pytest the pattern is to
    # return the object here
    yield browser

    # NOTE: keep this section in-case you have issues with the selenium driver.
    #       can be used to debug the issues like session timeouts
    # if browser:
    #     logging.info("browser existed and was shut down OK")
    # else:
    #     raise WebDriverException("Never created!")

    def fin():
        logging.debug("closing and quitting browser")
        browser.close()
        browser.quit()
        # https://github.com/saucelabs-sample-test-frameworks/Python-Pytest-Selenium/blob/master/conftest.py
        pass

    print("===== session teardown")
    # print("total tests = {}".format(request.session.testscollected))
    # print("tests that failed = {}".format(request.session.testsfailed))

    if request.session.testsfailed == 0:
        print("telling zalenium the tests passed")
        browser.add_cookie({"name": "zaleniumTestPassed", "value": "true"})
    else:
        print("telling zalenium the tests failed")
        browser.add_cookie({"name": "zaleniumTestPassed", "value": "false"})

    # lets end with the absolute final tear-down function
    request.addfinalizer(fin)


