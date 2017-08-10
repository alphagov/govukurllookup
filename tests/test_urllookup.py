# coding: utf-8

import unittest
import pytest

import pandas as pd
import re, requests
import sys
sys.path.append('/Users/ellieking/govuk_api')
from govukurllookup import *

def test_api_lookup():
    r = requests.get('https://www.gov.uk/api/content/government/news/national-apprenticeship-award-winners-announced')

    expected = r.json()

    assert api_lookup('/government/news/hertfordshire-apprentice-wins-national-apprenticeship-award') == expected

def test_govukurls_class_init(self):

    assert (len(self.urlsclass.dedupurls) < len(self.urls))
    assert (len(self.urlsclass.dedupurls) == len(self.urls) / 2)



class TestCleanUrls(unittest.TestCase):

    def setUp(self):#runs everytime a test id run
        
        # Load in test data

        self.urls = [
                '/',
                '/government/world/turkey',
                '/government/publications/crown-commercial-service-customer-update-september-2016/crown-commercial-service-update-september-2016',
                '/guidance/guidance-for-driving-examiners-carrying-out-driving-tests-dt1/05-candidates-with-an-impairment',
                '/search/this-is/a-search/url',
                '/help/this/is/a/help/url',
                '/contact/this/is/a/contact/url'
                ]

        self.urls = self.urls * 2

        # Convert to pandas series (as expected by the class)

        self.urls = pd.Series(self.urls, name='full_url')
        
        self.urlsclass = govukurls(self.urls)

#    def tearDown(self):
#
    




