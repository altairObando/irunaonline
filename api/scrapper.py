import enum
import json
from unittest import result
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
            if response is not None:
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
        atk = 0
        defe= 0
        notes=''
        if divDesc is not None:
            desc = divDesc.text.strip()
        for s in item:
            rowName = s.text.strip()[0:4]
            if s.text and 'ATK:' in rowName:
                sp = s.text.replace('ATK:','').strip().split(' ') #'92 DEF: 2'
                value= sp[0]
                atk = value
                if 'DEF:' in " ".join(sp):
                    defe = sp[2]
                continue
            if s.text and 'DEF:' in rowName:
                defe = s.text.strip().replace('DEF:','').strip()
            if s.text and 'Notes:' in s.text.strip():
                notes = s.text.replace('Notes: ?','').strip()
            
        return { "name" : name, "description": desc, "uri": href, "atk": atk,'def': defe, 'notes' : notes }

    def GetRecoveryItems(self, section):
        content = self.GetContentBySection("/items/%s" % section)
        if content is None:
            return []
        
        items = content.findAll('div', {'class': section})
        result=[]
        for item in items:
            i = self.GetItemContent(item)
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
        if itemContent is None:
            return []

        itemInfo = self.GetItemContent(itemContent)
        ## Searching item images
        itemImage = page.find('div', { 'id': 'item_images'})
        if itemImage and itemImage is not None:
            img = itemImage.find("img")
            if img:
                name = img["alt"].replace('item_image_','').strip()
                src = img["src"]
                itemInfo["img"] = { 'name': name, 'src': src } 
        #Search references
        sections = self.GetAllSections(page)
        itemInfo["more"] = sections        
        return itemInfo
    
    def GetMonsterInfo(self, monsterContainer):
        monsters = []; current = {}; attr  = []; Weak=[]; drops = []; zones = []
        settingDrops = False; allSeted = False; validNotNamedFields = ['\n\n\nDrop:\n', ]
        for row in monsterContainer:
            if not row.name and row.text not in validNotNamedFields and 'Attr' not in row.text and 'Weak' not in row.text:
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
                attr.append(row.text.replace('\n','').replace('Attr','').replace(':','').strip())
                continue

            if 'Weak' in row.text:
                Weak.append(row.text.replace('\n','').replace('Weak','').replace(':','').strip())
                continue
            
            if current.get('name') and row.name == 'a': ## drop Zone
                if 'See Map' in row.text:
                    allSeted = True
                else:
                    zones.append(row.text)
                continue
            
            if allSeted:
                current["drop"] = drops
                current['attr'] = attr
                current['weak'] = Weak
                current['zone'] = zones
                monsters.append(json.dumps(current))
                current.clear()
                drops.clear()
                attr.clear()
                Weak.clear()
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

    def GetSearchResult(self, query):
        page = self.GetContentBySection(self.sections.querySection(query))
        if page is None:
            return []

        optionResults = self.sections.itemTypes
        searchResults = {}
        for option in optionResults:
            sections = page.find_all('div', { 'class' : option })
            if option == "Monsters":
                sectionMonsters = page.find(lambda tag:tag.name =="b" and option in tag.text)
                if sectionMonsters:
                    monst  = sectionMonsters.parent.parent.find_next_siblings('div')[0]
                    result = self.GetMonsterInfo(monst)
                    searchResults[option] = list(map(json.loads, result))
                continue
            for section in sections:
                if searchResults.get(option) is None:
                    searchResults[option] = []
                current = {}; values = searchResults.get(option); last = len(section) - 1
                ## Validar Sin objetos
                if (last <= 0):
                    continue
                ## Tags
                if section.name == "div":
                    tags = section["class"]
                    tags.remove(option)
                    tags.remove("default_attr")
                    current["tags"] = tags
                    

                for index, row in enumerate(section):
                    if row.name == "b" and current.get("name") is None:
                        anchor = row.find("a")
                        if anchor and anchor is not None:
                            current["name"] = anchor.text
                            current["href"] = anchor["href"]
                        continue 

                    if ":" in row.text:
                        current["status"] = row.text.strip()
                        continue
                    
                    if row.name == "div" and "ds" in row["class"] :
                        current["description"] = row.text
                        continue
                    
                    if row.name == "div" and "t_ds" in row["class"]:
                        current["more"] = row.text
                        continue
                    
                    if index >= last:
                        values.append(json.loads(json.dumps(current)))
                        current.clear()
                        continue
                
                searchResults[option] = values
        
        return searchResults

    def GetSkills(self, job):
        page = self.GetContentBySection(self.sections.skillSection(job))
        results = []
        if page is None:
            return results
        
        sections = page.find_all('div', { 'class' : 'col-md-12' })
        if len(sections) <= 0:
            print("no results")
            return results

        currentSkill = {}
        currentSubSkill = []
        allSkills = []

        last = len(sections) -1
        for sectionIndex, section in enumerate(sections):
            for index, row in enumerate(section):
                if row.text == "" or row.text == "\n" or row and row.name == "b" and "Skill" in row.text.strip():
                    continue
                
                if row and row.name == "b": #Title/First skill tree
                    name = row.text.strip()[:(len(row.text.strip()) - 2)]
                    if currentSkill.get("name") is not None and name != currentSkill.get("name"): #Fin de la adicion
                        currentSkill["skills"] = currentSubSkill
                        allSkills.append(json.loads(json.dumps(currentSkill)))
                        currentSkill.clear()
                        currentSubSkill.clear()
                    currentSkill["name"] = name
                    continue

                if index == 4 and row.name is None and len(row.text.strip()) > 0: #descripcion
                    currentSkill["description"] = row.text.strip()
                    continue 

                if row.name == "a" and job not in row.text and "Item -" not in row.text:
                    subSkill = {}
                    subSkill["href"] = row["href"]
                    for sub in row:
                        if sub.name == "div":
                            subSkill["lvl"] = sub.text.strip()
                            continue
                        if sub.text.strip() is not None and sub.text.strip() != "":
                            subSkill["name"] = sub.text.strip()
                    if len(subSkill) > 1:
                        currentSubSkill.append(subSkill)
                    continue
                if "Item -" in row.text:
                    
                    subSkill = currentSubSkill[-1]
                    if subSkill is not None:
                        subSkill["item"] = row.text.strip().split(" - ")[1]
                    if row.name == "a":
                        subSkill["itemRef"] = row["href"]
                    continue
            
            if sectionIndex >= last:
                currentSkill["skills"] = currentSubSkill
                allSkills.append(json.loads(json.dumps(currentSkill)))
        

        return allSkills