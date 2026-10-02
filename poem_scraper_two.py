from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import json
import re
import time
import aiohttp
import asyncio
import itertools
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext

def get_poem_from_poeticious():
    pass

async def dump_poets(poets: list):
    with open('poets_new.json', 'w') as f:
        json.dump(poets, f, indent=2)

async def get_poets_from_json():
    with open('poets_new.json', 'r') as f:
        return json.load(f)
        


"""
Poeticous Functions
"""
async def get_poems_by_poet_poeticous(
        poet: object,
        session: aiohttp.ClientSession,
        browser: Browser,
        sem: asyncio.Semaphore
) -> list:
    print('get_poems_by_poet_poeticous triggered')

    poet_name = format_poet_name_from_obj(poet_obj=poet)
    if not poet_name:
        return get_poet_poems_obj(poet_obj=None, poems=[], error='May be empty')
    poet_name_split = poet_name.split(' ')
    poet_name_href = '-'.join(poet_name_split).lower()

    url = f'https://www.poeticous.com/{poet_name_href}'
    print(url)

    async with sem:
        await asyncio.sleep(45)
        poet_exists = await poet_exists_poeticous(url=url, session=session)
        if not poet_exists: return get_poet_poems_obj(poet_obj=poet, poems=[], error=None)


        await asyncio.sleep(45)
        hrefs = await get_poem_hrefs_poeticous(url=url, browser=browser, session=session)

        
        poem_tasks = [get_poem_poeticous(href=href, poet_name=poet_name, session=session) for href in hrefs]
        poem_objs = await asyncio.gather(*poem_tasks, return_exceptions=True)

        # poem_objs_filtered = []

        # # filter the "None's"
        # for poem_obj in poem_objs:
        #     if poem_obj: poem_objs_filtered.append(poem_obj)
        #     else: continue
            
        # https://www.poeticous.com/Charles-Mackay
        # https://www.poeticous.com/charles-mackay/tis-sweet-in-the-shade-of-the-lofty-trees


        # return poem_objs_filtered
        return get_poet_poems_obj(poet_obj=poet, poems=poem_objs)

async def get_poem_poeticous(
    href: str,
    poet_name: str,
    session: aiohttp.ClientSession
) -> object | None: 
    print('get_poem_poeticous triggered')
    url = f'https://www.poeticous.com/{href}'
    await asyncio.sleep(45)
    async with session.get(url) as response:
        html_data = await response.text()

    soup = BeautifulSoup(html_data, 'html.parser')

    h2_tag = soup.find('h2', class_='merri-title text-center mb-0')
    if not h2_tag:
        return None

    title = h2_tag.text.strip()

    body_container = soup.find('div', class_='p-poem')
    if not body_container:
        return None
    
    stanzas = []

    line_tags = body_container.find_all('div', class_='verse')
    if not line_tags:
        return None
    stanza = []
    for line_tag in line_tags:
        line_text = line_tag.get_text()
        if line_text == None or line_text == '':
            continue
        line_tag_sibling = line_tag.find_next_sibling('div')
        if not line_tag_sibling:
            print('Not this')
            stanza.append(line_text)
            stanzas.append(stanza)
            stanza = []
            continue
        classes = line_tag_sibling.get('class')
        if 'verse' not in classes and 'verse ' not in classes:
            print('Not class')
            stanza.append(line_text)
            stanzas.append(stanza)
            stanza = []
            continue
        stanza.append(line_text)
    

    # poem_obj = get_poem_obj(title=title, poet_name=poet_name, stanzas=stanzas)

    return get_poem_obj(title=title, poet_name=poet_name, stanzas=stanzas)


# get all poem hrefs for a given poet
async def get_poem_hrefs_poeticous(
        url: str,
        browser: Browser,
        session: aiohttp.ClientSession
) -> list[str]:
    print('get_poem_hrefs_poeticous triggered')
    # https://www.poeticous.com/charles-mackay?locale=en&page=2
    hrefs = []
    i  = 1
    end = False
    while not end:
        paging_hrefs = await get_poem_hrefs_from_page_poeticous(base_url=url, page=i, browser=browser, session=session)
        if len(paging_hrefs) < 1:
            end = True
        hrefs.append(paging_hrefs)
        i += 1

    # flatten the hrefs
    hrefs_flattened = list(itertools.chain.from_iterable(hrefs))
    print(hrefs_flattened[0])
    return hrefs_flattened

