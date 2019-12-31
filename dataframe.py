import os

class PageRep:
    def __init__(self, 
    ownerParcelInfoItem,
    valueInfoItemList,
    saleTransferInfoItemList,
    pageUrl
    ):
        self.OwnerParcelInfo = ownerParcelInfoItem
        self.ValueInfoItemList = valueInfoItemList
        self.SaleTransferInfoList = saleTransferInfoItemList
        self.PageUrl = pageUrl

    def WriteOut(
        self,
        ownerParcelPath="OwnerParcelInfo.csv",
        valueInfoPath = "ValueInfo.csv",
        saleInfoPath = "SaleInfo.csv"
    ):
        # Prepare parcel file
        if not os.path.exists(ownerParcelPath):
            with open(ownerParcelPath, "w") as f:
                f.write(OwnerParcelInfoItem.ToCsvHeader())

        # Write parcel info
        with open(ownerParcelPath, "a") as f:
            f.write(self.OwnerParcelInfo.ToCsvString())

        # Prepare value file
        if not os.path.exists(valueInfoPath):
            with open(valueInfoPath, "w") as f:
                f.write("Address," + ValueInfoItem.ToCsvHeader())
        
        # Write value info
        with open(valueInfoPath, "a") as f:
            for v in self.ValueInfoItemList:
                f.write("{0},{1}".format(Helper.ToSafeCellContent(self.OwnerParcelInfo.MailingAddress), v.ToCsvString()))
        
        # Prepare sales file
        if not os.path.exists(saleInfoPath):
            with open(saleInfoPath, "a") as f:
                f.write("Address," + SaleTransferInfoItem.ToCsvHeader())

        # Write sales info
        with open(saleInfoPath, "a") as f:
            for v in self.SaleTransferInfoList:
                f.write("{0},{1}".format(Helper.ToSafeCellContent(self.OwnerParcelInfo.MailingAddress), v.ToCsvString()))

        



class OwnerParcelInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)

    @staticmethod
    def ToCsvHeader():
        string = ""
        string += "{0},".format("Owner Name")
        string += "{0},".format("Mailing Address")
        string += "{0},".format("Location Address")
        string += "{0},".format("Property Class")
        string += "{0},".format("Zoning District")
        string += "{0},".format("Square")
        string += "{0},".format("Book")
        string += "{0},".format("Line")
        string += "{0},".format("Legal Description")
        string += "{0},".format("Today's Date")
        string += "{0},".format("Municipal District")
        string += "{0},".format("Tax Bill Number")
        string += "{0},".format("Special Tax District")
        string += "{0},".format("Special Task District Map")
        string += "{0},".format("Land Area (sq ft)")
        string += "{0},".format("Building Area (sq ft)")
        string += "{0},".format("Revised Building Area (sq ft)")
        string += "{0},".format("Lot / Folio")
        string += "{0},".format("Assessment Area")
        string += "{0},".format("Parcel Map")
        string += "{0},".format("Assessment Area Map")
        string += "{0},".format("url")
        string += "\n"
        return string

    def FromDict(self, d):
        self.OwnerName = d["OwnerName"]
        self.MailingAddress = d["MailingAddress"]
        self.LocationAddress = d["LocationAddress"]
        self.PropertyClass = d["PropertyClass"]
        self.SubdivisionName = d["SubdivisionName"]
        self.ZoningDistrict = d["ZoningDistrict"]
        self.Square = d["Square"]
        self.Book = d["Book"]
        self.Line = d["Line"]
        self.LegalDescription = d["LegalDescription"]
        self.TodaysDate = d["Today'sDate"]
        self.MunicipalDistrict = d["MunicipalDistrict"]
        self.TaxBillNumber = d["TaxBillNumber"]
        self.SpecialTaxDistrict = d["SpecialTaxDistrict"]
        
        # Download special tax district map later
        self.SpecialTaxDistrictMap = ""

        self.LandAreaSF = d["LandArea(sqft)"]
        self.BuildingAreaSF = d["BuildingArea(sqft)"]
        self.RevisedBuildingAreaSF = d["RevisedBldgArea(sqft)"]
        self.LotFolio = d["Lot/Folio"]
        self.AssessmentArea = d["AssessmentArea"]

        # Download parcel map
        self.ParcelMap = ""

        # Download Assesment Area
        self.AssessmentAreaMap = ""

        # Assign URI later
        self.URI = ""

    def ToCsvString(self):
        string = ""
        string += "{0},".format(Helper.ToSafeCellContent(self.OwnerName))
        string += "{0},".format(Helper.ToSafeCellContent(self.MailingAddress))
        string += "{0},".format(Helper.ToSafeCellContent(self.LocationAddress))
        string += "{0},".format(Helper.ToSafeCellContent(self.PropertyClass))
        string += "{0},".format(Helper.ToSafeCellContent(self.ZoningDistrict))
        string += "{0},".format(Helper.ToSafeCellContent(self.Square))
        string += "{0},".format(Helper.ToSafeCellContent(self.Book))
        string += "{0},".format(Helper.ToSafeCellContent(self.Line))
        string += "{0},".format(Helper.ToSafeCellContent(self.LegalDescription))
        string += "{0},".format(Helper.ToSafeCellContent(self.TodaysDate))
        string += "{0},".format(Helper.ToSafeCellContent(self.MunicipalDistrict))
        string += "{0},".format(Helper.ToSafeCellContent(self.TaxBillNumber))
        string += "{0},".format(Helper.ToSafeCellContent(self.SpecialTaxDistrict))
        string += "{0},".format(Helper.ToSafeCellContent(self.SpecialTaxDistrictMap))
        string += "{0},".format(Helper.ToSafeCellContent(self.LandAreaSF))
        string += "{0},".format(Helper.ToSafeCellContent(self.BuildingAreaSF))
        string += "{0},".format(Helper.ToSafeCellContent(self.RevisedBuildingAreaSF))
        string += "{0},".format(Helper.ToSafeCellContent(self.LotFolio))
        string += "{0},".format(Helper.ToSafeCellContent(self.AssessmentArea))
        string += "{0},".format(Helper.ToSafeCellContent(self.ParcelMap))
        string += "{0},".format(Helper.ToSafeCellContent(self.AssessmentAreaMap))
        string += "{0},".format(Helper.ToSafeCellContent(self.URI))
        string += "\n"
        return string

    def ToSafeCellContent(self, string):
        if "," not in string:
            return string
        else:
            return "\"{0}\"".format(string)





class ValueInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)

    @staticmethod
    def ToCsvHeader():
        string = ""
        string += "{0},".format("Year")
        string += "{0},".format("Land Value")
        string += "{0},".format("Building Value")
        string += "{0},".format("Total Value")
        string += "{0},".format("Assessed Land Value")
        string += "{0},".format("Assessed Building Value")
        string += "{0},".format("Total Assessed Value")
        string += "{0},".format("Homestead Exemption Value")
        string += "{0},".format("Taxable Assessment")
        string += "{0},".format("Age Freeze")
        string += "{0},".format("Disability Freeze")
        string += "{0},".format("Assmnt Change")
        string += "{0},".format("Tax Contract")
        string += "\n"
        return string

    def FromDict(self, d):
        self.Year = d["Year"]
        self.LandValue = d["LandValue"]
        self.BuildingValue = d["BuildingValue"]
        self.TotalValue = d["TotalValue"]
        self.AssessedLandValue = d["AssessedLandValue"]
        self.AssessedBuildingValue = d["AssessedBuildingValue"]
        self.TotalAssessedValue = d["TotalAssessedValue"]
        self.HomesteadExemptionValue = d["HomesteadExemptionValue"]
        self.TaxableAssessmentValue = d["TaxableAssessment"]
        self.AgeFreeze = d["AgeFreeze"]
        self.DisabilityFreeze = d["DisabilityFreeze"]
        self.AssmntChange = d["AssmntChange"]
        self.TaxContract = d["TaxContract"]

    def ToCsvString(self):
        string = ""
        string += "{0},".format(Helper.ToSafeCellContent(self.Year))
        string += "{0},".format(Helper.ToSafeCellContent(self.LandValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.BuildingValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.TotalValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.AssessedLandValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.AssessedBuildingValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.TotalAssessedValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.HomesteadExemptionValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.TaxableAssessmentValue))
        string += "{0},".format(Helper.ToSafeCellContent(self.AgeFreeze))
        string += "{0},".format(Helper.ToSafeCellContent(self.DisabilityFreeze))
        string += "{0},".format(Helper.ToSafeCellContent(self.AssmntChange))
        string += "{0},".format(Helper.ToSafeCellContent(self.TaxContract))
        string += "\n"
        return string

class SaleTransferInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)

    @staticmethod
    def ToCsvHeader():
        string = ""
        string += "{0},".format("Sale / TransferDate")
        string += "{0},".format("Price")
        string += "{0},".format("Grantor")
        string += "{0},".format("Grantee")
        string += "{0},".format("Notarial Archive Number")
        string += "{0},".format("Instrument Number")
        string += "\n"
        return string

    def FromDict(self, d):
        self.SaleTransferDate = d["Sale/TransferDate"]
        self.Price = d["Price"]
        self.Grantor = d["Grantor"]
        self.Grantee = d["Grantee"]
        self.NotarialArchiveNumber = d["NotarialArchiveNumber"]
        self.InstrumentNumber = d["InstrumentNumber"]

    def ToCsvString(self):
        string = ""
        string += "{0},".format(Helper.ToSafeCellContent(self.SaleTransferDate))
        string += "{0},".format(Helper.ToSafeCellContent(self.Price))
        string += "{0},".format(Helper.ToSafeCellContent(self.Grantor))
        string += "{0},".format(Helper.ToSafeCellContent(self.Grantee))
        string += "{0},".format(Helper.ToSafeCellContent(self.NotarialArchiveNumber))
        string += "{0},".format(Helper.ToSafeCellContent(self.InstrumentNumber))
        string += "\n"
        return string

class Helper:
    def __init__(self):
        pass

    @staticmethod
    def ToSafeCellContent(string):
        string = string.replace("\n", " ")
        if "," not in string:
            return string
        else:
            return "\"{0}\"".format(string)





