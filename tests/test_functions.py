#!/usr/bin/env python

import pytest


@pytest.mark.usefixtures("driver")
def test_google_title(driver):
    # driver.get("https://google.com")
    # print(driver.title)
    # print("testing {}".format(driver))
    # assert driver.title == 'Google'
    assert True

@pytest.mark.usefixtures("driver")
def test_wtf_title(driver):
    assert "quick" == "notquick"

    # driver.get("https://wtfismyip.com")
    # print(driver.title)
    # print("testing {}".format(driver))
    # assert driver.title == 'Google'
