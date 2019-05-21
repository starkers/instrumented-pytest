#!/usr/bin/env python

import pytest


@pytest.mark.usefixtures("driver")
class TestResource(object):

    # def test_anything(self, driver):
    #     assert False

    def test_my_ip(self, driver):
        driver.get("https://wtfismyip.com/text")
        print(driver.title)
        print("testing {}".format(driver))
        assert driver.title == 'WTF is my IP?!?!??'


    # def test_bbc(self, driver):
    #     driver.get("https://bbc.co.uk")
    #     print(driver.title)
    #     print("testing {}".format(driver))
    #     assert driver.title == 'BBC - Home'
