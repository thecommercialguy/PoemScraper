from bs4 import BeautifulSoup
import requests
import json
import re

# RETURNS A LIST OF POEM DIVS
# BASED ON DIV.POEM (GUTENBERG)
def get_poems(soup):
    poems = []
    for div in soup.find_all('div', 'poem'):  # get poems
        schema_check = div.find('div', 'poem')
        if schema_check:
            continue
        poems.append(div)
        # if div.find('b'):
        #     print(div.find('b').get_text())
    return poems


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

    all_stanzas = get_stanzas(poem)  # all div.stanza elements
    if not all_stanzas:
        return
    
    # OBTAINING POEM.DIV
    title_el = all_stanzas[0].css.select('span > b')
    poet_el = all_stanzas[len(all_stanzas) - 1].css.select_one('span > i')

    # if len(title_el) > 1: 
    #     return None

    if not title_el:
        return  None # may throw an error here 
    
    if not poet_el:
        return None
    
    title = title_el[0].get_text()
    poet = poet_el.get_text()
    
    body = all_stanzas[1:len(all_stanzas)-1]

    stanzas = []

    for stanza in body:
        stanza_spans = stanza.find_all('span')
        stanza_text = extract_text(stanza_spans)
        if None in stanza_text:
            return 
        
        stanzas.append(stanza_text)

    if len(stanzas) < 1:
        return None



    poem_obj = {
        "title": title,
        "poet": poet,
        "stanzas": stanzas
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

# RETURNS A TITLE
def get_title():
    stanzas = get_stanzas()
    # print(len(stanzas))
    i = 0
    for stanza in stanzas:
        # i+=1
        if stanza[0].css.select('span > b'):
            i += 1

    # print(i)
    

    

resposne = requests.get('https://www.gutenberg.org/files/43224/43224-h/43224-h.htm')
html_data = resposne.text
# print(resposne.text)

soup = BeautifulSoup(html_data, 'html.parser')

poems = get_poems(soup)


poem_objs = build_poems(poems)

with open("ouput.json", "w") as outfile:
    json.dump(poem_objs, outfile, indent=4)
print(len(poem_objs))










