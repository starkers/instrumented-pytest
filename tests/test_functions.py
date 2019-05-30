#!/usr/bin/env python

import pytest


@pytest.mark.usefixtures("driver")
def test_google(driver):
    driver.get("https://google.com")
    assert driver.title == 'Google'

# this one will always fail
@pytest.mark.usefixtures("driver")
def test_failure(driver):
    assert "slow" == "quick"

