class PageSection:
    def __init__(self):
        self.pets  = "/pets"
        self.recoveryItems = "/items/Recovery"
        self.statusItems = "/items/Status"
    def itemSection(self, itemName):
        return "/item/%s" % itemName