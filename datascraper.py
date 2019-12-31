from selenium import webdriver
from dataframe import *
import os
import unicodedata
import re
from pprint import pprint

class Scraper:
    def __init__(self, 
    imgFolder="downloads", 
    downloadFiles=True):
        self.Pages = {}
        self.Driver = webdriver.Chrome()
        self.ImageFolder = imgFolder
        if not os.path.exists(imgFolder) and downloadFiles:
            os.makedirs(imgFolder)

    def ReadWebPage(self, url):
        self.Driver.get(url)
        ownerParcelInfo = self.ParseOwnerParcelInfo()
        ownerParcelInfo.URI = url

        address = self.slugify(ownerParcelInfo.MailingAddress)
        print(address, ": parsed owner / parcel data")

        valueObjects = self.ParseValueInfo()
        print(address, ": parsed {0} value records".format(len(valueObjects)))

        salesObjects = self.ParseSalesInfo()
        print(address, ": parsed {0} sales records".format(len(salesObjects)))

        # Create page path
        pagePath = os.path.join(self.ImageFolder, address)
        if not os.path.exists(pagePath):
            os.mkdir(pagePath)
        
        #Create image path

        # Create Page Rep
        rep = PageRep(ownerParcelInfo, valueObjects, salesObjects, url)
        self.Pages[rep.OwnerParcelInfo.MailingAddress] = rep
        rep.WriteOut()
        print(address, ": successfully written to disk".format(len(salesObjects)))

    def ParseOwnerParcelInfo(self):
        owner_headers = self.Driver.find_elements_by_class_name("owner_header")
        owner_values = self.Driver.find_elements_by_class_name("owner_value")
        owner_parcel_value_dict = {}
        for h, v in zip(owner_headers, owner_values):
            owner_parcel_value_dict[h.text.replace(" ", "")] = v.text

        # Create an Owner / Parcel info object
        ownerParcelInfo = OwnerParcelInfoItem(owner_parcel_value_dict)

        return ownerParcelInfo

    def ParseValueInfo(self):
        tax_headers = self.Driver.find_elements_by_class_name("tax_header")
        tax_values = self.Driver.find_elements_by_class_name("tax_value")
        numColumns = len(tax_headers)
        value_partition = self.PartitionList(tax_values, numColumns)
        valueObjects = []
        for line in value_partition:
            line_dict = {}
            for h, v in zip(tax_headers, line):
                line_dict[h.text.replace("\n", "").replace(" ", "")] = v.text
            valueInfo = ValueInfoItem(line_dict)
            valueObjects.append(valueInfo)
        return valueObjects

    def ParseSalesInfo(self):
        sales_headers = self.Driver.find_elements_by_class_name("sales_header")
        sales_values = self.Driver.find_elements_by_class_name("sales_value")
        numColumns = len(sales_headers)
        value_partition = self.PartitionList(sales_values, numColumns)
        salesObjects = []
        for line in value_partition:
            line_dict = {}
            for h, v in zip(sales_headers, line):
                line_dict[h.text.replace("\n", "").replace(" ", "")] = v.text
            salesInfo = SaleTransferInfoItem(line_dict)
            salesObjects.append(salesInfo)
        return salesObjects
        
    def PartitionList(self, lst, length):
        newList = []
        buffer = []
        for elem in lst:
            if (len(buffer) < length):
                buffer.append(elem)
            else:
                newList.append(buffer)
                buffer = []
                buffer.append(elem)

        # Last leftover chunk
        if len(buffer) == length:
            newList.append(buffer)
        return newList
    
    def slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        return value
