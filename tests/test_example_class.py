#!/usr/bin/env python

import pytest

# use this fixture to ensure the selenium 'driver' is available
@pytest.mark.usefixtures("driver")
# add whatever tests you like as a class.. ensure you prefix the class name with 'Test'
class TestExampleClass(object):

    # if you want a function to run.. ensure the name is prefixed with test_
    def test_wtf_is_my_ip(self, driver):
        driver.get("https://wtfismyip.com")
        print(driver.title)
        assert driver.title == 'WTF is my IP?!?!??'


    def test_bbc_title(self, driver):
        driver.get("https://bbc.co.uk")
        print(driver.title)
        assert driver.title == 'BBC - Home'
