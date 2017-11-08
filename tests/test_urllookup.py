""" Tests for the govukurls class from the govukurllookup module.
"""
# coding: utf-8

import pytest
import requests
from govukurllookup import api_lookup, govukurls
import pandas as pd

def is_connected():
    """
    Check that gov.uk is accessible.

    Used to skip tests if no internet connection is available.
    """
    import socket
    try:
        host = socket.gethostbyname("www.gov.uk")
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

class TestGovukurls(object):

    def setup_method(self):
        """
        Setup test conditions for subsequent method calls.
        For more info, see: https://docs.pytest.org/en/2.7.3/xunit_setup.html
        """

        # Load in test data as pandas dataframe
        # Test urls are duplicated twice.

        self.urls = pd.read_csv('tests/test_urls.csv')

        # Note that self.urls is a dataframe so we must specify the appropriate
        # column: `url`

        self.urlsclass = govukurls(self.urls.url)

    def test_govukurls_deduplication(self):
        """
        Test that duplicate urls are successfully removed by the init method.
        """

        assert len(self.urlsclass.dedupurls) < len(self.urls)
        assert len(self.urlsclass.dedupurls) == len(self.urls) / 2

    @pytest.mark.skipif(not is_connected(), reason="Cannot connect to gov.uk")
    def test_api_lookup(self):
        """
        Test the api_lookup function works for a single url.

        Uses the first deduplicated url to check that the api_lookup function
        returns the same as a simple api call using requests.

        Note that an internet connection is required for these api calls!
        The test will be skipped if this is not available.
        """

        # Set up the url for the api call

        expected_url = 'https://www.gov.uk/api/content{}'.format(self.urlsclass.dedupurls[0])

        # Make request and extract json.

        expected = requests.get(expected_url).json()

        assert api_lookup(self.urlsclass.dedupurls[0]) == expected

    @pytest.mark.skipif(not is_connected(), reason="Cannot connect to gov.uk")
    def test_lookup_method(self):
        """
        Test the lookup method function works for a series of urls.

        Note that an internet connection is required for these api calls!
        The test will be skipped if this is not available.
        """

        # Run lookup method

        self.urlsclass.lookup()

        assert len(self.urlsclass.urldicts) == len(self.urlsclass.dedupurls)

        # TODO: test a redirect url

    def test_extract_text(self):
        """
        Test the extract_text() method.

        """

        # Run lookup and extract_text methods

        self.urlsclass.lookup()
        self.urlsclass.extract_texts()

        assert len(self.urlsclass.urldicts) == len(self.urlsclass.urltxt)
        assert self.urlsclass.urltxt.shape == (20, 2)
        assert self.urlsclass.urltxt.iloc[0, 1] == '/business-support-helpline'
