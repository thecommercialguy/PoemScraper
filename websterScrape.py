import json
import time
import requests
from bs4 import BeautifulSoup
# from scraper import get_freq

# <div class="left-content col position-relative overflow-hidden" 
# id="left-content" data-word-click="enabled"> -- CONTAINER ENTRY
# ⬇️
# <div id="dictionary-entry-1" class="entry-word-section-container">  -- PER PART OF SPEECH
# ⬇️ ⬇️
#    <div class="row entry-header"> 
#    ⬇️ ⬇️
# ⬇️ ⬇️ <div class="entry-header-content d-flex flex-wrap align-items-baseline flex-row mb-0"> -- WORD CONTAINER
# ⬇️ ⬇️ ⬇️ ⬇️ 
# ⬇️ ⬇️ ⬇️ *<h1 class="hword">dog</h1> -- WORD
#    ⬇️ <h2 class="parts-of-speech"><a class="important-blue-link" href="/dictionary/noun">noun</a></h2> -- PART OF SPEECH
# <a class="play-pron-v2 text-decoration-none prons-entry-list-item d-inline badge mw-badge-gray-300" data-lang="en_us" data-file="dog00002" data-dir="d" href="https://www.merriam-webster.com/dictionary/dog?pronunciation&amp;lang=en_us&amp;dir=d&amp;file=dog00002" data-url="https://www.merriam-webster.com/dictionary/dog?pronunciation&amp;lang=en_us&amp;dir=d&amp;file=dog00002" title="How to pronounce dog (audio)">ˈdȯg&nbsp;<svg width="15" height="13" viewBox="0 0 15 13" fill="none" xmlns="http://www.w3.org/2000/svg" data-inject-url="https://www.merriam-webster.com/dist-cross-dungarees/2025-07-31--18-53-56-bbman/images/svg/audio-pron-redesign.svg" class="svg replaced-svg"><title>How to pronounce dog (audio)</title>
# <path fill-rule="evenodd" clip-rule="evenodd" d="M13.513 6.34363C13.513 4.21463 12.623 2.33405 10.7864 0.687267L11.4026 0C13.406 1.79629 14.436 3.91633 14.436 6.34363C14.436 8.77387 13.3787 10.9297 11.3318 12.7981L10.7095 12.1163C12.6005 10.3902 13.513 8.4697 13.513 6.34363ZM10.8305 6.33811C10.8305 5.19038 10.2301 3.91597 8.89573 2.50719L9.5659 1.87241C10.9804 3.36579 11.7536 4.85692 11.7536 6.33811C11.7536 8.50095 10.6077 9.83479 9.56034 10.9028L8.90129 10.2565C9.91606 9.22174 10.8305 8.11681 10.8305 6.33811ZM0 8.6107V4.0387H3.23077L6.46154 1.75408V10.959L3.11169 8.6107H0Z" fill="#4A7D95"></path>
# </svg></a>


# div.entry-word-container > div.vg  ( CONTAINS DEFINTIONS )
# div.vg > div.vg-sseq-entry-item[]  (Each "definiton , which may contain multiple variants")
# div.vg-sseq-entry-item > div.sb has-num has-let ms-lg-4 ms-3 w-100~  contains senses?
# div.sb has-num has-let ms-lg-4 ms-3 w-100~ > div.sb-0 sb-entry~ primary sense?
# || if sb-entry has subcontent, ie div.class="sense-content w-100"
#   ⬇️
# span.class="dtText" defintion
# div.sub-content-thread mb-3 example (may have multiple)
# ~ FOR sn-entry in sb has-num has-let ms-lg-4 ms-3 w-100 || vg-sseq-entry-item (higher)
# https://www.merriam-webster.com/dictionary/strident

# "IF" defHedword

# if AFTER search, word appears to be not found, 
# attempt dictionary.com logic


# if word NOT IN, if the word passing "freq", if the word not in x, define the word

# this is an edge case 
# 'entry-uros has-single-def'
# should only have a pos

# class="vg-sseq-entry-item " as "sense"
# for class="sb-0 sb-entry" in "sesne" (vg-sseq-...)
# IF class="sense has-sn has-num" -- Likely the first entry per sense
# IF class="sense has-sn" -- Likely NOT first entry
# IF class="sense  no-subnum" -- Likely NOT first entry
# class="sense-content w-100" will LIKELY contain senseIdx data
# class="dt hasSdSense" will LIKELY contain DEFINTION per senseIdx
# class="dt "  will LIKELY contain DEFINTION per senseIdx
# class="sdsense" > WILL LIKELY CONTAIN EXAMPLE
# class="sdsense > "class="dtText" WILL LIKELY CONAIN "direct" EXAMPLE TEXT




