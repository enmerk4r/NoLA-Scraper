from selenium import webdriver
from dataframe import *
import os
import unicodedata
import re
from pprint import pprint
import urllib3
import time
import datetime
import uuid
from selenium.common.exceptions import UnexpectedAlertPresentException

class Scraper:
    def __init__(self, 
    imgFolder="downloads", 
    downloadFiles=True,
    goToNextParcel=True,
    entryLimit = None,
    stopWhenDuplicate=False):
        self.Pages = {}
        self.Driver = webdriver.Chrome()
        self.ImageFolder = imgFolder
        self.GoToNextParcel = goToNextParcel
        self.EntryLimit = entryLimit
        if not os.path.exists(imgFolder) and downloadFiles:
            os.makedirs(imgFolder)
        self.parsedUrls = []
        self.StopWhenDuplicate = stopWhenDuplicate

    def ReadWebPage(self, url):
        try:
            if (url in self.parsedUrls):
                print("DUPLICATE! Skipping record")
                if self.StopWhenDuplicate:
                    print("**** REACHED STOP CONDITION ****")
                    return
                imageUri, specialTaxDistrictMapUri, parcelMapUri, AssessmentAreaMapUri, nextUri, zoningLink = self.GetHyperlinks()
            else:
                pageGuid = str(uuid.uuid4())
                print("============================")
                print("Parsing page: {0}".format(len(self.Pages) + 1))
                print("============================")
                self.Driver.get(url)
                ownerParcelInfo = self.ParseOwnerParcelInfo()
                ownerParcelInfo.URI = url

                address = self.slugify(ownerParcelInfo.MailingAddress)

                print(address, ": parsed owner / parcel data")

                valueObjects = self.ParseValueInfo()
                print(address, ": parsed {0} value records".format(len(valueObjects)))

                salesObjects = self.ParseSalesInfo()
                print(address, ": parsed {0} sales records".format(len(salesObjects)))

                # Create address path
                addressPath = os.path.join(self.ImageFolder, address)
                if not os.path.exists(addressPath):
                    os.mkdir(addressPath)

                # Create page path
                pagePath = os.path.join(addressPath, pageGuid)
                if not os.path.exists(pagePath):
                    os.mkdir(pagePath)
                
                # Create image path
                imagesPath = os.path.join(pagePath, "Images")
                if not os.path.exists(imagesPath):
                    os.mkdir(imagesPath)

                # Create sketch path
                sketchPath = os.path.join(pagePath, "Sketches")
                if not os.path.exists(sketchPath):
                    os.mkdir(sketchPath)

                # Download Sketches
                if self.DownloadImages:
                    numSketches = 0
                    numSketches += self.DownloadSketch(sketchPath)
                    print(address, ": downloaded {0} sketch(es)".format(numSketches))

                # Get downloadable links
                imageUri, specialTaxDistrictMapUri, parcelMapUri, AssessmentAreaMapUri, nextUri, zoningLink = self.GetHyperlinks()
                ownerParcelInfo.SpecialTaxDistrictMap = specialTaxDistrictMapUri
                ownerParcelInfo.ParcelMap = parcelMapUri
                ownerParcelInfo.AssessmentAreaMap = AssessmentAreaMapUri
                ownerParcelInfo.ImageUrl = imageUri

                # Parse zoning data
                if zoningLink != None:
                    try:
                        self.Driver.get(zoningLink)
                        zoningInfo = self.ParseZoningInfo(pagePath)
                        ownerParcelInfo.ZoningDistrict = zoningInfo.ZoningDistrict
                        ownerParcelInfo.ZoningDescription = zoningInfo.ZoningDescription
                    except:
                        ownerParcelInfo.ZoningDistrict = ""
                        ownerParcelInfo.ZoningDescription = ""


                if self.DownloadImages:
                    # Download files
                    numFiles = 0
                    
                    if specialTaxDistrictMapUri is not None:
                        taxDistrMapPath = os.path.join(pagePath, "SpecialTaxDistrictMap.pdf")
                        self.DownloadFile(specialTaxDistrictMapUri, taxDistrMapPath)
                        numFiles += 1
                    
                    if parcelMapUri is not None:
                        parcelMapPath = os.path.join(pagePath, "ParcelMap.pdf")
                        self.DownloadFile(parcelMapUri, parcelMapPath)
                        numFiles += 1
                    
                    if AssessmentAreaMapUri is not None:
                        assmntAreaPath = os.path.join(pagePath, "AssessmentAreaMap.pdf")
                        self.DownloadFile(AssessmentAreaMapUri, assmntAreaPath)
                        numFiles += 1
                    
                    


                    print(address, ": downloaded {0} PDF file(s)".format(numFiles))
                    

                    # Download Images
                    if imageUri is not None:
                        numImgs = self.DownloadImages(imageUri, imagesPath)
                        print(address, ": downloaded {0} image(s)".format(numImgs))

                # Create Page Rep
                rep = PageRep(ownerParcelInfo, valueObjects, salesObjects, url)
                rep.Guid = pageGuid
                self.parsedUrls.append(url)
                self.Pages[rep.Guid] = rep
                rep.WriteOut()
                print(address, ": successfully written to disk")

            # Next Page
            if (self.GoToNextParcel):
                if (self.EntryLimit == None or len(self.Pages) < self.EntryLimit):
                    self.ReadWebPage(nextUri)
                elif len(self.Pages) >= self.EntryLimit:
                    print("**** REACHED ENTRY LIMIT ****")
        except UnexpectedAlertPresentException as exception:
            alert_obj = self.Driver.switch_to.alert
            alert_obj.accept()
            self.ReadWebPage(url)


    def DownloadSketch(self, sketchPath):
        try:
            tds = self.Driver.find_element_by_class_name("sketch_main")
            image = tds.find_element_by_tag_name("img")
            source = image.get_attribute("src")
            self.DownloadFile(source, os.path.join(sketchPath, "MainSketch.jpg"))
            return 1
        except:
            return 0

    def DownloadImages(self, imagesUri, folder):
        try:
            self.Driver.get(imagesUri)
            images = self.Driver.find_elements_by_tag_name("img")
            counter = 0
            for img in images:
                src = img.get_attribute("src")
                if src != "http://qpublic9.qpublic.net/images/la_orleans.jpg":
                    self.DownloadFile(src, os.path.join(folder, "img_{0}.jpg".format(counter)))
                    counter += 1
            
            return counter
        except:
            return 0

    
    def GetHyperlinks(self):
        try:
            imageLink = self.Driver.find_element_by_link_text("Enlarge/Show All")
            imageUri = imageLink.get_attribute('href')
        except:
            imageUri = None

        nextLink = self.Driver.find_element_by_link_text("Next Parcel")
        nextUri = nextLink.get_attribute('href')

        specialTaxDistrictMapUri = None
        parcelMapUri = None
        AssessmentAreaMapUri = None
        ZoningLink = None

        hyperLinks = self.Driver.find_elements_by_tag_name("a")
        for h in hyperLinks:
            href = h.get_attribute('href')
            if "Show Viewer" in h.text:
                    ZoningLink = href
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

        
        return imageUri, specialTaxDistrictMapUri, parcelMapUri, AssessmentAreaMapUri, nextUri, ZoningLink

    def DownloadFile(self, url, path, chunk_size=1024):
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', url, preload_content=False)

            with open(path, 'wb') as out:
                while True:
                    data = r.read(chunk_size)
                    if not data:
                        break
                    out.write(data)

            r.release_conn()
        except:
            pass
    
    def ParseZoningInfo(self, path):
        # Make sure the map loads fully
        print("Waiting for the map to load...")
        try:
            WaitStart = datetime.datetime.now()
            WAIT_LIMIT = 60
            fullyLoaded = False
            while not fullyLoaded:
                try:
                    lines = self.Driver.find_elements_by_tag_name("td")
                    for td in lines:
                        try:
                            b = td.find_element_by_tag_name("b")
                            head = b.text
                            if "Zoning District:" in head or "Future Land Use:" in head:
                                print("Page fully loaded")
                                time.sleep(0.5)
                                fullyLoaded = True
                                break
                        except:
                            pass
                except:
                    time.sleep(1)

                # Make sure we're not stuck
                difference = datetime.datetime.now() - WaitStart
                if difference.seconds > WAIT_LIMIT:
                    fullyLoaded = True

            all_lines = self.Driver.find_elements_by_tag_name("td")
            zoning_dict = {}

            for td in all_lines:
                try:
                    b = td.find_element_by_tag_name("b")
                    head = b.text
                    value = td.text
                    clean = head.replace(" ", "").replace("\n", "")
                    if clean not in zoning_dict:
                        zoning_dict[clean] = value
                except:
                    pass

            # Save screenshot
            self.Driver.save_screenshot(os.path.join(path, "zoning.png"))

            zoningInfo = ZoningInfoItem(zoning_dict)
            return zoningInfo
        except UnexpectedAlertPresentException as exception:
            return None


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
