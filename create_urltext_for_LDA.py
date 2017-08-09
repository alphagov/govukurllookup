
"""
This script takes a list of truncated urls (missing www.gov.uk) in csv form, accesses their text content through the gov.uk content API, extracts the title, description and body text, combines them into one field and writes the url and text to file. 

Example usage:
python test.py --fpath input/test_urltext.csv --wpath input/test_tags.csv

"""   

__author__ = "Ellie King"
__copyright__ = "Government Digital Service, 07/08/2017"


from govukurllookup import *
import argparse

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument(
    '--fpath', dest='filepath', metavar='FILENAME', default=None,
    help='import trunacated url data in csv'
)
parser.add_argument(
    '--wpath', dest='outpath', metavar='FILENAME', default=None,
    help='export url, text data in csv'
)

def import_urls(fpath):
    """#import the csv as a dataframe but extract the first column as a panda series so it is typed correctly for govukurls class"""
    turls = pd.read_csv(fpath).iloc[:,0] 

    return(turls)

def wtf(wpath):
    '''write data structure to a csv file list to pd then to_csv'''
    f = open(wpath,'w')
    f.write('path,text\n')
    for row in urltext:
        f.write(row.path+','+row.text+'\n')
    f.close()
    return(0)


if __name__ == '__main__':
    args = parser.parse_args()

print("Loading input file {}".format(args.filepath))
trunc_urls = import_urls(
        fpath = args.filepath, 
        ) #import the csv 


print("creating class object")
prepped  = govukurls(trunc_urls) #check pandas series and drop any duplicates

print("Looking up api") 
prepped.lookup() #api_lookup over the series to put json content into dict

print("creating list of dictionaries")
list_of_dict = prepped.urldicts

print("Extracting and cleaning the right content")
urltext = extract_text(list_of_dict)

print("Writing output to file")
wtf(wpath = args.outpath)