# get the hrefs contained within a poeticous page
async def get_poem_hrefs_from_page_poeticous(
        base_url: str, 
        page: int,
        browser: Browser,
        session: aiohttp.ClientSession
) -> list[str]:
    print('get_poem_hrefs_from_page_poeticous triggered')
    # https://www.poeticous.com/charles-mackay?locale=en&page=2
    url = base_url if page < 2 else f'{base_url}?locale=en&page={page}'

    
    html_data = await get_poem_page_text_poeticous_pw(url=url, browser=browser)
    
    if not html_data:
        return []

    hrefs = []

    soup = BeautifulSoup(html_data, 'html.parser')
    
    # poems_container = soup.find('div', id='my-poems-container')
    # poems_container = soup.find('div', class_='container mb-7 pt-3kk pt-md-6 pt-lg-2')
    # get poem cards
    poem_cards = soup.find_all('div', class_='p-animated-card col-xl-4 col-md-6 mb-4')
    if not poem_cards:
        return hrefs
    
    for poem_card in poem_cards:
        a_tag = poem_card.find('a')
        if not a_tag:
            continue
        href = a_tag.get('href')
        if not href:
            continue
        hrefs.append(href)
    # print(hrefs)
    
    return hrefs


async def poet_exists_poeticous(
    url: str, 
    session: aiohttp.ClientSession
) -> bool:
    print('poet_exists_poeticous triggered')
    async with session.get(url) as response:
        html_data = await response.text()
      
    
    soup = BeautifulSoup(html_data, 'html.parser')
    body = soup.find('body')
    if not body: return False
    body_text = body.getText()
    print('body', body_text)

    page_not_found_text = 'You are being redirected'

    if page_not_found_text in body_text: return False
    
    return True


## Playwright section

async def get_poem_page_text_poeticous_pw(
    url: str,
    browser: Browser
) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    page = await browser.new_page()
    try:
        print(url, 'slfkjsdljf')
        await page.set_extra_http_headers(headers)
        await page.goto(url, wait_until="domcontentloaded")
        await page.goto(url, wait_until="domcontentloaded")
        await page.screenshot(path='screenshot.png', full_page=True)
        # await page.wait_for_selector('div#my-poems-container')
        # await page.wait_for_load_state('domcontentloaded')
        text = await page.locator('body').inner_html()
        # print(text)
       

        if text != None and text != '':
            return text
        else:
            return ''
        
    finally:
        await page.close()


async def get_poem_poeticous_test(
    href: str,
    poet_name: str,
    session: aiohttp.ClientSession
) -> object | None: 
    print('get_poem_poeticous triggered')
    url = f'https://www.poeticous.com/{href}'

    async with session.get(url) as response:
        html_data = await response.text()

    soup = BeautifulSoup(html_data, 'html.parser')

    h2_tag = soup.find('h2', class_='merri-title text-center mb-0')
    if not h2_tag:
        return None

    title = h2_tag.text.strip()

    body_container = soup.find('div', class_='p-poem')
    if not body_container:
        return None
    
    stanzas = []

    line_tags = body_container.find_all('div', class_='verse')
    # line_tags_set = set(line_tags)
    if not line_tags:
        return None
    stanza = []
    for line_tag in line_tags:
        # line_text = line_tag.get_text().strip()
        line_text = line_tag.get_text()
        if line_text == None or line_text == '':
            continue
        line_text = normalize_text(line_text)
        line_tag_sibling = line_tag.find_next_sibling('div')
        # print(line_tag_sibling)
        if not line_tag_sibling:
            print('Not this')
            stanza.append(line_text)
            stanzas.append(stanza)
            stanza = []
            continue
        classes = line_tag_sibling.get('class')
        if 'verse' not in classes and 'verse ' not in classes:
            print('Not class')
            stanza.append(line_text)
            stanzas.append(stanza)
            stanza = []
            continue
        stanza.append(line_text)
    
    print(stanzas)
    poem_obj = get_poem_obj(title=title, poet_name=poet_name, stanzas=stanzas)

    return poem_obj
