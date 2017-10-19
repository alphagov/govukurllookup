"""govukurls class and methods for handling lookups using the gov.uk 
content api
"""
# coding: utf-8

from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

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
        # Create and register a new `tqdm` instance with `pandas`
        # (can use tqdm_gui, optional kwargs, etc.)
        tqdm.pandas(desc="api lookup progress")

        self.urldicts = self.dedupurls.apply(api_lookup)

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

    def extract_titles_descs(self):
        """
        Loop through all url dicts and extract url and title and description.
        """

        # Use the .apply() method to loop through the urldicts series
        # and extract the titel and description.

        self.url_tit_des = self.urldicts.apply(extract_title_desc)

        # Convert the url_tit_des series into a datafram

        self.url_tit_des = self.url_tit_des.apply(pd.Series)

        return self.url_tit_des

    def extract_meta_and_texts(self):
        """
        Loop through all url dicts and extract url and title and description.
        """

        # Use the .apply() method to loop through the urldicts series
        # and extract the titel and description.

        self.meta = self.urldicts.apply(extract_meta)

        # Convert the url_tit_des series into a datafram

        self.meta = self.meta.apply(pd.Series)

        return self.meta

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

def safeget(dct, *keys):
    #return NoneTyoe instead of key value error if the dictionary key is missing
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def tidy(stringitem):
    #return string without tab, newlines, commas
    tidystring = stringitem.strip().replace("\t", " ").replace("\r", " ")
    tidystring = tidystring.replace('\n', ' ').replace(',', ' ')
    return tidystring

def extract_text(page):
    """
    For each dictionary extract the url and all content items.

    Concatenate content items and clean.
    Give back a dict containing url and text
    """
    urltext = dict.fromkeys(['url', 'text'])

    try:

        page_path = safeget(page, 'base_path').encode('utf-8').strip()
        page_title = safeget(page, 'title')
        page_desc = safeget(page, 'description')

        page_body = safeget(page, 'details', 'body')

        if page_body is None:
            page_body = unicode("", "utf-8")

        page_parts = safeget(page, 'details', 'parts')

        if page_parts is None:
            page_parts = unicode("", "utf-8")

        page_text = page_body + page_parts

        soup = BeautifulSoup(page_text, 'html.parser')
         
         # Remove all script and style elements using BeautifulSoup

        for script in soup(["script", "style"]):
            script.extract()
            
        # Concatenate the unicode text fields including all text from soup
        
        txt = u' '.join((page_title, page_desc, soup.getText())).encode('utf-8').strip()
        
        # Format string by replacing tabs, new lines and commas
        
        txt = txt.strip().replace("\t", " ").replace("\r", " ")
        txt = txt.replace('\n', ' ').replace(',', ' ')

        urltext['url'] = page_path
        urltext['text'] = txt

    except Exception as exc:
        print(exc)
        print('Error extracting text from ' + str(page_path))
        print('Returning url text without html parsing')

    return urltext

def extract_title_desc(page):
    """
    For each dictionary extract the url and page title and description.

    Concatenate content items and clean.
    Give back a dict containing url and text (title only)
    """
    url_tit_des = dict.fromkeys(['url', 'title', 'desc'])

    try:

        page_path = safeget(page, 'base_path').encode('utf-8').strip()
        page_title = safeget(page, 'title').encode('utf-8')
        page_desc = safeget(page, 'description').encode('utf-8')
        
        # Format string by replacing tabs, new lines and commas
        
        page_title = tidy(page_title)
        page_desc = tidy(page_desc)

        url_tit_des['url'] = page_path
        url_tit_des['title'] = page_title
        url_tit_des['desc'] = page_desc

    except Exception as exc:
        print(exc)
        print('Error extracting text from ' + page_path)
        print('Returning url text without html parsing')

    return url_tit_des

def extract_meta(page):
    """
    For each dictionary extract the url and page title and description.

    Concatenate content items and clean.
    Give back a dict containing url and text (title only)
    """
    meta_page = dict.fromkeys(['url', 'title', 'desc', 'text', 'doc_type', 'pub_date', 'pub_app', 'pub_title',])

    try:

        page_path = safeget(page, 'base_path').encode('utf-8').strip()
        page_title = safeget(page, 'title').encode('utf-8')
        page_desc = safeget(page, 'description').encode('utf-8')
        page_doctype = safeget(page, 'document_type').encode('utf-8')
        page_pubdate = safeget(page, 'first_published_at').encode('utf-8')
        page_pubapp = safeget(page, 'publishing_app').encode('utf-8')
        page_pubtitle = safeget(page, 'links', 'primary_publishing_organisation', 'title')

        page_body = safeget(page, 'details', 'body')

        if page_body is None:
            page_body = unicode("", "utf-8")

        page_parts = safeget(page, 'details', 'parts')

        if page_parts is None:
            page_parts = unicode("", "utf-8")

        page_text = page_body + page_parts

        soup = BeautifulSoup(page_text, 'html.parser')
         
         # Remove all script and style elements using BeautifulSoup

        for script in soup(["script", "style"]):
            script.extract()
            

        
        text = soup.getText().encode('utf-8').strip()
        
        # Format string by replacing tabs, new lines and commas
        
        page_title = tidy(page_title)
        page_desc = tidy(page_desc)
        page_text = tidy(text)

        meta_page['url'] = page_path
        meta_page['title'] = page_title
        meta_page['desc'] = page_desc
        meta_page['text'] = page_text
        meta_page['doc_type'] = page_doctype
        meta_page['pub_date'] = page_pubdate
        meta_page['pub_app'] = page_pubapp
        meta_page['pub_title'] = page_pubtitle

    except Exception as exc:
        print(exc)
        print('Error extracting text from ' + page_path)
        print('Returning url text without html parsing')

    return meta_page
