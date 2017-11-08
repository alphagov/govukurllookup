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

    def __init__(self, urls, content_store_url="https://www.gov.uk/api/content"):
        """
        Check that x is a pd series.
        """

        self.urls = urls
        self.content_store_url = content_store_url
        assert isinstance(self.urls, pd.core.series.Series)

        self.dedupurls = self.urls.drop_duplicates().dropna()

    def lookup(self):
        """
        Look up urls on GOV.UK content API
        """

        self.urldicts = self.dedupurls.apply(
            api_lookup, args=(self.content_store_url,)
        )

        return self.urldicts

    def extract_texts(self):
        """
        Loop through all url dicts and extract url and text.
        """

        # Use the .apply() method to loop through the urldicts series
        # and extract the text.

        self.urltxt = self.urldicts.apply(extract_text)

        # Convert the urltxt series into a datafram

        self.urltxt = self.urltxt.apply(pd.Series)

        return self.urltxt

def api_lookup(base_path, content_store_url):
    '''
    Lookup a url on the GOV.UK content API

    Take a single url string as input, and returns a dict returned by an api
    call to the content api.
    '''
    # Form the api url

    url = content_store_url + base_path

    try:

        # Lookup the url and return the json

        results = requests.get(url).json()

        # Check whether api returned a redirect, and if so look up the api_url
        # using a standard http call so that we are returned the redirect url.

        if results['document_type'] == "redirect":
            redirect_url = "https://www.gov.uk" + base_path
            redirect = requests.get(redirect_url)

            # Extract redirected url, and use this in a new call to the
            # content api.

            redirected_api = content_store_url + redirect.url.path
            results = requests.get(redirected_api).json()

    except Exception as e:
        print(e)
        print('Error looking up ' + url)

    return results

def safeget(dct, *keys):
    #return NoneTyoe instead of key value error if the dictionary key is missing
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def extract_text(page):
    """
    For each dictionary extract the url and all content items.

    Concatenate content items and clean.
    Give back a dict containing url and text
    """
    urltext = dict.fromkeys(['url', 'text'])

    try:

        page_path = safeget(page, 'base_path').strip()
        page_title = safeget(page, 'title')
        page_desc = safeget(page, 'description')

        page_body = safeget(page, 'details', 'body')
        page_parts = safeget(page, 'details', 'parts')

        page_text = (page_body or "") + (page_parts or "")

        soup = BeautifulSoup(page_text, 'html.parser')
         
         # Remove all script and style elements using BeautifulSoup

        for script in soup(["script", "style"]):
            script.extract()
            
        # Concatenate the unicode text fields including all text from soup
        
        txt = ' '.join((page_title, page_desc, soup.getText())).strip()
        
        # Format string by replacing tabs, new lines and commas
        
        txt = txt.strip().replace("\t", " ").replace("\r", " ")
        txt = txt.replace('\n', ' ').replace(',', ' ')

        urltext['url'] = page_path
        urltext['text'] = txt

    except Exception as exc:
        print(exc)
        print('Error extracting text from ' + page_path)
        print('Returning url text without html parsing')

    return urltext