def get_definitions(word):
    resposne = requests.get(f'https://www.merriam-webster.com/dictionary/{word}')
    html_data = resposne.text

    # is alp

    soup = BeautifulSoup(html_data, 'html.parser')
    page_container = soup.find('div', 'left-content col position-relative overflow-hidden')

    pos_data_entrys = page_container.find('div', class_='entry-word-section-container')
    print(word)

    for pos_data_entry in pos_data_entrys:
        
        header_entry = pos_data_entry.find('div', class_='row entry-header')  # CONTAINNG WORD AND PART OF SPEECH

        word = header_entry.find(['h1', 'p'], class_='hword')  # WORD
        part_of_speech = header_entry.find('h2', class_='parts-of-speech').text  # PART OF SPEECH
        print('Part of speech:', part_of_speech)

        syl_pron_container = header_entry.find('div', class_='row entry-attr mb-3 mt-2')  # SYLLABLE PRONOUNCIATION CONTAIENR
        if syl_pron_container:
            word_syllable_repr = ''
            if syl_pron_container.find('span', class_='word-syllables-entry'):  
                word_syllable_repr = syl_pron_container.find('span', class_='word-syllables-entry').text  # WORD'S SYLLABLE REPRESENTION 
            word_pronounciation = syl_pron_container.find_all('span', class_='prons-entries-list-inline mb-1')  # WORD PRONOUNCIATION REPRESNETION // MAY BE A LIST

        definitions_container = pos_data_entry.find('div', 'vg')  # DEFINITIONS CONTAINER

        # definition_sense_container = pos_data_entry.find('div', class_='vg-sseq-entry-item')  # SENSE ENTRY
        definition_sense_containers = definitions_container.find_all('div', class_='vg-sseq-entry-item')  # SENSE ENTRY

        for i, definition_sense_container in enumerate(definition_sense_containers):

            definition_subsense_containers = definition_sense_container.find_all('div', class_='sb-entry')  # LIST OF SUBSENSE CONTAINERS

            for idx, definition_subsense_container in enumerate(definition_subsense_containers):
                definition_text = definition_subsense_container.find('span', class_='dtText')  # DEFINITION TEXT
                if definition_text:
                    print(f'{idx + 1} Definition', definition_text.text)

                examples = definition_subsense_container.find_all('div', class_='sub-content-thread mb-3')  # ASSOCIATED EXAMPLE(S) IF ANY
                if len(examples) > 0:
                    for example in examples:
                        print('Examples:', example.text)

            print('-------------------')


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

def structure_definitions_with_score(word):
    url = f"https://api.datamuse.com/words?sp={word}&qe=sp&md=dp"
    response = requests.get(url)
    data = response.json()

    if not data or "defs" not in data[0]:
        return {"word": word, "error": "No definitions found"}

    structured = {
        "word": word,
        "score": data[0]["score"],
        "definitions_by_pos": {}
    }

    for definition in data[0]["defs"]:
        pos, def_text = definition.split("\t", 1)
        if pos not in structured["definitions_by_pos"]:
            structured["definitions_by_pos"][pos] = []
        structured["definitions_by_pos"][pos].append({
            "definition": def_text,
            "score": data[0]["score"]  # Same score for all definitions
        })

    return structured
with open("ouput.json", "r") as infile:
    poem_objs = json.load(infile)


get_definitions('honey-horn')
print(len(poem_objs))

# https://api.datamuse.com/words?sp=scar&qe=sp&md=dpf
# better poem function
# for poem in poem_objs:
#     for s in poem['stanzas']:
#         for l in s:
#             c = l.split(' ')
#             for w in c:
#                 f = get_freq(w)
#                 if f < 5:
#                     print(w, "xyz")
#                     get_definitions(w)

# get_freq()


# get_definitions('boughs')



# Something about IF it contains a DT (definition text) -> Check for an example (div.sub-content-thread mb-3) 
# <div class="sense-content w-100"> each of the prior mentioned contained here (OF the sb_entry)
# IF not DT, the "text" will represent something like "informal" (usage label)