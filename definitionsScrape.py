import re
import json
import time
import asyncio
import aiohttp
import random
import traceback
import requests
import unicodedata
from bs4 import BeautifulSoup, NavigableString, Tag
from swiftshadow import QuickProxy
from swiftshadow.classes import ProxyInterface
from zenrows import ZenRowsClient
from playwright.async_api import async_playwright, Page, Playwright
# from playwright.sync_api import async_playwright, TimeoutError, Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor


# options = Options()
# options.add_argument("--headless=new")                 # much faster for automated runs
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")

mispelled_text = "The word you've entered isn't in the dictionary. Click on a spelling suggestion below or try again using the search bar above."
# options.add_argument("window-size=1200X600")

# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
# options.page_load_strategy = "eager"  

# def get_word_page_webster(word):
#     driver = webdriver.Chrome(options=options)

#     try:
#         driver.get("https://www.merriam-webster.com/")
#         driver.set_window_position(0, 0)
#         driver.set_window_size(957, 970)

#         driver.implicitly_wait(10)
#         search_box_container_home = driver.find_element('id', 'home-search-form')
#         search_box_home = search_box_container_home.find_element('id', 'home-search-term')
#         search_box_home.click()

#         driver.implicitly_wait(15)

#         search_box_container = driver.find_element('id', 'search-form')
#         search_box = search_box_container.find_element('id', 'search-term')
#         search_box.send_keys(word)

#         search_button = search_box_container.find_element('id', 'search-form-submit-btn')
#         search_button.click()

#         driver.implicitly_wait(15)

#         url = driver.current_url

#         return url  
#     finally: 
#         driver.close()
        # driver.quit()
# user_agents = [
#     # Chrome - macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#     # Safari - macOS
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
#     # Chrome - Linux
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",

# ]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.example.com/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}
extra_http_headers={
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.example.com/",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


async def get_word_page_webster_pw(p: Playwright, word_obj, prox):
    # print(ua.random)
    try:
        word = word_obj['word']
        # ua = UserAgent(browsers=['chrome'], os=['Mac OS X'], platforms=['desktop'])
        # print(ua.chrome)
        await asyncio.sleep(random.uniform(0.8, 1.8))
        # client = ZenRowsClient('522b49d529dab60ecca388404eda93c169d33f63',concurrency=20, retries=1)

        # Get the WebSocket connection URL
        connection_url = "wss://browser.zenrows.com?apikey=522b49d529dab60ecca388404eda93c169d33f63"        
        print(random.choice(prox))
        
        url = f"https://www.merriam-webster.com/dictionary/{word_obj['word']}"
        # connection_url= 'wss://browser.zenrows.com?apikey=522b49d529dab60ecca388404eda93c169d33f63'
        args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        ]
        browser = await p.chromium.launch(
            headless=True,
            args=args
        )
        # context = await browser.new_context(
        #     viewport={"width": 1600, "height": 971},
        #     # user_agent= user_agents[0]
        #     extra_http_headers={
        #         "User-Agent": user_agents[random.randint(0,len(user_agents)-1)],
        #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        #         "Accept-Encoding": "gzip, deflate, br",
        #         "Accept-Language": "en-US,en;q=0.5",
        #         "Referer": "https://www.flixyapp.com/",
        #         "Connection": "keep-alive",
        #         "Cache-Control": "no-cache",
        #         "Sec-Fetch-Dest": "document",
        #         "Sec-Fetch-Mode": "navigate",
        #         "Sec-Fetch-Site": "same-origin",
        #         "Sec-Fetch-User": "?1",
        #         "Upgrade-Insecure-Requests": "1",
        #     }
        # )
        # browser = await p.chromium.connect_over_cdp(connection_url);       
        context = await browser.new_context(
            viewport={"width": 1600, "height": 971},
            user_agent= user_agents[0],
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/",
                "Connection": "keep-alive",
                "Prioority": "u=0, i",
                "Host": "www.merriam-webster.com",
                "Cache-Control": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Upgrade-Insecure-Requests": "1",
            },
            java_script_enabled=True,
            locale="en-US"
            # proxy={
            #     'server': random.choice(prox)
            # }
        )
        page = await context.new_page()
        
        response = await page.goto(url, timeout=60_000)
        # response = await page.goto(url, wait_until="domcontentloaded", timeout=60_000)

        await page.wait_for_load_state("networkidle") 
        status = response.status if response else None
        if status > 300:
            # print(status)
            pass
        # # page.
        site_cookies = await context.cookies(url)
        print("site cookies:", site_cookies)

        # If the site shows a cookie-consent banner, accept it (site-specific selector)
        consent = page.locator('text=Accept').first
        if await consent.count() > 0:
            await consent.click()
            await page.wait_for_load_state("networkidle", timeout=10_000)

        # # page.wait_for_load_state('networkidle')
        # # await print(page.title())
        # search_box_home = page.locator("#home-search-term").first
        # await search_box_home.wait_for(state="visible", timeout=10000)
        # await search_box_home.click()
        # # search_box = await page.locator('#search-term').first
        # # await search_box.wait_for(state="visible", timeout=5000)
        # await search_box_home.fill(word)

        # search_button = page.locator('button.btn.position-absolute.home-search-button.search-dictionary').first
        # await search_button.wait_for(state="visible")
        # await search_button.click()
        content = await page.content()
        word_obj['content'] = content
        # print(word_obj)
        return word_obj
    except Exception as e:
        print(f"Error fetching URL for {word}: {e}")
        # stat = awiat
        # print()
        word_obj['content'] = None
        return word_obj
    finally:
        await browser.close()

async def get_word_page_collins_pw(p: Playwright, word_obj):
    # print(ua.random)
    browser = None
    try:
        word = word_obj['word']
        await asyncio.sleep(random.uniform(0.8, 1.8))

        # safe_word = quote(word.strip("\"'`’"), safe='-')
        url = f"https://www.collinsdictionary.com/us/dictionary/english/{word_obj['word']}"

        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        launch_args = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]

        # try headless first, fall back to headful if CF challenge persists
        browser = await p.chromium.launch(headless=True, args=launch_args)
        context = await browser.new_context(
            viewport={"width": 1600, "height": 971},
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/",
                "Connection": "keep-alive",
                "Prioority": "u=0, i",
                "Host": "www.merriam-webster.com",
                "Cache-Control": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Upgrade-Insecure-Requests": "1",
            },
            user_agent=ua,
            java_script_enabled=True,
            locale="en-US"
        )

        # small stealth: override webdriver and languages before any script runs
        # await context.add_init_script("""
        #     Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        #     Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
        #     Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        # """)

        page = await context.new_page()
        # single navigation, wait for network idle
        await page.goto(url, wait_until="networkidle", timeout=10_000)
 

        html = await page.content()
        # detect Cloudflare / JS challenge
        cf_indicators = ["Just a moment", "Enable JavaScript and cookies", "cf_chl_opt", "challenge-platform", "Verifying you are human"]
        blocked = any(ind in html for ind in cf_indicators)

        if blocked:
            # try again visible so challenge scripts can run with full capabilities
            await browser.close()
            browser = await p.chromium.launch(headless=False, args=launch_args)
            context = await browser.new_context(
                viewport={"width": 1600, "height": 971},
                user_agent=ua,
                java_script_enabled=True,
                locale="en-US"
            )
            # await context.add_init_script("""
            #     Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            #     Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
            #     Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            # """)
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=120_000)
            # allow extra time for CF challenge to resolve
            try:

                await page.wait_for_load_state("networkidle", timeout=30_000)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            except Exception:
                pass
            html = await page.content()

        
        word_obj['content'] = html
        print(html)

        return word_obj
    except Exception as e:
        print(f"Error fetching URL for {word}: {e}")
        # stat = awiat
        # print()
        word_obj['content'] = None
        return word_obj
   



