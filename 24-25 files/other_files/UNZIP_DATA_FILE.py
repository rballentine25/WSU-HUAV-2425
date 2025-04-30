# to run this file, download the Pandas library with the following CMD line command:"pip install pandas"

import pandas as pd
import os
from datetime import date

# data files on the GitHub will most likely be in "pickle" format, which is a python serialization format
# that stores python objects in a binary file. pickle files are much smaller than their excel counterparts, 
# which have been too big to upload to GitHub. 
# Run this script to extract pickle files into Excel files, or to compress large excel files to pickles before
# uploading to GitHub.

# change this filename to the data file you want to open/convert:
filename = "9_11_24_Genset_test_3.xlsx"

# if the file is a pickle, a new file will be created in the same folder with the name data_convert_EXCEL_date.xlsx.
# opposite will happen if the file is an excel file.
if filename.endswith('.pkl'):
    data = pd.read_pickle("24-25 files/" + filename)
    data.to_excel('24-25 files/data_convert_EXCEL_' + date.today().strftime("%Y%m%d") + '.xlsx')

if filename.endswith('.xlsx'):
    data = pd.read_excel("24-25 files/" + filename)
    data.to_pickle('24-25 files/data_convert_PICKLE_' + date.today().strftime("%Y%m%d") + '.pkl')