"""
All Poerty Functions
"""
async def get_poet_page_text_allpoetry(
    url: str,
    context: BrowserContext
) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    page = await context.new_page()
    try:
        print(url, 'slfkjsdljf')
        await page.set_extra_http_headers(headers)
        await page.goto(url, wait_until="commit")
        await page.goto(url, wait_until="commit")
        print(f"FINAL URL:  {page.url}")
        # print(f"STATUS:     {response.status}"

        await page.screenshot(path='screenshot.png', full_page=True)
        # await page.wait_for_selector('div#my-poems-container')
        # await page.wait_for_load_state('domcontentloaded')
        not_found = page.get_by_text("404 File Not Found ", exact=True)
        # await not_found.is_visible()
        # print(not_found)
        if await not_found.is_visible(): return None
        # await page.get_by_text("Full title list", exact=False).wait_for(timeout=10_000)
        # print(text)
        a_tag_class = 'a.btn--link.get.only'
        a_tag = page.locator('btn--link get only')
        print(a_tag)
        await a_tag.wait_for(state="visible")
        await a_tag.click()

        await page.wait_for_load_state("domcontentloaded")


        text = await page.locator('body').inner_html()
        print(text)

       

        if text != None and text != '':
            return text
        else:
            return ''
    except Exception as e:
        print(e)
        return
        
    finally:
        await page.close()

async def get_poems_by_poet_allpoetry(
    poet: object,
    session: aiohttp.ClientSession,
    context: BrowserContext,
    sem: asyncio.Semaphore,
    get_poem_sem: asyncio.Semaphore
) -> list:
    print('get_poems_by_poet_allpoetry triggered')
    
    poet_name = format_poet_name_from_obj(poet_obj=poet)
    if not poet_name:
        return get_poet_poems_obj(poet_obj=None, poems=[], error=None)
    poet_name_split = poet_name.split(' ')
    poet_name_href = '-'.join(poet_name_split).lower()

    url = f'https://allpoetry.com/{poet_name_href}'
    
    async with sem:
        try:
            await asyncio.sleep(5)
            poem_hrefs = []
            poem_objs = []
            poem_list_href = await get_poet_poem_list_href_allpoetry(url=url, context=context, session=session)

            poem_hrefs =  await get_poem_hrefs_from_poet_page_allpoetry(url=url, session=session) if not poem_list_href else await get_poem_hrefs_from_list_allpoetry(href=poem_list_href, session=session)
            if not poem_hrefs or len(poem_hrefs) == 0: raise Exception('Not found')

            poem_tasks = [get_poem_allpoetry(href=href, poet_name=poet_name, sem=get_poem_sem, session=session) for href in poem_hrefs]
            poem_objs = await asyncio.gather(*poem_tasks, return_exceptions=True) 

            poem_objs_filtered = []
            for poem_obj in poem_objs:
                if poem_obj: poem_objs_filtered.append(poem_obj)
            
            print(poem_objs_filtered)


            return get_poet_poems_obj(poet_obj=poet, poems=poem_objs_filtered, error=None)
        
        except Exception as e:
            return get_poet_poems_obj(poet_obj=poet, poems=[], error=str(e))


async def get_poem_objs_allpoetry(
    poet_name: str,
    hrefs: list,
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore
):
    poem_tasks = [get_poem_allpoetry(href=href, poet_name=poet_name, sem=sem, session=session) for href in hrefs]
    poem_objs = await asyncio.gather(*poem_tasks, return_exceptions=True) 

    return poem_objs

async def get_poem_hrefs_from_list_allpoetry(
    href: str,
    session: aiohttp.ClientSession
) -> list[str]:
    print('get_poem_hrefs_from_list_allpoetry triggered')
    url = f'https://www.allpoetry.com{href}'
    try:
        async with session.get(url) as response:
            html_data = await response.text()

        soup = BeautifulSoup(html_data, 'html.parser')
        ul_tag = soup.find('ul', class_='gapped')
        if not ul_tag: return []

        a_tags = ul_tag.select('li > a')
        if not a_tags or len(a_tags) == 0: return []

        hrefs = [a_tag.get('href') for a_tag in a_tags if a_tag.get('href') or len(a_tag.get('href')) > 0]

        # for a_tag in a_tags:
        #     href = a_tag.get('href')
        #     if not href or len(href) == 0: continue
        #     hrefs.append(href)

        return hrefs

    except Exception as e:
        print('e', e)
        return []
    
