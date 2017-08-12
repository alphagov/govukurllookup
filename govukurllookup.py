"""govukurls class and methods for handling lookups using the gov.uk 
content api
"""
# coding: utf-8

from datetime import datetime
import requests
import pandas as pd
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

        # Instantiate class objects for later use.

        self.urldicts = pd.Series()


    def lookup(self):
        """
        Look up urls on GOV.UK content API
        """

        self.urldicts = self.dedupurls.apply(api_lookup)

        return self.urldicts

def api_lookup(url):
    
    '''
    Lookup a url on the GOV.UK content API

    Take a single url string as input, and returns a dict returned by an api
    call to the content api.
    '''
    # Form the api url

    api_url = "https://www.gov.uk/api/content{}".format(url)

    try:

        # Lookup the url and return the json

        results = requests.get(api_url).json()

        # Check whether api returned a redirect, and if so look up the api_url
        # using a standard http call so that we are returned the redirect url.

        if results['document_type'] == "redirect":
            redirect_url = "https://www.gov.uk" + url
            redirect = requests.get(redirect_url)

            # Extract redirected url, and use this in a new call to the
            # content api.

            redirected_url = redirect.url
            redirected_api = redirected_url.replace(
                "https://www.gov.uk",
                "https://www.gov.uk/api/content"
                )
            results = requests.get(redirected_api).json()

    except Exception as e:
        print(e)
        print('Error looking up ' + api_url)

    return results


class UrlData(object):
    def __init__(self, path, text):
        self.path = path
        self.text = text

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def extract_text(list_of_dict):
    """loop through list and for each dictionary extract the url and all contnet items. Concatenate content items and clean. Give back a url, text list"""
    urltext = []
    errors = []
    for page in list_of_dict:

        try:
            page_path = page['base_path']
            page_title = page['title']
            page_desc = page['description']
            page_body = safeget('details','body')
            page_parts = safeget('details','parts') 

            page_text =page_body + page_parts

            soup = BeautifulSoup(page_text,'html.parser') #parse html using bs4
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








