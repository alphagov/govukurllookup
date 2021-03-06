[![Build Status](https://travis-ci.org/ukgovdatascience/govukurllookup.svg?branch=master)](https://travis-ci.org/ukgovdatascience/govukurllookup)
[![codecov](https://codecov.io/gh/ukgovdatascience/govukurllookup/branch/master/graph/badge.svg)](https://codecov.io/gh/ukgovdatascience/govukurllookup)
[![GitHub tag](https://img.shields.io/github/tag/ukgovdatascience/govukurllookup.svg)](https://github.com/ukgovdatascience/govukurllookup/releases)

# Helper module for using the GOV.UK content API

Helper module for returning data from the GOV.UK content API.

Take a pandas series as input, which should be a list of urls, without the `https://www.gov.uk` slug.

Returns a list of dictionaries from the response json.

## Usage

The module makes use of pandas for a range of functions when dealing with tabular data.

```
import pandas as pd
from govukurllookup import *

# Import urls from a csv file

urls = pd.read_csv('url_file.csv')

foo = govukurls(urls.url)

# In initialising the object, the list of urls will be deduplicated:
# Number of duplicates removed:

len(foo.urls) - len(foo.dedupurls)

# Run a lookup on the content API

foo.lookup()

# A list of dicts is returned

foo.urldicts

```
