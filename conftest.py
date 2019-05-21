import pytest
# from os import environ
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from os import getenv, path
import time
from datetime import datetime as dt
import pytest_prom

@pytest.fixture(scope='session')
def driver(request):
    """

    :type request: object
    """

    hub_address = getenv("HUB_ADDRESS", "http://localhost:4444/wd/hub")

    response = requests.head(hub_address)
    while response.status_code != 500:
        print('sleeping:', str(dt.now()), response.status_code)
        print('sleeping:', str(dt.now()), response.headers)
        time.sleep(1)
        response = requests.head(hub_address)

    browser = webdriver.Remote(
        command_executor=hub_address,
        desired_capabilities=DesiredCapabilities.CHROME
    )
    # always open ANY page so setting cookie on teardown isn't raised as an error
    browser.get("https://www.cloudflarestatus.com/")
    print("===== main browser init done====")
    yield browser

    if browser:
        print("did summing here.. maybe retrieved session ID?")
    else:
        raise WebDriverException("Never created!")

    def fin():
        # print("=== generate a report or summin in fin()")
        print("===== close()")
        browser.close()
        print("===== quit()")
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

    request.addfinalizer(fin)