async def get_poem_hrefs_from_poet_page_allpoetry(
    url: str,
    session: aiohttp.ClientSession
) -> list[str]:
    print('get_poem_hrefs_from_poet_page_allpoetry triggered')
    # url = f'https://allpoetry.com{href}'
    try:
        async with session.get(url) as response:
            html_data = await response.text()

        soup = BeautifulSoup(html_data, 'html.parser')
        # title vcard item 
        a_tags = soup.select('h1.title.vcard.item > a')
        print('a_tags', a_tags)
        if not a_tags or len(a_tags) == 0: return []

        hrefs = [a_tag.get('href') for a_tag in a_tags if a_tag.get('href') or len(a_tag.get('href')) > 0]

        return hrefs

    except Exception as e:
        print('e', e)
        return []


async def get_poem_allpoetry(
    href: str,
    poet_name: str,
    sem: asyncio.Semaphore,
    session: aiohttp.ClientSession
) -> object | None: 
    print('get_poem_allpoetry triggered')
    async with sem:
        try:
            url = f'https://allpoetry.com{href}'
            await asyncio.sleep(3) 
            async with session.get(url) as response:
                html_data = await response.text()
            
            soup = BeautifulSoup(html_data, 'html.parser')

            title_tag = soup.select_one('h1 > a')
            if not title_tag: return None

            title = title_tag.get_text().strip()
            if not title: return
            if len(title) < 0: return None

            poem_body_tag = soup.find('div', class_='poem_body')
            if not poem_body_tag: return None
            
            poem_content_tag = poem_body_tag.find('div', class_=re.compile('orig_'))
            if not poem_body_tag: return None
            
            poem_content = poem_content_tag.contents
            poem_content = [item for item in poem_content if repr(item) != '\n' and len(str(item)) != 1]
            # for i, val in enumerate(poem_content):
            #     if i + 1 == 13:

            #         print(f'{i+1}: {str(val)} : {len(str(val))}')
            #         print(repr(val))
            # print(poem_content[0])
            
            # Find consecuitive <br/>'s, indicating a space / end of a stanza
            pre_stanzas = []
            start = 0

            i = 1
            while i < len(poem_content):
                curr_item = poem_content[i]
                prev_item = poem_content[i-1]
                # print(f'***{curr_item}***')
                # print(prev_item)
                if isinstance(curr_item, Tag) and isinstance(prev_item, Tag):
                    if str(curr_item) == '<br/>' and str(prev_item) == '<br/>':
                        pre_stanzas.append(poem_content[start:i-1])
                        start = i + 1
                
                i += 1 
            
            pre_stanzas.append(poem_content[start:len(poem_content)])
            # print(pre_stanzas)

            stanzas = []
            for index, pre_stanza in enumerate(pre_stanzas):
                print('index',index)
                print(pre_stanza)
                print('')
                stanza = clean_stanza_allpoems(stanza=pre_stanza)
                if not stanza: continue
                stanzas.append(stanza)

            if len(stanzas) == 0: return None
            
            return get_poem_obj(title=title, poet_name=poet_name, stanzas=stanzas)
        
        except Exception as e:
            print('e', e)
            return None

    
async def get_poet_poem_list_href_allpoetry(
    url: str, 
    context: BrowserContext,
    session: aiohttp.ClientSession
):
    print('get_poet_poem_list_href_allpoetry triggered')
    async with session.get(url) as response:
        html_data = await response.text()
    # html_data = await get_poet_page_text_allpoetry(url=url, context=context)
    # print('html', html_data)
    

    soup = BeautifulSoup(html_data, 'html.parser')
    not_found = soup.select_one('h2.error')

    if not_found: 
        raise Exception('Not found')
        return None

    # tl_container = soup.select_one('div.t_links')
    # print(tl_container)
    # a_tags = tl_container.find_all('a')
    # hrefs = [a_tag.get('href') for a_tag in a_tags if a_tag.get('href') is not None]
    # print(a_tags, 'lsfjlsajf')
    # return
    
    list_page_tag = soup.find('a', string=re.compile('Full title list →'))
    if not list_page_tag: return None


    href = list_page_tag.get('href')
    if not href: return None

    return href


