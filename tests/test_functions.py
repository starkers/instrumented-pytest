#!/usr/bin/env python

import pytest


@pytest.mark.usefixtures("driver")
def test_google(driver):
    driver.get("https://google.com")
    print(driver.title)
    print("testing {}".format(driver))
    assert driver.title == 'Google'

@pytest.mark.usefixtures("driver")
def test_fast_failure(driver):
    assert "slow" == "quick"


@pytest.mark.usefixtures("driver")
def test_foobar(driver):
    driver.get("https://google.com")
    print(driver.title)
    print("testing {}".format(driver))
    assert driver.title == 'Google'

    # driver.get("https://wtfismyip.com")
    # print(driver.title)
    # print("testing {}".format(driver))
    # assert driver.title == 'Google'
