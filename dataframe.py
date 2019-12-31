class PageRep:
    def __init__(self, 
    ownerParcelInfoItem,
    valueInfoItemList,
    saleTransferInfoItemList,
    imageLinks,
    pageUrl
    ):
        self.OwnerParcelInfo = ownerParcelInfoItem
        self.ValueInfoItemList = valueInfoItemList
        self.SaleTransferInfoList = saleTransferInfoItemList
        # download images
        self.PageUrl = pageUrl


class OwnerParcelInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)

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
        # Download special tax district map
        self.LandAreaSF = d["LandArea(sqft)"]
        self.BuildingAreaSF = d["BuildingArea(sqft)"]
        self.RevisedBuildingAreaSF = d["RevisedBldgArea(sqft)"]
        self.LotFolio = d["Lot/Folio"]
        # Download parcel map
        self.AssessmentArea = d["AssessmentArea"]
        # Download Assesment Area



class ValueInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)

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

class SaleTransferInfoItem:
    def __init__(self, dictionary):
        self.FromDict(dictionary)
        
    def FromDict(self, d):
        self.SaleTransferDate = d["Sale/TransferDate"]
        self.Price = d["Price"]
        self.Grantor = d["Grantor"]
        self.Grantee = d["Grantee"]
        self.NotarialArchiveNumber = d["NotarialArchiveNumber"]
        self.InstrumentNumber = d["InstrumentNumber"]






