from selenium import webdriver
from dataframe import *
import os
import unicodedata
import re
from pprint import pprint
import urllib3

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
        imagesPath = os.path.join(pagePath, "Images")
        if not os.path.exists(imagesPath):
            os.mkdir(imagesPath)

        # Get downloadable links
        imageUri, specialTaxDistrictMapUri, parcelMapUri, AssessmentAreaMapUri, nextUri = self.GetHyperlinks()

        # Download files
        taxDistrMapPath = os.path.join(pagePath, "SpecialTaxDistrictMap.pdf")
        self.DownloadFile(specialTaxDistrictMapUri, taxDistrMapPath)
        ownerParcelInfo.SpecialTaxDistrictMap = taxDistrMapPath

        parcelMapPath = os.path.join(pagePath, "ParcelMap.pdf")
        self.DownloadFile(parcelMapUri, parcelMapPath)
        ownerParcelInfo.ParcelMap = parcelMapPath
        
        assmntAreaPath = os.path.join(pagePath, "AssessmentAreaMap.pdf")
        self.DownloadFile(AssessmentAreaMapUri, assmntAreaPath)
        ownerParcelInfo.AssessmentAreaMap = assmntAreaPath

        # Download Images
        self.DownloadImages(imageUri, imagesPath)
        ownerParcelInfo.ImageUrl = imageUri

        # Create Page Rep
        rep = PageRep(ownerParcelInfo, valueObjects, salesObjects, url)
        self.Pages[rep.OwnerParcelInfo.MailingAddress] = rep
        rep.WriteOut()
        print(address, ": successfully written to disk")

    def DownloadImages(self, imagesUri, folder):
        self.Driver.get(imagesUri)
        images = self.Driver.find_elements_by_tag_name("img")
        counter = 0
        for img in images:
            src = img.get_attribute("src")
            if src != "http://qpublic9.qpublic.net/images/la_orleans.jpg":
                self.DownloadFile(src, os.path.join(folder, "img_{0}.jpg".format(counter)))
                counter += 1

    
    def GetHyperlinks(self):
        imageLink = self.Driver.find_element_by_link_text("Enlarge/Show All")
        imageUri = imageLink.get_attribute('href')

        nextLink = self.Driver.find_element_by_link_text("Next Parcel")
        nextUri = nextLink.get_attribute('href')

        specialTaxDistrictMapUri = None
        parcelMapUri = None
        AssessmentAreaMapUri = None

        hyperLinks = self.Driver.find_elements_by_tag_name("a")
        for h in hyperLinks:
            href = h.get_attribute('href')
            try:
                img = h.find_element_by_tag_name("img")

                if img.get_attribute("src") == "http://qpublic9.qpublic.net/images/special_tax_district_map.gif":
                    specialTaxDistrictMapUri = href
                elif img.get_attribute("src") == "http://qpublic9.qpublic.net/images/spm.gif":
                    parcelMapUri = href
                elif img.get_attribute("src") == "http://qpublic9.qpublic.net/images/saa.gif":
                    AssessmentAreaMapUri = href
            except:
                pass

        
        return imageUri, specialTaxDistrictMapUri, parcelMapUri, AssessmentAreaMapUri, nextUri

    def DownloadFile(self, url, path, chunk_size=1024):
        http = urllib3.PoolManager()
        r = http.request('GET', url, preload_content=False)

        with open(path, 'wb') as out:
            while True:
                data = r.read(chunk_size)
                if not data:
                    break
                out.write(data)

        r.release_conn()


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
