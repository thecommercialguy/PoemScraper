from bs4 import BeautifulSoup
import requests

# RETURNS A LIST OF POEM DIV'S
# BASED OF DIV.POEM (GUTENBERG)
def get_poems():
    poems = []
    for div in soup.find_all('div', 'poem'):  # get poems
        poems.append(div)
        # if div.find('b'):
        #     print(div.find('b').get_text())
    return poems


# RETURNS A LIST OF STANZAS (GUTENBERG)
def get_stanzas():
    poems = get_poems()
    stanzas = []
    # print(poems[0])

    for poem in poems:

        stanzas.append(poem.find_all('div', 'stanza'))
        print(len(poem.find_all('div', 'stanza')))

    return stanzas

def build_poems(poems):

    for poem in poems:
        pass

def build_poem(poem):

    stanzas = get_stanzas(poem)

    pass

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


build_poems(poems)

soup.div
# get_poems()
get_title()