# async def get_definitions(url: str, session) -> object:
# async def get_definitions(html_data, session) -> object:
async def get_definitions(word_obj, session) -> object:
    url = f"https://www.merriam-webster.com/dictionary/{word_obj['word']}"
    # print(word_obj['word'])
    async with session.get(url) as response:
        html_data = await response.text()

    soup = BeautifulSoup(html_data, 'html.parser')

    not_found_err = soup.find('p', class_='spelling-suggestion-text')
    not_found_entries = soup.find('p', class_='partial-match-blurb')
    if not_found_err:
        word_obj['error'] = '404: Not Found'
        # print('djfdhsk')
        return word_obj
    if not_found_entries:
        word_obj['error'] = '401: Malformed Entry'
        return word_obj
    
    try:

        # return 'Found'
        page_container = soup.find('div', 'left-content col position-relative overflow-hidden')

        pos_data_entries = page_container.find_all('div', class_='entry-word-section-container')
        # entry-word-section-container diff part of speech
        # print(word)

        # ex_sense = {
        #     'definition': None,
        #     'example': None
        # }
        # genreally ignore a subsense -> subsense

        ex_object = {
            "word": None,
            "partOfSpeech": [],
            "pronunciation": [],
            # "senses": [],
            # "senses": {},
            "partOfSpeechSense": [],
            "headWord": None,
            "isLowFreq": True,
            "isParentWord": False,
            "error": None
        }

        for speech_idx, pos_data_entry in enumerate(pos_data_entries):
            # print(speech_idx, 'speech index')

            # Finding header data (Word, Part of Speech, Pronunciation)
            header_entry = pos_data_entry.find('div', class_='row entry-header')  # CONTAINNG WORD AND PART OF SPEECH

            ## Finding word (first index only)
            if speech_idx == 0:
                ex_object['word'] = header_entry.find('h1', class_='hword').text  # WORD
                # print(word_obj['word'],ex_object['word'])

            ## Finding part of speech
            part_of_speech_container = header_entry.find('h2', class_='parts-of-speech')
            part_of_speech = ''
            if part_of_speech_container:
                part_of_speech = header_entry.find('h2', class_='parts-of-speech').text  # PART OF SPEECH
                ex_object['partOfSpeech'].append(part_of_speech)

            if part_of_speech == '':
                if len(ex_object['pronunciation']) == 0:
                    word_obj['error'] = 'cav'
                    return word_obj
                else:
                    continue
        
            
            dir_pron = header_entry.find('a', class_='play-pron-v2')
            if dir_pron:
                dir_pron_clean = dir_pron.get_text(" ", strip=True)
                dir_pron_clean = dir_pron_clean.replace("\xa0", " ").strip()
                ex_object['pronunciation'].append([dir_pron_clean])
            else:
                ## Finding word pronounciation
                pronunciation = header_entry.find('span', class_='prons-entries-list-inline mb-1')  # PRONUNCIATION
                if pronunciation: 
                    pronunciation_clean = pronunciation.get_text(" ", strip=True)
                    pronunciation_clean = pronunciation_clean.replace("\xa0", " ").strip()
                    # print(pronounciation_clean)
                    ex_object['pronunciation'].append([pronunciation_clean])

            ex_pos_sense = {
                f"pos:{part_of_speech}": []
            }

            pos_sense = {
                "partOfSpeech": part_of_speech,
                "posSenses": []
            }

            # Finding senses

            ## Finding overall senses section # may need a list of vg, if necessaery
            senses_sections = pos_data_entry.find_all('div', class_='vg')  # SENSES SECTION 

            for sense_section_idx, senses_section in enumerate(senses_sections):
                ## Finding all sense containers
                sense_entry_containers = senses_section.find_all('div', class_='vg-sseq-entry-item')  # SENSE CONTAINERS
                # EACH BIG MEANING (SENSE)
                # print(senses_section)
                # senses = []
                ex_senses = {
                    'senses': []
                }
                # senses = []

                
                ## Iterating through sense/subsense containers
                for sense_container_idx, sense_container in enumerate(sense_entry_containers):
                    # print(sense_container_idx+1)


                    ### Finding subsense containers
                    subsense_containers = sense_container.find_all('div', class_='sb-entry')  # SUBSENSE(S)

                    ex_subsenses = {
                        'subsenses': []
                    }
        
                    # subsense_arr = []  # SUBSENSES ie, 
                    # sense_arr = []  # SUBSENSES ie, 
                    # print('curr vg-sseq-entry-item:', sense_container_idx)
                    ### Iterating through subsense containers
                    for subsense_container_idx, subsense_container in enumerate(subsense_containers):
                        # print('curr sb idx:',subsense_container_idx)
                        modifier = subsense_container.find('span', class_='sen has-num-only')
                        if modifier:
                            continue
                        
                        modifier_1 = subsense_container.find('span', class_='sen has-sn')
                        if modifier_1:
                            continue

                   
                        ex_sense = {
                            'subsense': {'definition': None,
                                        'example': None}
                        }
            
                        #### Finding defintion container
                        definition_container = subsense_container.find('span', class_='dt')
                        # print('Anlyz:', subsense_container)
                        #### Finding defintion
                        defintion = definition_container.find('span', class_='dtText')
                        if defintion:
                            # some more cleaning needs to be done here, especially when it refrences another set of entries
                            defintion_clean = defintion.text #
                            reference_start = '(see '
                            if reference_start in defintion_clean:
                                defintion_clean = remove_definition_reference(defintion_clean)


                            # ex_sense['definition'] = defintion_clean
                            ex_sense['subsense']['definition'] = defintion_clean

                       
                        #### Finding example
                        example = subsense_container.find('div', class_='sub-content-thread mb-3')

                        if example:
                            example_clean = example.text.strip()
                            ex_sense['subsense']['example'] = example_clean

                        # print(ex_sense)
                        ex_subsenses['subsenses'].append(ex_sense)


                    # print(ex_senses['senses'])
                    ex_senses['senses'].append(ex_subsenses)

                  

                pos_sense['posSenses'].append(ex_senses) # keep this

            ex_object['partOfSpeechSense'].append(pos_sense) # keep this

    except Exception as e:
        # print(f'Error parsing word {word_obj['word']}: {e}')
        err_text = traceback.format_exc()
        # print(f"Error parsing word {word_obj.get('word')}: {e}")
        # print(err_text)               
        word_obj['error'] = str(e)
        word_obj['traceback'] = err_text
        return word_obj








        # Subsenses
        # syl_pron_container = header_entry.find('div', class_='row entry-attr mb-3 mt-2')  # SYLLABLE PRONOUNCIATION CONTAIENR
        # if syl_pron_container:
        #     word_syllable_repr = ''
        #     if syl_pron_container.find('span', class_='word-syllables-entry'):  
        #         word_syllable_repr = syl_pron_container.find('span', class_='word-syllables-entry').text  # WORD'S SYLLABLE REPRESENTION 
        #     word_pronounciation = syl_pron_container.find_all('span', class_='prons-entries-list-inline mb-1')  # WORD PRONOUNCIATION REPRESNETION // MAY BE A LIST
        ############

        # # definition_sense_container = pos_data_entry.find('div', class_='vg-sseq-entry-item')  # SENSE ENTRY
        # definition_sense_containers = definitions_container.find_all('div', class_='vg-sseq-entry-item')  # SENSE ENTRY

        # for i, definition_sense_container in enumerate(definition_sense_containers):

        #     definition_subsense_containers = definition_sense_container.find_all('div', class_='sb-entry')  # LIST OF SUBSENSE CONTAINERS

        #     for idx, definition_subsense_container in enumerate(definition_subsense_containers):
        #         definition_text = definition_subsense_container.find('span', class_='dtText')  # DEFINITION TEXT
        #         if definition_text:
        #             print(f'{idx + 1} Definition', definition_text.text)

        #         examples = definition_subsense_container.find_all('div', class_='sub-content-thread mb-3')  # ASSOCIATED EXAMPLE(S) IF ANY
        #         if len(examples) > 0:
        #             for example in examples:
        #                 print('Examples:', example.text)

        #     print('-------------------')

    if word_obj['word'].lower() != ex_object['word'].lower():
        headWord = ex_object['word']  # Word found
        ex_object['word'] = word_obj['word']  # Word searched
        ex_object['headWord'] = headWord  # Word found


    # print(ex_object)

    return ex_object

