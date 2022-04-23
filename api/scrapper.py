import requests
from bs4 import BeautifulSoup
from .pageSections import PageSection

class Scrapper:
    def __init__(self):
        self.baseUrl="http://www.iruna-online.info/"
        self.errorCodes = [ 500,400,403]
        self.sections = PageSection()

    def GetContentBySection(self, sectionName=""):
        """
            Obtiene un contenido basandose en la ruta completa.
        """
        try:
            response = requests.get(self.baseUrl + sectionName);
            if response is not None and response.status_code not in self.errorCodes:
                return BeautifulSoup(response.content, 'html.parser')
            return None
        except:
            print("No page found") 
            return None
    
    def GetRecoveryItems(self):
        content = self.GetContentBySection(self.sections.recoveryItems)
        if content is None:
            return []
        
        items = content.findAll('div', {'class':'Recovery'})
        result=[]
        replaceText = "[Recovery]"
        for item in items:
            basic    = item.find("a")
            descItem = item.find("div", {"class": "ds"})
            name =""
            desc =""
            href=""
            if basic:
                name = basic.text.replace(replaceText, "").strip()
                href = basic["href"]
            if descItem:
                desc = descItem.text
            result.append({ "name" : name, "description": desc, "uri": href })
        return result

    def GetPets(self):
        petContent = self.GetContentBySection(self.sections.pets)
        if petContent is None:
            return []

        table = petContent.find('table', { 'class': 'table table-condensed table-bordered table-responsive' })
        rows = table.findAll('tr')
        title = "Pet Skill"
        result = []
        for row in rows:
            tItem = row.find('th')
            if tItem is not None:
                title = tItem.text
            
            skill = row.find('td')
            if skill is not None:
                result.append(skill.text)
            
        return { title : result }
    
    def GetFullItem(self, itemName):
        page = self.GetContentBySection(self.sections.itemSection(itemName))
        if page is None:
            return []
        itemContent = page.find('div', { 'class': "default_attr" })