import pytest
from os import environ
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@pytest.fixture(scope='function')
def driver(request):
    """

    :type request: object
    """
    # test_name = request.node.name
    hubAddress = "http://localhost:4444/wd/hub"
    browser = webdriver.Remote(
        command_executor=hubAddress,
        desired_capabilities=DesiredCapabilities.CHROME
    )

    print("===== main browser init done====")
    yield browser

    if browser:
        print("did summing here.. maybe retreived session ID?")
    else:
        raise WebDriverException("Never created!")

    def fin():
        # write logs or something here
        # https://github.com/saucelabs-sample-test-frameworks/Python-Pytest-Selenium/blob/master/conftest.py
        pass

    print("teardown---")
    if not request.node.rep_call.failed:
        print("telling zalenium the tests passed")
        browser.add_cookie({"name": "zaleniumTestPassed", "value": "true"})
    else:
        print("telling zalenium the tests failed")
        browser.add_cookie({"name": "zaleniumTestPassed", "value": "false"})
    browser.close()
    request.addfinalizer(fin)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)