# Basic algorithm for API v0.2.5
#
# The basic algorithm aims at transforming an user input Excel file (CSV, XLS, XLSX) into an object of the **Dataset_core class** with the following attributes:
# - filename: the name of the Excel file including the extension
# - rows: the count of rows of the Excel file
# - columns: the count of columns of the Excel file
# - headers: the list of columns headers of the Excel file
# - metrics_headers and attributes_headers: the lists of columns header representing metrics and attributes
# - values: the processed values of the Excel file


# Import of the required librairies

import pandas as pd # importing pandas library
import os as os # importing os  library

# Definition of a reference list of Metrics headers

reference_metrics_headers = ['Revenue', 'Active Users', 'Turnover USD', 'Registrations', 'Costs', 'Sign-Ups', 'Churned Users']

# Definition of the Dataset_core class

class Dataset_core:

    def __init__(self, filepath):

        # Capture of the file's path
        # filepath expected to be a string - e.g. 'folder/spreadsheet.xlsx'

        self.filepath = filepath

        # Extraction of the file's name, including the extension

        self.filename = os.path.basename(self.filepath)

        # Opening of the file within a pandas dataframe ('df')

        if self.filename.lower().endswith(('.xls', '.xlsx')): # checking if file's extension is .xls or .xlsx
            self.df = pd.read_excel(self.filepath, sheet_name=0, header=0) # reading the Excel input file into a pandas dataframe
        elif self.filename.lower().endswith(('.csv')): # checking if file's extension is .csv
            self.df = pd.read_csv(self.filepath, header=0) # reading the CSV input file into a pandas dataframe

        # Count of the dataframe's rows and columns

        self.rows = len(self.df.index) # counting rows
        self.columns = len(self.df.columns) # counting columns

        # Capture of the dataframe's list of column headers

        self.headers = list(self.df.columns.values)

        # Capture of the dataframe's lists of metrics and attributes

        metrics_list=[]
        attributes_list=[]

        for header in self.headers:
            if header in reference_metrics_headers:
                metrics_list.append(header)
            else:
                attributes_list.append(header)

        self.metrics_headers = metrics_list
        self.attributes_headers = attributes_list

    def generate_content(self):

        # Capture of the dataframe's values

        self.df.insert(0 , 'row', self.df.index)
        self.values = self.df.to_dict(orient='records')
