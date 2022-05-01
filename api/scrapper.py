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
    
    def GetItemContent(self, item):
        anchor = item.find("a")
        divDesc= item.find("div", { "class": "ds"})
        name = anchor.text.strip()
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
        itemContent = page.find('div', { 'class': "default_attr" })
        itemInfo = self.GetItemContent(itemContent)
        sections = self.GetAllSections(page)
        itemInfo["more"] = sections 
        ## Searching item images
        itemImage = page.find('div', { 'id': 'item_images'})
        if itemImage and itemImage is not None:
            img = itemImage.find("img")
            if img:
                name = img["alt"].replace('item_image_','').strip()
                src = img["src"]
                itemInfo["img"] = { 'name': name, 'src': src }        
        return itemInfo
    
    def GetMonsterInfo(self, monsterContainer):
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
    
    def GetBlacksmithInfo(self, blackContainer):
        items = []
        currentItem = {}
        materials   = []
        for row in blackContainer:
            text = row.text.replace('\n','')
            if row == None or row.name == "br" or ":" in text or (row.name == None and text == ''):
                continue
            if row.name and row.name == "b" and not currentItem.get("name"):
                currentItem["name"] = text
                continue

            if row.name == "a" and "x" in text:
                materials.append(text)
                continue

            if row.name == "a" and "x" not in text:
                currentItem["materials"] = materials
                currentItem["city"] = text
                items.append(json.dumps(currentItem))
                currentItem.clear()
                materials.clear()
        return items
    
    def GetProductionInfo(self, container):
        items =[]; currentItem = {}; materials = []
        lastIndex = len(container) - 1
        for index, row in enumerate(list(container)):
            if row is None: 
                continue

            if row.name == "b" and not currentItem.get("name"):
                currentItem["name"] = row.text.strip()  
                continue

            if row.name is None and "Lv" in row.text:
                currentItem["lvRequired"] = row.text.strip()
                continue

            if row.name == "a":
                order = len(materials) +1
                materials.append("%d : %s" %(order, row.text))
                continue
            ## termino de buscar materiales
            if (row.name == "b" and currentItem.get("name")) or lastIndex == index:
                currentItem["materials"] = materials
                items.append(json.dumps(currentItem))
                currentItem.clear()
                materials.clear()
                ## Set the new item name.
                currentItem["name"] = row.text.strip()
                continue

        return items



    def GetAllSections(self, container):
        sections = container.find_all('div', { 'class': 'row'})
        result = {}
        for section in sections:
            title = section.find("b")
            if not title:
                continue
            sectionInfo = section.find_next_siblings('div')[0]
            if title.text == "Monsters":
                temp = self.GetMonsterInfo(sectionInfo)
                result["Monsters"] = list(map(json.loads, temp))
                continue 

            if title.text == "Blacksmith":
                temp = self.GetBlacksmithInfo(sectionInfo)
                result["Blacksmith"] = list(map(json.loads, temp))
                continue 

            if title.text == "Production":
                temp = self.GetProductionInfo(sectionInfo)
                result["Production"] = list(map(json.loads, temp))
                continue

            if title.text == "Materials":
                temp = self.GetProductionInfo(sectionInfo)
                result["Materials"] = list(map(json.loads, temp))
                continue      
        return result