import json
import requests
from bs4 import BeautifulSoup
from .pageSections import PageSection

class Scrapper:
    def __init__(self):
        self.baseUrl="http://www.iruna-online.info"
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
    
    def GetItemContent(self, item, replaceText):
        anchor = item.find("a")
        divDesc= item.find("div", { "class": "ds"})
        name = anchor.text.replace(replaceText,"").strip()
        href = anchor['href']
        desc = ''
        if divDesc is not None:
            desc = divDesc.text
        return { "name" : name, "description": desc, "uri": href }

    def GetRecoveryItems(self):
        content = self.GetContentBySection(self.sections.recoveryItems)
        if content is None:
            return []
        
        items = content.findAll('div', {'class':'Recovery'})
        result=[]
        replaceText = "[Recovery]"
        for item in items:
            i = self.GetItemContent(item, replaceText)
            result.append(i)
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
        itemContent = page.find_all('div', { 'class': "default_attr" })
        replaceText = "[Recovery]"

        itemInfo = self.GetItemContent(itemContent, replaceText)
        # Drops from monsters section.
        dropContainer = itemContent.parent.find_next_siblings('div')[0]
        dropFromMonster = dropContainer.find("b")
        if dropFromMonster is not None and dropFromMonster.text == "Monsters":
            monsters = self.GetMonsterInfo(itemContent)
            itemInfo["monsters"] = list(map(json.loads, monsters))
        ## end Drop section
        itemContent.find("b")        
        return itemInfo
    
    def GetMonsterInfo(self, container):
        monsterContainer = container.parent.find_next_siblings('div')[1]
        monsters = []; current = {}; attr  = []; drops = []; zones = []
        settingDrops = False; allSeted = False; validNotNamedFields = ['\n\n\nDrop:\n', ]
        for row in monsterContainer:
            if not row.name and row.text not in validNotNamedFields and 'Attr' not in row.text:
                continue

            if not current.get('imgSrc') and row.name == "img":
                current['imgSrc'] = row['src']
                continue

            if not current.get('name') and row.name == 'b':
                name = row.find('a')
                current['name'] = name.text
                continue

            if row.text == '\n\n\nDrop:\n':
                drops = []
                settingDrops = True
                continue

            if settingDrops and row.name == 'a':
                mdrp = {}
                mdrp['href'] = row['href']
                mdrp['name'] = row.text
                drops.append(mdrp)
                continue

            if settingDrops and row.name == 'br':
                settingDrops = False
                continue

            if 'Attr' in row.text:
                attr.append(row.text.replace('\n\n','')[4:-1])
                continue
            
            if current.get('name') and row.name == 'a': ## drop Zone
                zones.append(row.text)
                if 'See Map' in row.text:
                    allSeted = True
                continue
            
            if allSeted:
                current["drop"] = drops
                current['attr'] = attr
                current['zone'] = zones
                monsters.append(json.dumps(current))
                current.clear()
                drops.clear()
                attr.clear()
                zones.clear()
                current = {}
                allSeted = False
                settingDrops = False
        
        return monsters