async def get_definitions_dictionary(word_obj, session):
    # happy
    url = f'https://www.dictionary.com/browse/{word_obj['word']}'
    async with session.get(url) as response:
        html_data = await response.text()


    soup = BeautifulSoup(html_data, 'html.parser')
    try:
        main_section = soup.find('main')

        not_found = main_section.find('span', class_='hp91nlVaykGzCu7JxmyY')
        if not_found:
            raise Exception('Not found')
            

        word_section = main_section.find('div', id=re.compile(r'^dictionary-entry-'))

        word_container = word_section.find('div', class_='bZjAAKVoBi7vttR0xUts')
        word = word_container.find('h1').text

        pronunciation_container = word_section.find('div', class_='aB40zqNSml1nCbUuOh7V')
        pronunciation = pronunciation_container.find('p').find('span').text

        
        part_of_speech_container = main_section.find('div', class_='S3nX0leWTGgcyInfTEbW')

        part_of_speech_raw = part_of_speech_container.find('h2').text
        if '(' in part_of_speech_raw:
            if part_of_speech_raw[0] == '(':
                pos_split = part_of_speech_raw.split(')')
                pos_join = pos_split[-1].strip()
                part_of_speech = pos_join
            else:
                pos_split = part_of_speech_raw.split('(')
                pos_join = pos_split[0].strip()
                part_of_speech = pos_join
        else:
            part_of_speech = part_of_speech_raw

        meta_container = part_of_speech_container.find('div', class_='JCaD6kbRs6iNqMfskUMc')
        meta = ''
        if meta_container:
            meta = meta_container.text
        definitons_container = word_section.find("ol", class_='t5mJ11S_WhGnhaUCbL5g wRxb9i_TOKzQ15D2tIVD')
        defintion = ''
        if definitons_container:
            defintion = definitons_container.find('li').text

        if defintion == '':
            raise Exception('Not found')
        
        ex_object = {
            "word": None,
            "partOfSpeech": [],
            "pronunciation": [],
            # "senses": [],
            # "senses": {},
            "partOfSpeechSense": [],
            "headWord": None,
            "isLowFreq": True,
            "isParentWord": False,
            "error": None
        }
        # print(ex_object)
        
        if meta != '':
            defintion = f'{meta} : {defintion}'
        
        senses = {
            'senses': []
        }

        pos_sense = {
                "partOfSpeech": part_of_speech,
                "posSenses": []
        }

        subsesnse = {
            'subsense': {
                'defintion': f': {defintion.strip()}',
                'example': None
            }
        }
        # print(ex_object)

        senses['senses'].append(subsesnse)
        # print(senses, 'djjdj')

        pos_sense['posSenses'].append(senses)

        ex_object['partOfSpeechSense'].append(pos_sense)
        

        ex_object['partOfSpeech'].append(part_of_speech)
        ex_object['pronunciation'].append([pronunciation])


        # word_test = [l for l in word if l.isalpha()]
        # word_prop_test = [l for l in word_prop if l.isalpha()]


        if word_obj['word'] != word:
            ex_object['headWord'] = word
    
        ex_object['word'] = word_obj['word']

        # print('djd')
        # print(ex_object)
        return ex_object
    except Exception as e:
        # print(f'{word_obj['word']}: {e}')
        err_text = traceback.format_exc()
        return word_obj
        print(err_text)    

    # sad path


async def get_definitions_datamuse(word_obj, session):
    # url = f'https://api.datamuse.com/words?sp={word_obj['word']}&md=dfp&ipa=1&max=5'


    # is it's likely a 's word  # frequency of it all
    # print(word_obj['word'][-2:], 'djdjjd')
    word = ''
    url = ''
    # print(['word'][-2])
    if word_obj['word'][-2:] == "'s":
        word = word_obj['word'][:-2]
        url = f'https://api.datamuse.com/words?sp={word}&md=dfr&ipa=1&max=5'
    else:
        url = f'https://api.datamuse.com/words?sp={word_obj['word']}&md=dfr&ipa=1&max=5'
    async with session.get(url) as response:
        response = await response.json()
     
    # print(response[0]['tags'])

    # if its the same, - special characters


    if not isinstance(response, list):
        if word == '':
            return {'word':word_obj['word'], 'isLowFreq': True, 'error': '404: Not Found'}
        else:
            return {'word':word_obj['word'], 'isLowFreq': True, 'error': '404: Not Found'}

    
    if len(response) < 1:
        return {'word':word_obj['word'], 'isLowFreq': True, 'error': '404: Not Found'}

    frequency = [tag[2:] for tag in response[0]['tags'] if tag[:2] == 'f:']
    # print(float(frequency[0]), "fjj")

    if float(frequency[0]) >= 4.8:
        # print('ddkkd')
        word_obj['isLowFreq'] = False
        word_obj['error'] = None
        word_obj['headWord'] = word
        return word_obj

    word_res = response[0]
    if word == '':
        word = word_obj['word']

    word_prop = word_res['word']

    word_test = [l for l in word if l.isalpha()]
    word_prop_test = [l for l in word_prop if l.isalpha()]

    if word_test != word_prop_test:
        # print('Not the same', word_prop)
        return {'word':word_obj['word'], 'isLowFreq': True, 'error': "401: Doesn't Match"}
    
    hw = word_res.get('defHeadword')
    if hw:
        head_word_res = word_res['defHeadword']
        r = await get_definitions({'word': head_word_res}, session)
        if r['error'] != None:
            return word_obj
        else:
            temp = r['word']
            r['word'] = word_obj['word']
            r['headWord'] = temp
            return r


    defs = word_res.get('defs')

    if not defs:
        # print('Not found', word_obj['word'])
        return {'word':word_obj['word'], 'error': '404: Not Found'}
    


    ex_object = {
        "word": None,
        "partOfSpeech": [],
        "pronunciation": [],
        # "senses": [],
        # "senses": {},
        "partOfSpeechSense": [],
        "headWord": None,
        "isLowFreq": True,
        "isParentWord": False,
        "error": None
    }
    
    pos_dict = {
        'n': 'noun',
        'v': 'verb',
        'adj': 'adjective',
        'adv': 'adverb'
    }
    try:
        for d in defs:
            def_split = d.split('\t')
            part_of_speech = pos_dict[def_split[0]]
            defintion = def_split[1]

            if part_of_speech not in ex_object['partOfSpeech']:
                # print('check')
                ex_object['partOfSpeech'].append(part_of_speech)
                pos_sense = {
                    "partOfSpeech": part_of_speech,
                    "posSenses": []
                }
                # print(pos_sense)
                senses = {
                    'senses': []
                }
                pos_sense['posSenses'].append(senses)
                # print(pos_sense)

                ex_object['partOfSpeechSense'].append(pos_sense)
            

            subsesnse = {
                'subsense': {
                    'defintion': f': {defintion.strip()}',
                    'example': None
                }
            }

            pos_sense_arr = ex_object['partOfSpeechSense']
            for pos_sense_obj in pos_sense_arr:
                if pos_sense_obj['partOfSpeech'] == part_of_speech:
                    pos_sense_obj['posSenses'][0]['senses'].append(subsesnse)
        
  

        ipa_start = 'ipa_pron:'
        pronunciation = [tag[len(ipa_start):] for tag in response[0]['tags'] if tag[:len(ipa_start)] == ipa_start]
        ex_object['pronunciation'].append([pronunciation[0]])



        # checking if original word is different from word from the response (aside from hyphens, spaces and other specail characters)
        if word_obj['word'] != word_res['word']:
            ex_object['headWord'] = word_res['word']
        
        ex_object['word'] = word_obj['word']

        # print(ex_object)

        return ex_object
    except Exception as e:
        # print(f'{word}:', e)
        return {'word': word_obj['word'], 'error': 'parse error'}


async def get_definitions_collins(word_obj, session):
    # url = f"https://www.collinsdictionary.com/us/dictionary/english/{word_obj['word']}"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #     "Referer": "https://www.google.com/",
    #     "Accept-Language": "en-US,en;q=0.9",
    # }
    # url = "https://www.collinsdictionary.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.collinsdictionary.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    # async with session.get(url, allow_redirects=True, headers=headers) as response:
    #     await asyncio.sleep(1.8)
    #     final_url = str(response.url)
    #     status = response.status

    #     html_data = await response.text()
    #     # print(final_url, word_obj['word'], status)
    #     if '/spellcheck/' in final_url or 'spellcheck' in final_url:
    #         word_obj['error'] = '404: Not Found'
    #         return word_obj
    html_data = word_obj['content']

    soup = BeautifulSoup(html_data, 'html.parser')
    # print(soup)
    # print(soup)

    main_content = soup.find('div', class_='spellcheck_wrapper')
    # print(main_content, word_obj['word'])

    # not_found = main_content.find('h1')
    # if not_found:
    #     if not_found.text == f'Sorry, no results for “{word_obj['word'].strip()}” in the English Dictionary.':
    #         word_obj['error'] = '404: Not Found'
    #         return word_obj
    # f'Sorry, no results for “{fdklah}” in the English Dictionary.'
    
    
    ex_object = {
        "word": None,
        "partOfSpeech": [],
        "pronunciation": [],
        # "senses": [],
        # "senses": {},
        "partOfSpeechSense": [],
        "headWord": None,
        "isLowFreq": True,
        "isParentWord": False,
        "error": None
    }

    dictionary_entry_container = main_content.find('div', class_='dictentry dictlink')

    word_container = dictionary_entry_container.find('h2', class_='h2_entry')
    word = word_container.find('span', class_='orth')
    if not word:
        word_obj['error'] = '404: Not Found'
        return word_obj
    ex_object['word'] = word.text

    pronunciation_container = dictionary_entry_container.find('div', class_='mini_h2')
    pronciation = pronunciation_container.find('span', class_='pron')
    if not pronciation:
        word_obj['error'] = '404: Not Found'
        return word_obj
    ex_object['pronunciation'].append(pronciation.text)

    definitions_container = word_container.find('div', class_='content definitions ced')
    part_of_speech = definitions_container.find('span', class_='gramGrp pos')
    if not part_of_speech:
        word_obj['error'] = '404: Not Found'
        return word_obj
    ex_object['partOfSpeech'].appened(part_of_speech.text)

    sense = definitions_container.find('div', class_='def')
    if not sense:
        word_obj['error'] = '404: Not Found'
        return word_obj
    
    pos_sense_obj = {
        'partOfSpeech': {part_of_speech.text}, 
        'posSenses': [
            {
                'senses': [
                    {'subsenses': [{'subsense': {'definition': f': {sense.text}', 'example': None}}, {'subsense': {'definition': ': to produce by or as if by incubation : hatch', 'example': None}}]}, 
                ]
            },
        ]
    }

    ex_object['partOfSpeechSense'].append(pos_sense_obj)

    if word.text != word_obj['word']:
        ex_object['headWord'] = word.text
        ex_object['word'] = word_obj['word']

    return ex_object


