class PageSection:
    def __init__(self):
        self.pets  = "/pets"
        self.recoveryItems = "/items/Recovery"
        self.statusItems = "/items/Status"
        self.itemTypes = ["Items","Ores", "Collectibles", "Special", "Swords", "Claws", "Canes", "Rod", "Armor", "Bows", "Throwing", "Additional", "Crystas", "AlCrystas", "RelicCrystas"]

    def itemSection(self, itemName):
        return "/item/%s" % itemName
    
    def querySection(self, query):
        return "/search?search=%s" % query

    def skillSection(self, job):
        return "/skills/%s" % job