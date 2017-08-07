# Helper module for using the GOV.UK content API (v0.0.0.9000)

Helper module for returning data from the GOV.UK content API.

Take a pandas series as input, which should be a list of urls, without the `https://www.gov.uk` slug.

Returns a list of dictionaries from the response json.

## Usage

The module makes use of pandas for a range of functions when dealing with tabular data.

```
import pandas as pd
from govukurllookup import govukurllookup

# Import urls from a csv file

urls = pd.read_csv('url_file.csv')

foo = govukurls(urls.url)

# In initialising the object, the list of urls will be deduplicated:
# Number of duplicates removed:

len(foo.urls) - len(foo.dedupurls)

# Run a lookup on the content API

foo.lookup()

```