def clean_stanza_allpoems(stanza: list) -> list | None:
    if len(stanza) == 0: return None
    stanza_cleaned = []
    for item in stanza:
        if isinstance(item, Tag):
            # print(item)
            if str(item) == '<br/>': continue
            item_contents = item.contents
            for content in item_contents:
                # no current fix for this
                raise Exception('html in tag')
                if isinstance(content, NavigableString):
                    line = normalize_text(str(item).strip())
                    stanza_cleaned.append(line)
            continue

        # line = normalize_text(str(item).strip())
        # stanza_cleaned.append(line)
        stanza_cleaned.append(item)
    
    if len(stanza_cleaned) < 1: return None

    return stanza_cleaned


"""
General Accessory Functions
"""

def format_poet_name_from_obj(poet_obj):
    print('format_poet_name_from_obj triggered')
    first_name = poet_obj.get('first_name')
    middle_name = poet_obj.get('middle_name')
    last_name = poet_obj.get('last_name')

    if not first_name and not last_name and not middle_name:
        return None

   
    if (first_name != '' and first_name != None) and (middle_name != '' and middle_name != None) and (last_name != '' and last_name != None):
        return f'{first_name} {middle_name} {last_name}'
    elif (first_name != '' and first_name != None) and (last_name != '' and last_name != None):
        return f'{first_name} {last_name}'
    elif (first_name != '' and first_name != None):
        return first_name
    else:
        return last_name
    # else (last_name != '' and last_name != None):
    # when there is a last name, first name, and middle name

    # when there is no middle name

def get_poem_obj(
        title: str, 
        poet_name: str,
        stanzas: list[list[str]]
) -> object:
    print('get_poem_obj triggered')
    return {
        'title': title,
        'poet': poet_name,
        'stanzas': stanzas
    }

def get_poet_poems_obj(
    poet_obj: object | None,
    poems: list,
    error: str | None
) -> object:
    return {
        'poetObj': poet_obj,
        'poems': poems,
        'error': error
    }


