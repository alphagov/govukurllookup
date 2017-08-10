# coding: utf-8

import re, requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

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

        self.urldicts = self.dedupurls.apply(api_lookup)

        return self.urldicts

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

        if results['document_type'] == "redirect":
            url = "https://www.gov.uk" + x
            s = requests.get(url)
            redirected_url = s.url
            redirected_api =redirected_url.replace("https://www.gov.uk", 
                "https://www.gov.uk/api/content")
            r = requests.get(redirected_api)
            results = r.json()


    except Exception as e:
        print(e)
        print('Error looking up ' + url)
        print('Returning url dict without api lookup')
    
    return results


class UrlData(object):
    def __init__(self, path, text):
        self.path = path
        self.text = text

        
def extract_text(list_of_dict):
    """loop through list and for each dictionary extract the url and all contnet items. Concatenate content items and clean. Give back a url, text list"""
    urltext = []
    errors = []
    for page in list_of_dict:

        try:
            page_path = page['base_path']
            page_title = page['title']
            page_desc = page['description']
            page_body = page['details']['body'] 

            soup = BeautifulSoup(page_body,'html.parser') #parse html using bs4
                # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
                # extract all text from html 
            txt = "{0} {0} {0}".format([page_title, page_desc, soup.getText()])
                # format string by replacing tabs, new lines and commas
            txt = txt.strip().replace("\t", " ").replace("\r", " ").replace('\n', ' ').replace(',', ' ')
                # remove remaining excess whitespace
            txt = " ".join(txt.encode('utf-8').split())
            urltext.append(UrlData(page_path,txt))

        except Exception as e:
            print(e)
            print('Error extracting text from ' + page_path)
            errors.append(page_path)
            print('Returning url text without html parsing')

    print('There were {:d} urls without body text'.format(len(errors)))
    return urltext








