# coding: utf-8

import re, requests
import pandas as pd
from datetime import datetime

class govukurls(object):
    """
    Clean and handle GOV.UK urls.
    """

    def __init__(self, urls):
        """
        Check that x is a pd series.
        """

        self.urls = urls
        assert isinstance(self.urls, pd.core.series.Series)
        
        self.dedupurls = self.urls.drop_duplicates().dropna()


    def lookup(self):
        """
        Look up urls on GOV.UK content API
        """

        self.urldicts = [api_lookup(i) for i in self.dedupurls]

def api_lookup(x):
    
    '''
    Simple function to lookup a url on the GOV.UK content API
    Takes as an input the dictionary output by clean_url()
    '''

    url = "https://www.gov.uk/api/content" + x
    
    try:
       
        # read JSON result into r
        r = requests.get(url)
        results = r.json()

    except Exception as e:
        print(e)
        print('Error looking up ' + url)
        print('Returning url dict without api lookup')
    
    return results
