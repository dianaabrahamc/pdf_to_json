# importing required modules
import PyPDF2
import re
from os.path import exists
import argparse
import sys
import json


sys.path.append('C:/Users/diana/Documents')


class convertPdfToJson():
    def __init__(self):
        self.keys = []
        self.index_value = []
        self.values = []
        self.parser_arg()
        self.input_pdf_file()
        self.extract_pages()

        # closing the pdf file object
        self.pdfFileObj.close()

    def parser_arg(self):
        '''
        This function parses the command line arguments and stores it into 
        variables for use.
        '''
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--input', required=True)
        self.parser.add_argument('--output', required=True)
        self.args = self.parser.parse_args()
        self.inputPDFdir = self.args.input
        self.outputjsondir = self.args.output

    def input_pdf_file(self):
        '''
        PDF file path to be checked if valid else path value error
        Creating pdf object if valid file path

        Raises
        ------
        ValueError
            'Path is not correct'.

        Returns
        -------
        None.

        '''
        
        if exists(self.inputPDFdir):
            self.pdfFileObj = open(self.inputPDFdir, 'rb')
            # creating a pdf file object
            self.pdfReader = PyPDF2.PdfFileReader(self.pdfFileObj)
            # creating a pdf reader object
        else:
            raise ValueError('Path is not correct')

    def filter_list_empty_string(self, lst):
        '''
        Removing empty strings

        Parameters
        ----------
        lst : TYPE list

        Returns
        -------
        lst_filter : TYPE list

        '''
        lst_filter = list(filter(None, lst))
        
        return lst_filter

    def convert_list_string(self,lst_input):
        '''
        This function is to convert list to string.
        
        '''
        str_output = ''.join(str(x) for x in lst_input)
        return str_output

    def extracted_text_sort(self, text):
        '''
        This function converts the extracted text string to list of lines
        and sorts it.
        '''
        page_text_list = text.split("\n")
        # Converting string to a list with the pdf lines as elements.

        page_text_list_sorted = []
        for texts in page_text_list:
            texts = re.sub('  +', ' ', texts)
            texts = re.sub(r'[^\x00-\x7F\u25cf]', '', texts)
            # removes non-ascii values except bullet points

            page_text_list_sorted.append(texts.strip())
            # removing whitespaces from the list of strings

        self.page_text_list_sorted = self.filter_list_empty_string(
            page_text_list_sorted)
        # removing empty strings

    def find_headings_keys(self):
        '''
        This function is to find the keys by extracting the text which are 
        headings from the pdf file.

        Returns
        -------
        None.

        '''
        for i in range(len(self.page_text_list_sorted)):
            if self.page_text_list_sorted[i] == self.page_text_list_sorted[i][0]*\
                len(self.page_text_list_sorted[i]):
                self.keys.append(self.page_text_list_sorted[i-1])
                self.index_value.append(i+1)

    def find_values_pg_strt(self):
        '''
        This function is to find the values by extracting text which are under
        the headings from the pdf file.
        This function captures the values from the first to last excluding the 
        the last section.
        '''
        for j in range(len(self.index_value)-1):
            self.values.append(
                self.page_text_list_sorted[self.index_value[j]:self.index_value[j+1]-2])

    def find_values_pg_end(self):
        '''
        This function captures the values in the starting of the next page if 
        pages are more than 1 and appending it to the values under last heading
        of the previous page.
        
        '''
        value_pglast = self.page_text_list_sorted[self.index_value[-1]:]
        # Capturing the value under the last heading

        # Here index value is noted considering the possibility that there 
        # could be no values before heading in the next page.
        if (self.pages > 1) and (self.index_value[0]-2 > 0):
            value_in_new_page = self.page_text_list_sorted[0:self.index_value[0]-2]
            value_pglast.append(value_in_new_page)
        
        self.values.append(value_pglast)
    
    def name_add_mail_values(self):
        '''
        This function sorts and stores the text from the page starting 
        to different variables identifying specific string characters.

        '''
        name_add_mail = self.page_text_list_sorted[0:self.index_value[0]-2]
        name_add_mail_sorted = []
        for texts in name_add_mail:
            name_add_mail_split = re.sub('\|*', '', texts)
            name_add_mail_split = name_add_mail_split.strip().split("  ")

            for i in name_add_mail_split:
                name_add_mail_sorted.append(i)

        for i in name_add_mail_sorted:
            email_find = re.findall('\S+@+\S+', i)
            ph_find = re.findall('\S* \w*-\w*', i)

            name_find = re.findall(
                '[A-Za-z+ ]', name_add_mail_sorted[0])
            name = ''.join(str(x) for x in name_find)

            addr_find = re.findall('[A-Za-z*, A-Za-z* A-Za-z0-9*]',
                                   name_add_mail_sorted[3])
            addr = ''.join(str(x) for x in addr_find)

            if email_find != []:
                email = self.convert_list_string(email_find)
            if ph_find != []:
                ph = self.convert_list_string(ph_find)
                address= ph+','+addr
        
        return name,address,email
    
    def create_dict_name_addr(self, name, address, email):
        ''''
        Creating dictionary with the name, address, email and phone from the
        page start.
        '''
        dict_name_addr_mail = {"name": name, "address": address, "email": email}
        return dict_name_addr_mail
    
    def create_dict_values(self):
        '''
        Creating dictionary with keys as headings and values as text under 
        headings.
        '''
        dict_heading_values={self.keys[i]: self.values[i]
                        for i in range(len(self.keys))}
        return dict_heading_values

    def create_output_json(self,dictionary):
        '''
        This function creates output json file taking input from the command
        line.

        '''
        with open(self.outputjsondir, "w", encoding='utf-8') as outfile:
            json.dump(dictionary, outfile, indent=4, ensure_ascii=False)

    def extract_pages(self):
        '''
        This function extracts pages from the pdf file.

        '''
        # Reading number of pages from the pdf file
        numPages = self.pdfReader.numPages

        # Loop for reading all the Pages
        for page in range(numPages):
            # Creating a page object
            pageObj = self.pdfReader.getPage(page)
            # Extracting text from page

            self.pages = page+1
            # Converting from range to integer to know the current page number.

            page_text_str = pageObj.extractText()
            # Extracting text as string from pageObject.

            self.extracted_text_sort(page_text_str)

            self.find_headings_keys()

            # Applicable for page1
            if self.pages == 1:
                name,address,email=self.name_add_mail_values()

                self.find_values_pg_strt()
                self.find_values_pg_end()

            else:
                self.find_values_pg_end()
                self.find_values_pg_strt()

            self.values = [''.join([str(c) for c in lst]) for lst in self.values]
            # converting nest of lists to list

            final_dict=self.create_dict_name_addr(name,address,email)
            dict_heading_values = self.create_dict_values()

            # combining two dictionaries
            final_dict.update(dict_heading_values)
                        
            self.create_output_json(final_dict)


if __name__ == '__main__':
    convertPdfToJson()