async def get_definitions_wiktionary(word_obj, session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    url = f"https://en.wiktionary.org/wiki/{word_obj['word']}"
    async with session.get(url, headers=headers) as response:
        html_data = await response.text()
        # print(response.status)

    soup = BeautifulSoup(html_data, 'html.parser')
    # print(soup)

    not_found_text = f'Wiktionary does not yet have an entry for {word_obj['word']}.'
    not_found = soup.find(string=not_found_text)
    if not_found:
        # print('How')
        word_obj['error'] = '404: Not Found'
        return word_obj
    # print('here', word_obj['word'])

    ex_object = {
        "word": None,
        "partOfSpeech": [],
        "pronunciation": [],
        # "senses": [],
        # "senses": {},
        "partOfSpeechSense": [],
        "headWord": None,
        "isLowFreq": True,
        "isParentWord": False,
        "error": None
    }

    parts_of_speech_dict = {
        'interjection':'interjection',
        'conjunction':'conjunction',
        'determiner':'determiner',
        'adjective':'adjective',
        'article':'article',
        'adverb':'adverb',
        'noun':'noun',
        'postposition':'postposition',
        'participle':'participle',
        'particle':'particle',
        'numeral':'numeral',
        'number':'number',
        'preposition':'preposition',
        'proper noun':'noun',
        'pronoun':'pronoun',
        'verb':'verb'
    }
    # unpursuable
    
    main_container = soup.find('main', id='content')
    if not main_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj

    # sad path
    

    header_container = main_container.find('header', class_="mw-body-header vector-page-titlebar no-font-mode-scale")
    if not header_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj
    header_text = header_container.find('span', class_="mw-page-title-main").text.lower()
    word_obj['word'] = header_text

    # print(header_text)
    data_section_container = main_container.find('div', id="mw-content-text") 
    if not data_section_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj
    
    data_containers = data_section_container.find_all('div', class_='mw-heading')
    
    # Iterate through data containers to find necessary data in neigboring containers (h3.pronunciation -> pronunciation text, h3.partOfSpeech -> senses)
    for data_container in data_containers:
        language_heading = data_container.find('h2')
        if language_heading:
            # if 'english' not in language_heading.text.lower() and 'transligual' not in language_heading.text.lower():
            if 'translingual' != language_heading.text.lower().strip() and 'english' != language_heading.text.lower().strip():
                # print(language_heading.text, 'djdj')
                # print(language_heading.text.lower(), 'transligual' not in language_heading.text.lower())
                break

        container_title = data_container.find('h3')
        if not container_title:
            continue
        container_title_text = container_title.text.lower().strip()
        if container_title_text == 'pronunciation':
            pronunciations_container = data_container.find_next('ul')
            if not pronunciations_container:
                continue
            pron_lis = pronunciations_container.find_all('li')
            for pron_li in pron_lis:
                if 'ipa' in pron_li.text.lower():
                    pron_li_split = pron_li.text.lower().split('ipa(key):')
                    pronunciation = pron_li_split[-1].strip().strip('/[]')
                    # print(pronunciation, '*')
                    ex_object['pronunciation'] = [pronunciation]

            pass
            # print(container_title_text)
            # 
            # container_title_text.
        elif container_title_text in parts_of_speech_dict:
            ex_object['partOfSpeech'].append(parts_of_speech_dict[container_title_text])
            definitions_container = data_container.find_next('ol')
            if not definitions_container:
                continue
            definition_containers = definitions_container.find_all('li', recursive=False)
            if not definition_containers:
                continue
            most_recent_pos = container_title_text
            senses = parse_definitions_wiktionary(definition_containers, most_recent_pos)
            if senses == 'error':
                continue
            ex_object['partOfSpeechSense'].append(senses)
        
        else:
            continue

    if ex_object['word'] != word_obj['word']:
        ex_object['headWord'] = ex_object['word']
        ex_object['word'] = word_obj['word']
    

    if len(ex_object['partOfSpeechSense']) < 1:
        word_obj['error'] = '401: Parse Error'
        return word_obj
    
    return ex_object

async def get_definitions_wiktionary_extra(word_obj, session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    url = f"https://en.wiktionary.org/wiki/{word_obj['word']}"
    async with session.get(url, headers=headers) as response:
        html_data = await response.text()
        # print(response.status)

    soup = BeautifulSoup(html_data, 'html.parser')
    # print(soup)

    not_found_text = f'Wiktionary does not yet have an entry for {word_obj['word']}.'
    not_found = soup.find(string=not_found_text)
    if not_found:
        # print('How')
        word_obj['error'] = '404: Not Found'
        return word_obj
    # print('here', word_obj['word'])

    ex_object = {
        "word": None,
        "partOfSpeech": [],
        "pronunciation": [],
        # "senses": [],
        # "senses": {},
        "partOfSpeechSense": [],
        "headWord": None,
        "isLowFreq": True,
        "isParentWord": False,
        "error": None
    }

    parts_of_speech_dict = {
        'interjection':'interjection',
        'conjunction':'conjunction',
        'determiner':'determiner',
        'adjective':'adjective',
        'article':'article',
        'adverb':'adverb',
        'noun':'noun',
        'postposition':'postposition',
        'participle':'participle',
        'particle':'particle',
        'numeral':'numeral',
        'number':'number',
        'preposition':'preposition',
        'proper noun':'noun',
        'pronoun':'pronoun',
        'verb':'verb'
    }
    # unpursuable
    
    main_container = soup.find('main', id='content')
    if not main_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj

    # sad path
    

    header_container = main_container.find('header', class_="mw-body-header vector-page-titlebar no-font-mode-scale")
    if not header_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj
    header_text = header_container.find('span', class_="mw-page-title-main").text.lower()

    word_obj['word'] = header_text

    data_section_container = main_container.find('div', id="mw-content-text") 
    if not data_section_container:
        word_obj['error'] = '401: Parse Error'
        return word_obj
    

    data_containers = data_section_container.find_all('div', class_='mw-heading')
    
    # Iterate through data containers to find necessary data in neigboring containers (h3.pronunciation -> pronunciation text, h3.partOfSpeech -> senses)
    for data_container in data_containers:
        # language_heading = data_container.find('h2')
        # if language_heading:
        #     # if 'english' not in language_heading.text.lower() and 'transligual' not in language_heading.text.lower():
        #     if 'translingual' != language_heading.text.lower().strip() and 'english' != language_heading.text.lower().strip():
        #         # print(language_heading.text, 'djdj')
        #         # print(language_heading.text.lower(), 'transligual' not in language_heading.text.lower())
        #         break

        container_title = data_container.find(['h3', 'h4'])
        if not container_title:
            continue
        container_title_text = container_title.text.lower().strip()
        if container_title_text == 'pronunciation':
            pronunciations_container = data_container.find_next('ul')
            if not pronunciations_container:
                continue
            pron_lis = pronunciations_container.find_all('li')
            for pron_li in pron_lis:
                if 'ipa' in pron_li.text.lower():
                    pron_li_split = pron_li.text.lower().split('ipa(key):')
                    pronunciation = pron_li_split[-1].strip().strip('/[]')
                    # print(pronunciation, '*')
                    ex_object['pronunciation'] = [pronunciation]
                    # print(pron_li.text.lower())
                    # print(pron_li_split)
                    # print(pron_li_split[-1].strip())
                    # print(len(pron_li_split))
            # print(container_title_text)
            # 
            # container_title_text.
        elif container_title_text in parts_of_speech_dict:
            ex_object['partOfSpeech'].append(parts_of_speech_dict[container_title_text])
            print('dj')
            definitions_container = data_container.find_next('ol')
          
            if not definitions_container:
                continue
            definition_containers = definitions_container.find_all('li', recursive=False)
            if not definition_containers:
                continue
            most_recent_pos = container_title_text
            senses = parse_definitions_wiktionary(definition_containers, most_recent_pos)
            if senses == 'error':
                continue
            ex_object['partOfSpeechSense'].append(senses)
        
        else:
            continue

    if ex_object['word'] != word_obj['word']:
        ex_object['headWord'] = ex_object['word']
        ex_object['word'] = word_obj['word']
    

    if len(ex_object['partOfSpeechSense']) < 1:
        word_obj['error'] = '401: Parse Error'
        # print('fjfj')
        return word_obj

    return ex_object
    
    # parts_of_speech.append(h3.text.lower().split()) - continue
    # if h3.text.lower().split() == 'pronunciation'
    # get neigbooring ul > li span class_=ipa text
    # if h3.text.lower().split() in pos' get newigboring / next ol
    # the li text in the ol as senses, couild have multiple ol on the same level
    # find

# /ˈæ͜ɑː.ren.del/
    

    
# content



def parse_definitions_wiktionary(definition_containers, pos):
    if len(definition_containers) < 1:
        return 'error'
    
    pos_sense = {
        'partOfSpeech': pos, 
        'posSenses': [
            {
                'senses':[]
            }
        ],
    }

    # senses = {
    #         'senses': []
    # }
    # senses = {
    #     'senses': [
    #         {'subsenses': [{'subsense': {'definition': f': Archaic. :  3rd person singular present indicative of {word_obj['word'][:-3]}.', 'example': None}}]},                   
    #     ]
    # }, 

    for li in definition_containers:
        if not li.text:
            continue
        # print(li.text)
        nested = li.find('ol')
        # print(len(li.÷))
        if not nested:
            # senses_data = {
            #     'senses': [
            #         {'subsenses': [{'subsense': {'definition': f': {li.text}.', 'example': None}}]},                   
            #     ]
            # }
            li_text = li.text.split('\n')
          
            example = li.find('i', class_='e-example')
            example_text = None
            if example:
                example_text = example.text

            subsense_data = {'subsenses': [{'subsense': {'definition': f': {li_text[0]}', 'example': example_text}}]},                   
          
            pos_sense['posSenses'][0]['senses'].append(subsense_data)
            continue
        
        nested_lis = nested.find_all('li')
        # print('---')

        subsenses = {'subsenses': []}
        
        

        # Finding nested <li>'s which will be subsenses for the primary sense
        for nested_li in nested_lis:
            # Setting up defintion text array to be joined into a "definition" string
            subsense_text = []

            # Iterating through definition <li> items / children to extract relevant data in the correct order
            for ch in nested_li.children:
                # If text is "unwrapped", add to subsense text
                if isinstance(ch, NavigableString):
                    subsense_text.append(ch)
                # If text is "wrapped" ensure it is of the proper structure to be added to the subsense text
                elif isinstance(ch, Tag):
                    classes = ch.get('class')
                    if classes:
                        if "nyms-toggle" or "HQToggle" in classes:
                            continue
                    if ch.name == 'dl' or ch.name == 'ul':
                        continue

                    subsense_text.append(ch.text)

            # Looking for subsense examples
            example = nested_li.find('i', class_='Latn mention e-example')
            example_text = None
            if example:
                example_text = example.text

            subsense = {
                'subsense': 
                    {'definition': f': {''.join(subsense_text).strip()}', 'example': example_text}
                
            }
            subsenses['subsenses'].append(subsense)

            



            # print('Res:', ''.join(text))
            # text = nested_li.text

            # if ''.__contains__('Coordinate ')
            # print('Nested li:', nested_li.text)
            # print('Subsenses:', subsenses)
            break
        # print(subsenses)
        # pos_sense['posSenses']['senses'].append(subsenses)
        pos_sense['posSenses'][-1]['senses'].append(subsenses)
        # print(pos_sense)
        break
    if len(pos_sense['posSenses']) < 1:
        return 'error'
    
    # if len(senses['senses'] > 1):

    
    return pos_sense
    
    
    

 


async def get_dash_word_defintions(word_obj, session):
    if '-' not in word_obj['word']:
        word_obj['error'] = '401: No dash'
        return [word_obj]

    parent_word = word_obj
    parent_word["isParentWord"] = True
    parent_word["error"] = None

    # print(parent_word)
    word_split = word_obj['word'].split('-')
    # print(parent_word)
    # print('\n')
    sub_words = []
    sub_words.append(parent_word)
    for w in word_split:
        # print(w)
        # async with session.get(url) as response:
            # url = f'https://api.datamuse.com/words?sp={word_obj['word']}&md=dfr&ipa=1&max=5'
        r = await get_definitions_datamuse({'word':w}, session)
        sub_words.append(r)
        

        # print(r, '\n')
        # return r
    


    return sub_words
    



async def get_eth_word_defintions(word_obj):
    print(list(word_obj['word']))
    if word_obj['word'][-3:] != 'eth':
        return word_obj
    
    
    word = word_obj['word'][:-3]
    if word_obj['word'][-5] == word_obj['word'][-4]:
        word = word_obj['word'][:-4]

    ex_object = {
        "word": word_obj['word'],
        "partOfSpeech": ['verb'],
        "pronunciation": [],
        # "senses": [],
        # "senses": {},
        "partOfSpeechSense": [
            {
            'partOfSpeech': 'verb', 
            'posSenses': [
                    {
                        'senses': [
                            {'subsenses': [{'subsense': {'definition': f': Archaic. :  3rd person singular present indicative of {word}.', 'example': None}}]},                   
                        ]
                    }, 
                ],
            }
        ],
        "headWord": word,
        "isLowFreq": True,
        "isParentWord": False,
        "error": None
    }
    # print(ex_object)
    return ex_object


async def get_accent_word_definitions(word_obj, session):
    word = word_obj['word']
    accent_word = format_accent_charaters(word)
    if word == accent_word:
        word_obj['error'] = '401: Not accented'
        return word_obj
    
    accent_word_obj = {'word': accent_word}

    definition_functions = [
        get_definitions,
        get_definitions_dictionary,
        get_definitions_datamuse,
        get_definitions_wiktionary,
        get_definitions_wiktionary_extra
    ]

    for func in definition_functions:
        accent_word_obj = await func(accent_word_obj, session)
        if accent_word_obj.get('error') is None:
            accent_word_obj['headWord'] = accent_word_obj['word']
            accent_word_obj['word'] = word
            return accent_word_obj
    
    return word_obj 

async def get_ed_word_defintions(word_obj, session):
    word = word_obj['word']
    # from -2 backwards
    if word[-2:] != "'d":
        word_obj['error'] = '401: Not an ed word'
        return word_obj
    
    # add the ed

    ed_word = word[:-2] + 'ed'
    # get_freq
    url = f'https://api.datamuse.com/words?sp={ed_word}&md=df&max=2'
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        
    if len(data) < 1:
        word_obj['error'] = '404: Not found'
        return word_obj
    
    word_frequency = float(data[0]['tags'][0][2:])

    if word_frequency == 0 or word_frequency >= 4.8:
        word_obj['isLowFreq'] = False
        word_obj['error'] = None
        return word_obj
    
    definition_functions = [
        get_definitions,
        get_definitions_dictionary,
        get_definitions_datamuse,
        get_definitions_wiktionary,
        get_definitions_wiktionary_extra
    ]

    ed_word_obj = {'word': ed_word}

    for func in definition_functions:
        ed_word_obj = await func(ed_word_obj, session)
        if ed_word_obj.get('error') is None:
            ed_word_obj['headWord'] = ed_word_obj['word']
            ed_word_obj['word'] = word
            return ed_word_obj
    
    word_obj['error'] = '404: Not Found'
    return word_obj 

   
    # get frequency 
    # if < point  or == 0
    # return low freq
    # else
    # get the sense (cascade)

    # modify the values head word + main word
    # return the value


    

    # accent_word_obj = await get_definitions(accent_word_obj, session)
    # if accent_word_obj['error'] == None:
    #     accent_word_obj['word'] = word
    #     accent_word_obj['headWord'] = accent_word_obj['word']
    #     return accent_word_obj

    # accent_word_obj = await get_definitions_dictionary(accent_word_obj, session)
    # if accent_word_obj['error'] == None:
    #     accent_word_obj['word'] = word
    #     accent_word_obj['headWord'] = accent_word_obj['word']
    #     return accent_word_obj


    # accent_word_obj = await get_definitions_datamuse(accent_word_obj, session)
    # if accent_word_obj['error'] == None:
    #     accent_word_obj['word'] = word
    #     accent_word_obj['headWord'] = accent_word_obj['word']
    #     return accent_word_obj


    # accent_word_obj = await get_definitions_wiktionary(accent_word_obj, session)
    # if accent_word_obj['error'] == None:
    #     accent_word_obj['word'] = word
    #     accent_word_obj['headWord'] = accent_word_obj['word']
    #     return accent_word_obj
    
    # accent_word_obj = await get_definitions_wiktionary_extra(accent_word_obj, session)
    # if accent_word_obj['error'] == None:
    #     accent_word_obj['word'] = word
    #     accent_word_obj['headWord'] = accent_word_obj['word']
    #     return accent_word_obj



            

        
        



    
    # Error does not equal anything

    
    {'word': 'invidious', 
     'score': 39036, 
     'tags': ['f:0.515366'], 
     'defs': ['adj\tCausing ill will, envy, or offense. ', 
              'adj\t(of a distinction) Offensively or unfairly discriminating. ', 
              'adj\t(obsolete) Envious, jealous. ', 
              'adj\tDetestable, hateful, or odious. (Often used in cases of perceived unfairness, or when facing a difficult situation or choice — especially in the phrase invidious position.) ']}


def get_freq(word):
    response = None
    _req = .5
    while True:
        try:
            # response = freqSession.get(f'https://api.datamuse.com/words?sp={word}&&md=f&max=1').json()
            response = freqSession.get(f'https://api.datamuse.com/words?sp={word}&md=df&max=2').json()

            # f'https://api.datamuse.com/words?sp={word}&qe=sp&md=f'
            # f'https://api.datamuse.com/words?sp={fox}&qe=sp&md=f&max=1'
        except:
            print('Could not get response. Sleep and retry...')
            time.sleep(_req)
            continue
        break

    # May do something where I check the frequency of the current and compare it to a neear head word
    # MAY access the [definition] if there -> def[headword] -> check "headword" frquency.... (as to ensure )
    freq = 0.0 
  
    if len(response)==0: return freq
    
    if len(response) == 1: float(response[0]['tags'][0][2:])

    if word == 'forgets':
        print('forgets')
        print(response[0]['defHeadword'])
        print(response[1]["word"])

    try:
        res_0 = response[0]['defHeadword'] 
    except (IndexError, KeyError, TypeError):
        return float(response[0]['tags'][0][2:])
        res_0 = None
    try:
        res_1 = response[1]["word"]
    except (IndexError, KeyError, TypeError):
        res_1 = None
        return float(response[0]['tags'][0][2:])

 

    if res_0 and res_1:
        res_0_freq = float(response[0]['tags'][0][2:])
        res_1_freq = float(response[1]['tags'][0][2:])
        if res_0.lower() == res_1.lower():
            print('Forgets')
            return res_0_freq if res_0_freq >= res_1_freq else res_1_freq
            
    return float(response[0]['tags'][0][2:])

async def get_freq_(word, session):
    url = f'https://api.datamuse.com/words?sp={word}&md=df&max=2'
    async with session.get(url, headers=headers) as response:
        response = await response.json()


    # May do something where I check the frequency of the current and compare it to a neear head word
    # MAY access the [definition] if there -> def[headword] -> check "headword" frquency.... (as to ensure )
    freq = 0.0 
  
    if len(response)==0: return freq, word
    
    if len(response) == 1: return float(response[0]['tags'][0][2:]), word

    if word == 'forgets':
        print('forgets')
        print(response[0]['defHeadword'])
        print(response[1]["word"])

    try:
        res_0 = response[0]['defHeadword'] 
    except (IndexError, KeyError, TypeError):
        return float(response[0]['tags'][0][2:]), word
        res_0 = None
    try:
        res_1 = response[1]["word"]
    except (IndexError, KeyError, TypeError):
        res_1 = None
        return float(response[0]['tags'][0][2:]), word

 

    if res_0 and res_1:
        res_0_freq = float(response[0]['tags'][0][2:])
        res_1_freq = float(response[1]['tags'][0][2:])
        if res_0.lower() == res_1.lower():
            print('Forgets')
            if res_0_freq >= res_1_freq: return res_0_freq, word 
            else: return res_1_freq, word
            
    return float(response[0]['tags'][0][2:]), word

    # return freq

def get_poems_word_freq():
    with open("ouput.json", "r", encoding='utf-8') as infile:
        poem_objs = json.load(infile)
    
    # low = set()
    # med = set()
    wordDict = dict()

    if not poem_objs:
        return
    
    visited = dict()
    

    for idx, poem in enumerate(poem_objs):
        stanzas = poem['stanzas']
        for stanza in stanzas: 
            for line in stanza:
                words = line.split(' ')
                words = [word for word in words if word not in visited]
                words_cleaned = [clean_word(word, visited).lower() for word in words]

                with ThreadPoolExecutor() as executor:
                    results = executor.map(get_freq, words_cleaned)
                    for word, freq in zip(words_cleaned, results):
                        if freq < 4.8:
                            if word == '': continue

                            if word not in wordDict:
                                wordDict[word] = {
                                    'word': word,
                                    'isLowFreq': True
                                }
                        else:
                            if word not in wordDict:
                                wordDict[word] = {
                                    'word': word,
                                    'isLowFreq': False
                                }



    return wordDict, visited 

async def get_poems_word_freq_():
    with open("ouput.json", "r", encoding='utf-8') as infile:
        poem_objs = json.load(infile)
    
    # low = set()
    # med = set()
    wordDict = dict()

    if not poem_objs:
        return
    
    visited = dict()
    
    async with aiohttp.ClientSession() as session:
        for idx, poem in enumerate(poem_objs):
            stanzas = poem['stanzas']
            for stanza in stanzas: 
                for line in stanza:
                    words = line.split(' ')
                    words = [word for word in words if word not in visited]
                    words_cleaned = [clean_word(word, visited).lower() for word in words]
                    
                    freq_tasks = [get_freq_(word, session) for word in words_cleaned]
                    freq_objects = await asyncio.gather(*freq_tasks, return_exceptions=False)
                    # print(freq_objects)
                    for freq, word in freq_objects:
                        if word == '': continue
                        # print(idx)
                        if freq < 4.8:
                            if word not in wordDict:
                                wordDict[word] = {
                                    'word': word,
                                    'isLowFreq': True
                                }
                        else:
                            if word not in wordDict:
                                wordDict[word] = {
                                    'word': word,
                                    'isLowFreq': False
                                }

    return wordDict, visited 


def dump_word_freq(d, v):
    pre_word_objects = []

    i = 0

    for k, v in d.items():
        pre_word_objects.append(v)
        if v['isLowFreq'] == True:
            i += 1

    with open('word_freq_.json', 'w', encoding='utf-8') as f:
        json.dump(pre_word_objects, f, ensure_ascii=False, indent=4)

# elif 4.8 <= freq < 5.1:
#         med.add(word)

def clean_word(word: str, visited: dict):   
    visited[word] = True

    if word == '——————' or word == '————————': return ''

    if word.isalpha():
        return word
    
    dash_chars = {"-", "–", "—", "\u2013", "\u2014"}
    apos_chars = {"'", "’", "`"}

    cleaned_word: str = ''
    # print(len(word))
    for idx, letter in enumerate(word):
        if letter in apos_chars and 0 < idx < len(word)-1:
        # if letter in ('"') and 0 < idx < len(word)-1:
            cleaned_word += letter
            continue

        if letter == '-' and idx + 1 < len(word) and word[idx+1] == '-':
            if 0 < idx < len(word) - 2:
                cleaned_word.append(letter)
                continue

        if letter in dash_chars:
            if 0 < idx < len(word) - 1:
                cleaned_word+=('-')
                continue
           
        if letter.isalpha():
            cleaned_word += letter
    
    if cleaned_word not in visited:
        visited[cleaned_word] = True
    

    return cleaned_word

def format_accent_charaters(word):

    return ''.join(
        ch for ch in unicodedata.normalize('NFD', word)
        if unicodedata.category(ch) != 'Mn'
    )


def group_defineition_objs(word_objs):
    low = []
    high = []
    missed = []

    for word_obj in word_objs:
        error = word_obj.get('error')
        if error is not None:
            missed.append(word_obj)
            continue

        isLowFreq = word_obj.get('isLowFreq')
        low.append(word_obj) if isLowFreq == True else high.append(word_obj)

    return low, high, missed


async def get_word_objs_from_file():
    
    with open("word_freq_.json", "r", encoding='utf-8') as f:
        freq_objs = json.load(f)
 
    freq_words = [w for w in freq_objs if w['isLowFreq'] == True]
    low_freq_words = [w for w in freq_objs if w['isLowFreq'] == False]

    low_freq_set = {w['word'] for w in low_freq_words}
  
    all_content = []
    low_freq_words = []
    high_freq_words = []
    missed_words = []
   
    async with aiohttp.ClientSession() as session:
        # Filters word objects through dictionary containing websites to obtain defintions.
        # "Missed words" will attempt to be found on other websites and 
        defintion_tasks = [get_definitions(word, session) for word in freq_words]
        defintion_objs = await asyncio.gather(*defintion_tasks, return_exceptions=False)
        low, high, missed = group_defineition_objs(defintion_objs)
        low_freq_words.extend(low)
        high_freq_words.extend(high)
        missed_words = missed


        # missed_words = [obj for obj in defintion_objs if obj['error'] is not None]
        # high_freq_words = [obj for obj in defintion_objs if obj.get('isLowFreq') == True and obj['error'] is None]
        # low_freq_words = [obj for obj in defintion_objs if obj.get('isLowFreq') == False and obj['error'] is None]
        # all_content.extend([obj for obj in defintion_objs if obj['error'] == None])
        

        if len(missed_words) > 0:
            defintion_tasks_1 = [get_definitions_dictionary(word, session) for word in missed_words]
            defintion_objs_1 = await asyncio.gather(*defintion_tasks_1, return_exceptions=False)
            low, high, missed = group_defineition_objs(defintion_objs_1)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed


            # all_content.extend([obj for obj in defintion_objs_1 if obj['error'] == None])

        if len(missed_words) > 0:
            defintion_tasks_2 = [get_definitions_datamuse(word, session) for word in missed_words]
            defintion_objs_2 = await asyncio.gather(*defintion_tasks_2, return_exceptions=False)
            low, high, missed = group_defineition_objs(defintion_objs_2)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed


            # missed_words = [obj for obj in defintion_objs_2 if obj['error'] != None]
            # all_content.extend([obj for obj in defintion_objs_2 if obj['error'] == None])
   
        if len(missed_words) > 0:
            eth_tasks = [get_eth_word_defintions(word) for word in missed_words]
            eth_objs = await asyncio.gather(*eth_tasks, return_exceptions=False)
            low, high, missed = group_defineition_objs(eth_objs)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed


            # missed_words = [obj for obj in eth_words if obj['error'] != None]
            # all_content.extend([obj for obj in eth_words if obj['error'] == None])

        if len(missed_words) > 0:
            defintion_tasks_3 = [get_definitions_wiktionary(word, session) for word in missed_words]
            defintion_objs_3 = await asyncio.gather(*defintion_tasks_3, return_exceptions=False)
            low, high, missed = group_defineition_objs(defintion_objs_3)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed
            # missed_words = [obj for obj in defintion_objs_3 if obj['error'] != None]
            # all_content.extend([obj for obj in defintion_objs_3 if obj['error'] == None])

        if len(missed_words) > 0:
            dash_tasks = [get_dash_word_defintions(word, session) for word in missed_words]
            dash_obj_arrays = await asyncio.gather(*dash_tasks, return_exceptions=False)
            missed_words = []
            for obj_array in dash_obj_arrays:
                low, high, missed = group_defineition_objs(obj_array)
                low_freq_words.extend(low)
                high_freq_words.extend(high)
                missed_words.extend(missed)

                # for obj in obj_array:
                    # <if true> if (condition) else <if false>
                    # all_content.append(obj) if obj['error'] == None else missed_words.append(obj)

        if len(missed_words) > 0:
            defintion_tasks_4 = [get_definitions_wiktionary_extra(word, session) for word in missed_words]
            defintion_objs_4 = await asyncio.gather(*defintion_tasks_4, return_exceptions=False)
            low, high, missed = group_defineition_objs(defintion_objs_4)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed
            # missed_words = [obj for obj in defintion_objs_4 if obj['error'] != None]
            # all_content.extend([obj for obj in defintion_objs_4 if obj['error'] == None])

        if len(missed_words) > 0:
            accent_tasks = [get_accent_word_definitions(word, session) for word in missed_words]
            accent_objs = await asyncio.gather(*accent_tasks, return_exceptions=False)
            low, high, missed = group_defineition_objs(accent_objs)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed
            # missed_words = [obj for obj in accent_objs if obj['error'] != None]
            # all_content.extend([obj for obj in accent_objs if obj['error'] == None])

        if len(missed_words) > 0:
            missed_words = []
            ed_tasks = [get_ed_word_defintions(word, session) for word in missed_words]
            ed_objs = await asyncio.gather(*ed_tasks, return_exceptions=False)
            low, high, missed = group_defineition_objs(ed_objs)
            low_freq_words.extend(low)
            high_freq_words.extend(high)
            missed_words = missed
            # missed_words = [obj for obj in ed_objs if obj['error'] != None]
            # all_content.extend([obj for obj in ed_objs if obj['error'] == None])

    # The sense formatting thing..

    

    low_freq_words = [w for w in low_freq_words if w['word'] not in low_freq_set]

    headWordObjs = []
    for word in low_freq_words:
        headWord = word.get('headWord')
        if headWord != None and headWord != '':
            headWordObj = word
            headWordObj['word'] = headWord
            headWordObj['headWord'] = None
            headWordObjs.append(headWordObj)
            print(word)
    print(headWordObjs[-1])
    if len(headWordObjs) > 0:
        for headWordObj in headWordObjs:
            low_freq_words.append(headWordObj)


    with open('high_freq_words.json', 'w', encoding='utf-8') as f:
        json.dump(high_freq_words, f, ensure_ascii=False, indent=2)

    with open('low_freq_words.json', 'w', encoding='utf-8') as f:
        json.dump(low_freq_words, f, ensure_ascii=False, indent=2)

    with open('missed_words_.json', 'w', encoding='utf-8') as ff:
        json.dump(missed_words, ff, ensure_ascii=False, indent=2)

def remove_definition_reference(definition: str):
    definiton_parts = definition.split(' ')

    delete_id = 'delete-me'
    delete_id_has_comma = 'delete-me-comma'

    i = 0
    start_string = '(see'
    # for part in definiton_parts:
    while i < len(definiton_parts):
        if definiton_parts[i] == start_string:
            definiton_parts[i] = delete_id
            j = i + 1
            while ')' not in definiton_parts[j]:
                definiton_parts[j] = delete_id
                j += 1
            if ',' in definiton_parts[j]:
                definiton_parts[j] = delete_id_has_comma 
            else:
                definiton_parts[j] = delete_id

            i = j
        i += 1
    
    definiton_parts_cleaned = []
    for i in range(len(definiton_parts)):
        part = definiton_parts[i]
        if part == delete_id_has_comma:
            definiton_parts_cleaned[-1] = definiton_parts_cleaned[-1] + ','
        if part != delete_id and part != delete_id_has_comma:
            definiton_parts_cleaned.append(part)
        

    return ' '.join(definiton_parts_cleaned)


# Basically, checking if a defintion has been found

# if p.class="spelling-suggestion-text".text.strip === "The word you've entered isn't in the dictionary. Click on a spelling suggestion below or try again using the search bar above."

async def main():
    start_time = time.perf_counter()
    word_freq_dict, visited = await get_poems_word_freq_()
    poem_duration = time.perf_counter() - start_time

    dump_word_freq(word_freq_dict, visited)
    post_dump_time = time.perf_counter()

    await get_word_objs_from_file()
    words_duration = time.perf_counter() - post_dump_time


    total_duration = time.perf_counter() - start_time

    print(f"Processed poems in {poem_duration} seconds")
    print(f"Processed {len(word_freq_dict)} words in {words_duration} seconds")
    print(f"Total time: {total_duration} seconds")
    # w = ':How are you (see how 1b)'
    # w = ": any of various aquatic and chiefly marine brown, red, or green algae (such as rockweed, gulfweed, and kelp) that often grow in masses, typically have leaflike blades (see blade entry 1 sense 2e), are usually anchored to a solid substrate (such as a rock) by holdfasts (see holdfast sense 2a), and include some (such as dulse, laver, and sea lettuce) that are used as food"
    # w = ': to make or lay (something) bare (see bare entry 1) : uncover'
    # w = ': kept for breeding (see breed entry 1 sense 3)'

    # print(c)
   

    # await get_word_objs_from_file()


if __name__ == "__main__":
    asyncio.run(main())
    # may try catch this
    # freqSession = requests.session()
    # word_freq_dict, visited = get_poems_word_freq()

    # dump_word_freq(d=word_freq_dict, v=visited)


    ##
    # with open("word_freq.json", "r", encoding='utf-8') as f:
    #     freq_objs = json.load(f)

    # ii = 0

    # low_freq_words = [w['word'] for w in freq_objs if w['isLowFreq'] == True]
    # low_freq_words = low_freq_words[:5]
    # q = queue()

    # with ThreadPoolExecutor() as exec:
    #     res = exec.map(get_word_page_webster, low_freq_words)  # returns url
    #     for w, p in zip(low_freq_words, res):
    #         queue.put(p)

    
    # for i, w in enumerate(freq_objs):

    #     if w['isLowFreq']:
    #         word_url = get_word_page_webster(w['word'])
    #         def_obj = get_definitions(word_url)
    #         print(def_obj)
    #         ii += 1

    #     if ii == 5:
    #         break


    
    # setting id at some point..
    # d = {}
    # print('—' == '—')

    # w = "Shakespeare listens—understands—"
    # w = w.split(' ')
    # for i in w:
    #     z = clean_word(i, d)
    #     print(i)
    #     print(z)
    






    # ch = '\u00c3\u00ab'
    # ch = '\u00c3'
    # print(unicodedata.category('\u00c3'))
    # print(ch.isalpha())
    # Input and output filenames
    # infile = "output.json"
    # outfile = "output_utf8.json"

    # # Step 1: Read file (guess encoding if needed, e.g. 'latin1' if you saw mojibake)
    # with open("ouput.json", "r", encoding="utf-8") as f:   # <-- change to match your bad file's encoding
    #     data = json.load(f)

    # # Step 2: Write back out as proper UTF-8
    # with open(outfile, "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    
# retroactively checking frequency if no defintion for coumpiund word is found


    # word_url = get_word_page_webster("canst")
    # def_obj = get_definitions(word_url)
    # print(def_obj, '\n')
    # print('-----------\n')
    # print(def_obj['senses'], '\n')
    # print(def_obj['pronunciation'], '\n')
    # print('-----------\n')
    # print(def_obj['partOfSpeechSense'], '\n')


# word_url = get_word_page_webster("hewn")

# def_obj = get_definitions(word_url)

# print(def_obj, '\n')
# print('-----------\n')
# print(def_obj['senses'], '\n')
# print(def_obj['pronunciation'], '\n')
# print('-----------\n')
# print(def_obj['partOfSpeechSense'], '\n')
# print('-----------\n')
# print(len(def_obj['senses']['pos:adjective']), '\n')
# print('-----------\n')
# print(len(def_obj['senses']['pos:verb']), '\n')
# print(len(def_obj['senses'][2]['pos:verb']))
# print('-----------\n')
# print(len(def_obj['senses'][2]['pos:verb'][0]))
# print('-----------\n')
# print(len(def_obj['senses'][2]['pos:adj'][1]))


# print(len(def_obj['senses']))
# skip if nit found on either


# ALSO dictionary.com if there is no part of speech for the word
# "[Pg 178]", distinct removal
# could be done in "poem" cleaning
# try catch for the process
# 's ending words
# re-entering, fine.
# wide-eyed, fine.
# off-shore, fine.
# ebb-tide , fine.
# lover-wise, fine.
# whey-bearded, not fine.
# listen.) ,, does normalize
# so a lot will depend on how I split it
# like a process of request, validate response, retry request, valid response, etc
# so if it's seperated by a single hypen I should certianlya attempt to submit it
# then each potion will have a freq.. but yeah cant have the same definition

# \u2014 actual dash, may help
# basiclaly I could use data msuse to find a similar word..


#  ## Finding overall senses section # may need a list of vg, if necessaery
#         senses_section = pos_data_entry.find('div', class_='vg')  # SENSES SECTION 

#         ## Finding all sense containers
#         sense_entry_containers = senses_section.find_all('div', class_='vg-sseq-entry-item')  # SENSE CONTAINERS

#         ## Iterating through sense/subsense containers
#         for sense_container_idx, sense_container in enumerate(sense_entry_containers):
            
#             ### Finding subsense containers
#             subsense_containers = sense_container.find_all('div', class_='sb-entry')

#             sense_arr = []

#             ### Iterating through subsense containers
#             for subsense_container_idx, subsense_container in enumerate(subsense_containers):
#                 ex_sense = {
#                     'definition': None,
#                     'example': None
#                 }

#                 #### Finding defintion container
#                 definition_container = subsense_container.find('span', class_='dt')

#                 #### Finding defintion
#                 defintion = definition_container.find('span', class_='dtText')
#                 if defintion:
#                     # some more cleaning needs to be done here, especially when it refrences another set of entries
#                     defintion_clean = defintion.text #
#                     ex_sense['definition'] = defintion_clean

#                 #### Finding example container
#                 # class="sub-content-thread mb-3" WHERE AN EXAMPLE WOULD ACTUALLY BE FOUND
#                 # example_container = subsense_container.find('div', class_='sdsense') ACTUALLY A "SUBSENSE"
#                 # example_container = subsense_container.find('div', class_='sdsense')

#                 # if example_container:
#                 #### Finding example
#                 example = subsense_container.find('div', class_='sub-content-thread mb-3')

#                 if example:
#                     example_clean = example.text.strip()
#                     ex_sense['example'] = example_clean
                
#                 sense_arr.append(ex_sense)
            
#             ex_object['senses'].append(sense_arr)

# if the word can be split, then it should be added to words in seperate entries.. 
# thats when each method of adding fails

# {'senses':  # ALL MEANINGS PER POS*
#     [
#         {
#             'subsenses': [{'subsense': {'definition': ': the young of an animal or a family of young', 'example': 'a hen with her brood of chicks'}}]  # BIG MEANING(S)
#         }, 
#         {
#             'subsenses': [{'subsense': {'definition': ': a group having a common nature or origin', 'example': 'the entire brood of chronicle plays—T. S. Eliot'}}]  # BIG MEANING(S)
#         }, 
#         {
#             'subsenses': [{'subsense': {'definition': ': the children of a family', 'example': 'takes their brood to church every Sunday'}}]  # BIG MEANING(S)
#         }
#     ]
# }


[
    {
        'partOfSpeech': 'noun', 
        'posSenses': [
            {
                'senses': [
                    {'subsenses': [{'subsense': {'definition': ': the young of an animal or a family of young', 'example': 'a hen with her brood of chicks'}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': a group having a common nature or origin', 'example': 'the entire brood of chronicle plays—T. S. Eliot'}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': the children of a family', 'example': 'takes their brood to church every Sunday'}}]}]
             }
        ]
    }, 
    {
        'partOfSpeech': 'adjective', 
        'posSenses': [{'senses': [{'subsenses': [{'subsense': {'definition': ': kept for breeding (see breed entry 1 sense 3)', 'example': 'a brood flock'}}]}]}]
    }, 
    {
        'partOfSpeech': 'verb', 
        'posSenses': [
            {
                'senses': [
                    {'subsenses': [{'subsense': {'definition': ': to sit on or incubate (eggs)', 'example': None}}, {'subsense': {'definition': ': to produce by or as if by incubation : hatch', 'example': None}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': to cover (young) with the wings', 'example': None}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': to think anxiously or gloomily about : ponder', 'example': 'I used to brood these things on my walk—Christopher Morley'}}]}
                ]
            }, 
            {
                'senses': [
                    {'subsenses': [{'subsense': {'definition': ': to brood eggs or young', 'example': None}}, {'subsense': {'definition': ': to sit quietly and thoughtfully : meditate', 'example': None}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': hover, loom', 'example': 'the old fort brooding above the valley'}}]}, 
                    {'subsenses': [{'subsense': {'definition': ': to dwell gloomily on a subject', 'example': 'brooded over his mistake'}}, {'subsense': {'definition': ': to be in a state of depression', 'example': 'sat brooding in her room'}}]}
                ]
            }
        ]
    }
] 