def normalize_text(s: str) -> str:
    # s = s.replace("\u00a0", " ")
    # s = re.sub(r"\s+", " ", s)  # turns any whitespace (incl \r,\n,\t) into single space
    # s = s.replace('\u2019', "'")
    # s = s.replace('\u2014', "—")
    # s = s.replace('\u2013', "–")
    # return s.strip()
    if not s:
        return ''

    replacements = {
        "\u00a0": " ",    # NBSP
        "\ufeff": "",     # BOM
        # single quotes / apostrophes
        "\u2019": "'",    # right single quote
        "\u2018": "'",    # left single quote
        "\u201a": ",",    # single low-9 quotation mark
        "\u201b": "'",    # single high-reversed-9 quotation mark
        "\u2032": "'",    # prime
        # double quotes
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u201e": '"',    # double low-9 quotation mark
        "\u2033": '"',    # double prime
        # dashes / hyphens
        "\u2014": "—",    # em dash
        "\u2013": "–",    # en dash
        "\u2012": "-",    # figure dash
        "\u2010": "-",    # hyphen
        "\u2011": "-",    # non-breaking hyphen
        # ellipsis / bullets / other
        "\u2026": "...",  # ellipsis
        "\u00b7": "•",    # middle dot
        "\u2212": "-",    # minus sign -> hyphen
        # angle quotes
        "\u2039": "<",
        "\u203a": ">",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # collapse runs of whitespace (spaces, tabs, newlines) into a single space
    s = re.sub(r"\s+", " ", s)
    return s.strip()

"""
File Retrieval Functions
"""

def get_poets_from_file():
    file_name = 'poet_objs_new.json_birthplacesearch.json'
    poet_objs = None
    with open(file=file_name, encoding='utf-8', mode='r') as f:
        poet_objs = json.load(f)
    # print(poet_objs)
    return poet_objs
    poets = []
    for i in poet_objs:
        p = format_poet_name_from_obj(i)
        if p is not None: poets.append(p)
    
    return poets


async def dump_found_poem(
        poems: list,
        file_name: str
):
    with open(file=file_name, encoding='utf-8', mode='w') as f:
        json.dump(poems, f, ensure_ascii=False, indent=2)

async def dump_found_poems(
        poet_poem_objs: list,
        file_name: str
):
    poems = []
    for poet_poem_obj in poet_poem_objs:
        # error = poems_from_obj.get('error')
        poems_from_obj = poet_poem_obj.get('poems')
        if poems_from_obj is None: continue
        if len(poems_from_obj) < 1: continue
        poems.extend(poems_from_obj)


    with open(file=file_name, encoding='utf-8', mode='w') as f:
        json.dump(poems, f, ensure_ascii=False, indent=2)

async def dump_not_found_poets(
        poet_poem_objs: list,
        file_name: str
):
    # poets = []
    # for poet_poem_obj in poet_poem_objs:
    #     poet = poet_poem_obj.get('poetObj')
    #     if poet: poets.append(poet)


    with open(file=file_name, encoding='utf-8', mode='w') as f:
        json.dump(poet_poem_objs, f, indent=2)
 

async def main():
    # poets = await get_poets_from_pf()
    # await dump_poets(poets)
    # poets = await get_poets_from_json()
    sem = asyncio.Semaphore(7)
    sem_poem = asyncio.Semaphore(7)
    
 
    poems = []
    poet_poem_objs = []
    poet_poems_not_found = []
    poet_poems_error = []
    poet_objs = get_poets_from_file()
    # print()
    # poet_objs = poet_objs[:10]
    # poet_objs = [
    #     {
    #         "first_name": "Theodosia",
    #         "middle_name": None,
    #         "last_name": "Garrison",
    #         "birth_date": "January 01, 1874",
    #         "nationality": "American",
    #         "birth_place": "Newark, New Jersey, U.S.",
    #         "alt_names": [
    #         "Theodosia Pickering Garrison Faulks"
    #         ],
    #         "profile_picture_url": "https://d3eqbj00kgn0hf.cloudfront.net/poets/theodosia_garrison_27350821",
    #         "error": None
    #     }
    # ]
    # poet_objs = [
    #     {
    #         "first_name": "Ernest",
    #         "middle_name": None,
    #         "last_name": "Rhys",
    #         "birth_date": "January 01, 1874",
    #         "nationality": "American",
    #         "birth_place": "Newark, New Jersey, U.S.",
    #         "alt_names": [
    #         "Theodosia Pickering Garrison Faulks"
    #         ],
    #         "profile_picture_url": "https://d3eqbj00kgn0hf.cloudfront.net/poets/theodosia_garrison_27350821",
    #         "error": None
    #     }
    # ]
    # print(poet_objs)
    # upload poets...
    session_cookie = "Vi3fOjSsBr5bmWEUeTCRcAoqn9F5w8BG6ZSDpBS2f6Of59YW97iOdYauQEak9fa4gtUHqHvHwGLrpaIEI1tnJCmc9BnVEXRaJNiLbtj9fzGC9rMBYCS7Ic%2FclXpBpU21aGZ7d5Pcc%2BrlGSBLlU4h%2BQ5WqkU6ZWH3AMfahW9V9XSnmvWnnLgIlFC%2FC9nY3AF5o8nLu3DechcqCwTJmNwDVriohUE6E5SfyJi7Il2ALJKLenEdP2Ta%2FnIYriNrlVAdoeuC9cFBjIdgaxpkw9NlaXCAX8Yzpxlu%2FJ%2Bj8Bk3We%2BpgZd%2FN%2FhhNP6KeNekJVBAZgEEq%2BwQM1OH9fJP9S0DHRqnZ7YxxSe6b5XF1OcMTiXS1J%2F%2Fs33z5WXralvKsrAY29umQ8Uqlmt6ntjdJB%2Btc2cTtGCxZKez7zmytrNYU0HnUYnybEvUjvxpH7J6J9Q7YWFD0rGlUdewhu7sOQ3PhVltNqlYEAQ9W%2BheDvDRK1ZrQTpZoXD3lNg%2B5rxjJn5ZzmY8gIYkTfQucrqRVErFLEz2bNfgonk0vUX9xwpad%2BKDSkkH2FE47ZtpEU3swGhUEZK3tcmfmD8CQCceA7gdB2WsTOtIC68nu8pASNDIiIQnewVk1WfwH7lK2TlSYaY%2BnbwDxg2%2B9%2BIMpg%3D%3D--ezaADVjjEBqfNnLy--jBUueGowYh1Bqd8MiReXNA%3D%3D"
    remember_token = 'eyJfcmFpbHMiOnsibWVzc2FnZSI6Ild5SlhkMlIyYkhCeklpeHVkV3hzWFE9PSIsImV4cCI6bnVsbCwicHVyIjoiY29va2llLnJlbWVtYmVyX24ifX0%3D--42ab5081dd2bfc224ec9ab6eb87c6c6799aa5bf9'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    cookies = {
        "_N": session_cookie,
        "remember_user_token": remember_token,
        "tmb%24%7Buser.id%7D": "1",
        "unr": "0",
        "z": "1",
    }

    # async with aiohttp.ClientSession(headers=headers) as session:
    #     # poem = await get_poem_poeticous_test(href='charles-mackay/if-i-were-a-voice', poet_name='Charles Mackay', session=session)
    #     poem = await get_poem_poeticous_test(href='theodosia-garrison/transients', poet_name='Theodosia Garrison', session=session)
    #     print(poem)
            
    async with async_playwright() as playwright:
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            chromium = playwright.chromium
            browser = await chromium.launch(headless=False, channel="chrome") 
            context = await browser.new_context() 
            await context.add_cookies([
                {
                    "name": "_N",
                    "value": session_cookie,
                    "domain": "allpoetry.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "remember_n",
                    "value": remember_token,
                    "domain": "allpoetry.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "tmb%24%7Buser.id%7D",
                    "value": "1",
                    "domain": "allpoetry.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": False,
                },
                {
                    "name": "z",
                    "value": "1",
                    "domain": "allpoetry.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "unr",
                    "value": "0",
                    "domain": "allpoetry.com",
                    "path": "/",
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                
            ])
            # test_href = '/poem/8505619-Lament--O-how-all-things-are-far-removed--by-Rainer-Maria-Rilke'
            test_href = '/overheard-on-a-saltmarsh'
            # s = "\n                No. "
            # for i in s:
            #     print(i)
            poem = await get_poem_allpoetry(href=test_href, poet_name='Charles Bukowski', session=session, sem=sem_poem)
            await dump_found_poem(poems=[poem], file_name='output_single_new.json')
            print(poem)
            # poeticious_poem_tasks = [get_poems_by_poet_allpoetry(poet=poet, session=session, sem=sem, context=context, get_poem_sem=sem_poem) for poet in poet_objs]  # will return lists of poets
            # poeticious_poems = await asyncio.gather(*poeticious_poem_tasks, return_exceptions=True)




            # for poet_poem_obj in poeticious_poems:
            #     # print(poet_poem_obj)
            #     error = poet_poem_obj.get('error')
            #     if error is not None:
            #         poet_poems_error.append(poet_poem_obj)
            #         continue
            #     poet_from_obj = poet_poem_obj.get('poetObj')
            #     if not poet_from_obj: continue
            #     poems_from_obj = poet_poem_obj.get('poems')
            #     if poems_from_obj == None:
            #         poet_poems_not_found.append(poet_poem_obj)
            #         continue
            #     if len(poems_from_obj) < 1: 
            #         poet_poems_not_found.append(poet_poem_obj)
            #         continue
            #     poet_poem_objs.append(poet_poem_obj)

            # The 
            # https://allpoetry.com/poem/8505619-Lament--O-how-all-things-are-far-removed--by-Rainer-Maria-Rilke
            # the "" thing, what causes it, why, and how to prevent it and make those "" into stanzas
            # removing the "trasnlated" part on the last line

            # await dump_found_poems(poet_poem_objs=poet_poem_objs, file_name='output_new.json')
            # await dump_not_found_poets(poet_poem_objs=poet_poems_not_found, file_name='output_new_not_found.json')
            # await dump_not_found_poets(poet_poem_objs=poet_poems_error, file_name='output_new_error.json')

            # chromium = playwright.chromium  # used for playwright
            # browser = await chromium.launch()  # used for playwright

            # will realistically check for errors here

            # poeticious_poems_flattened = list(itertools.chain(poeticious_poems))
            # poet_poem_objs.append(poeticious_poems)

            # Filter poet poem objs into their respective lists

    print(len(poet_poem_objs))
    print(len(poet_poems_not_found))




    # then I'll get the words for the poems

if __name__ == "__main__":
    asyncio.run(main())