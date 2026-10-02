from bs4 import BeautifulSoup
import requests
import json
import re
import time

# Going to do some re ordering of this to get the poems by the "date" they were originally created
def get_poems_date(soup):
    dates = soup.css.select('tr > td.tdc > b > big')
    dates_set = {}

    for date in dates:
        # dates_set[date] = date.sourceline
        print(date.sourceline)
    
    


# RETURNS A LIST OF POEM DIVS
# BASED ON DIV.POEM (GUTENBERG)
def get_poems(soup):
    poems = []
    for div in soup.find_all('div', 'poem'):  # get poems
        schema_check = div.find('div', 'poem')
        if schema_check:
            continue
        poems.append(div)
        # print(poems)
        # if div.find('b'):
        #     print(div.find('b').get_text())
    return poems

# /[A-Za-z0-9]+,\s[0-9]{4}
# /[A-Za-z0-9]+,\s[0-9]{4}/gm


# RETURNS A LIST OF STANZAS 
# BASED ON DIV.POEM > DIV.STANZA (GUTENBERG)
def get_stanzas(poem):
    stanzas = poem.find_all('div', 'stanza')
    return stanzas if len(stanzas) > 1 else None

# RETURNS A FORMATTED LIST OF POEM_OBJS
# FROM DIV.POEM (GUTENBERG)
def build_poems(poems):
    poem_objs = []
    for poem in poems:
        poem_obj = build_poem(poem)
        if poem_obj == None:
            continue
        poem_objs.append(poem_obj)

    return poem_objs



# RETURNS A POEM_OBJ 
# FROM DIV.POEM (GUTENBERG)
def build_poem(poem):
    date = get_date(poem)

    all_stanzas = get_stanzas(poem)  # all div.stanza elements
    if not all_stanzas:
        return
    
    # OBTAINING POEM.DIV
    title_el = all_stanzas[0].css.select('span > b')
    poet_el = all_stanzas[len(all_stanzas) - 1].css.select_one('span > i')

    if not title_el:
        return  None # may throw an error here 
    
    if not poet_el:
        return None
    

    # EXTRACTING TITLE AND POET TEXT
    title = title_el[0].get_text()
    poet = poet_el.get_text()
    

    # ACCESSING ASSUMED POEM BODY
    body = all_stanzas[1:len(all_stanzas)-1]

    stanzas = []


    # ITERATING OVER DIV.STANZA AND STORING IT'S
    # CHILD SPAN'S STRINGS OF TEXT
    for stanza in body:
        stanza_spans = stanza.find_all('span')
        stanza_text = extract_text(stanza_spans)
        if None in stanza_text:
            return 
        
        stanzas.append(stanza_text)

    if len(stanzas) < 1:
        return None


    # STORING "CLEANED" DATA IN POEM OBJECT
    poem_obj = {
        "title": title,
        "poet": poet,
        "stanzas": stanzas,
        "source": "Poetry",
        "date_published": date.strip()
    }

    return poem_obj



# RETURNS EXTRACTED TEXT FROM A LIST OF ELEMENTS
def extract_text(els):
    stanza_text = []
    for el in els:
        text = el.get_text()
        if not text:
            return None
        stanza_text.append(text)

    return stanza_text

# GETS POEM'S DATE
def get_date(poem):
    print('Get date function')

    prev_date = poem.find_previous('td', class_='tdc')
    date = ''
    while date == '' and prev_date:
        date_tag = prev_date.css.select_one('b > big')
        if date_tag != None:
            date = date_tag.text
        else:
            prev_date = prev_date.find_previous('td', class_='tdc')

    return date
    

resposne = requests.get('https://www.gutenberg.org/files/43224/43224-h/43224-h.htm')
resposne.encoding = "utf-8"
html_data = resposne.text

soup = BeautifulSoup(html_data, 'html.parser')

# with open('source.html', 'w', encoding='utf-8') as f:
#     f.write(soup.prettify())

# get_poems_date(soup)

poems = get_poems(soup)
# print(poems[0], '--')

# # print(poems)
poem_objs = build_poems(poems)

# print(poem_objs[-1])


with open("ouput__.json", "w", encoding='utf-8') as outfile:
    json.dump(poem_objs, outfile, ensure_ascii=False, indent=4)

# with open("ouput.json", "r") as infile:
#     poem_objs = json.load(infile)

# # print(len(poem_objs))
# def main():
#     """Main execution logic"""
#     # result = get_freq()
#     # print(result)

# if __name__ == "__main__":
#     print("Running scraper directly...")
   

# _wait = 0.5

# def get_freq(term):
#     response = None
#     while True:
#         try:
#             response = requests.get('https://api.datamuse.com/words?sp='+term+'&md=f&max=1').json()
#         except:
#             print('Could not get response. Sleep and retry...')
#             time.sleep(_wait)
#             continue
#         break
#     freq = 0.0 if len(response)==0 else float(response[0]['tags'][0][2:])
#     return freq

# a = ['a', 'and', 'bough', 'spectacular', 'arduous', 'strident', 'Wrought', 'perilous', 'mood', 'deathward', 'weeping', 'flag-stones', 'heaven', 'cataract', 'clarionet', 'marvellous', 'swoon',
#     'reiterate', 'Olivia', 'unalterable', 'cessation', 'clefts', 'Quivered']

# for i in a:

#     print(i, get_freq(i))