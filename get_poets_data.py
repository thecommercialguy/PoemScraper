import requests
import wikipediaapi
from bs4 import BeautifulSoup, Tag, NavigableString
import shutil
import io
import boto3
from botocore.exceptions import ClientError
import os
import logging
import uuid
import json
import asyncio
import aiohttp
from poem_scraper_two import format_poet_name_from_obj
import tracemalloc
tracemalloc.start()

wikimedia_sem_info_box = asyncio.Semaphore(15)
wikimedia_sem_no_info_box = asyncio.Semaphore(15)

async def get_poet_data_wiki_entry(poet_name: str, session, sem: asyncio.Semaphore):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    p_name_split = poet_name.split()
    p_name_search_format = '+'.join(p_name_split)
    url = f'https://en.wikipedia.org/w/index.php?search={p_name_search_format}+poet&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1'
    
    print(url)
    poet_obj = {}
    async with sem:
        # res = requests.get(url, headers=headers, allow_redirects=True)
        try:
            async with session.get(url, headers=headers) as response:
                html_data = await response.text()

            soup = BeautifulSoup(html_data, 'html.parser')

            search_results = soup.find_all('li', class_="mw-search-result mw-search-result-ns-0")
            if len(search_results) == 0:
                raise Exception('Not found')
            
            for i, search_result in enumerate(search_results):
                if i == 3: 
                    print('giaff')
                    poet_obj=None
                    break
                    # BF*: poet_obj not null therefore error in obj returning None
                    first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
                    poet_obj['first_name'] = first_name 
                    poet_obj['middle_name'] = middle_name 
                    poet_obj['last_name'] = last_name
                    poet_obj['error'] = 'Not Found' 
                    return poet_obj
                
                a_tag = search_result.select_one('div.mw-search-result-heading > a')
                href = a_tag.attrs['href']
                # print(f'{i} {poet_name}: {href}')
                # if 'list' in href:
                #     continue
                # H. D.
                # Check if the res appears to be a poet, x "tries" and if it is false return "poet not found"
                poet = None
                if await verify_poet(href=href, poet_name=poet_name, session=session, headers=headers):
                    poet = await scrape_poet_data_wiki(poet_name=poet_name, href=href, session=session)
                    # print(f'{i} {poet_name}: {poet}')
                    # print(poet)
                    error = None
                    if poet != None:
                        error = poet.get('error')
                    if not poet or error is not None:
                        # print('sjsj')
                        print('!JJJJLLLJJJJJLLLLJJJJJLLLL!')
                        raise Exception('Not found')
                    poet_obj = poet

                if poet_obj: 
                    break
            
            # This may be able to be removed
            if poet_obj is None:
                poet_obj = await get_poet_data_wiki_retry(poet_name=poet_name, session=session)
                raise Exception('Not found')
            # else:
            #     first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
            #     poet_obj['first_name'] = first_name
            #     poet_obj['middle_name'] = middle_name
            #     poet_obj['last_name'] = last_name
            #     poet_obj['error'] = None
            


            return poet_obj
        except Exception as e:
            print(e)
            poet_obj = get_poet_obj(poet_name=poet_name, error=str(e))
            return poet_obj



async def get_poet_data_wiki_retry(poet_name: str, session):
    print('get_poet_data_wiki_retry called')
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    # https://en.wikipedia.org/w/index.php?title=Elizabeth_Coatsworth&action=info 
    # ^ Local Description / Central Description Could contian whether or not the page is for a poet or writer
    # 'poet' 'writer' 'critic'
    p_name_split = poet_name.split()
    p_name_search_format = '+'.join(p_name_split)
    url = f'https://en.wikipedia.org/w/index.php?search={p_name_search_format}&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1'

    
    print(url)
    # res = requests.get(url, headers=headers, allow_redirects=True)
    async with session.get(url, headers=headers) as response:
        html_data = await response.text()
    poet_obj = {}

    soup = BeautifulSoup(html_data, 'html.parser')

    search_results = soup.find_all('li', class_="mw-search-result mw-search-result-ns-0")
    if len(search_results) == 0:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
        poet_obj['first_name'] = first_name 
        poet_obj['middle_name'] = middle_name 
        poet_obj['last_name'] = last_name
        poet_obj['error'] = 'Not Found' 
        return poet_obj
        
    for i, search_result in enumerate(search_results):
        if i == 3: 
            # BF*: poet_obj not null therefore error in obj returning None
            first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
            poet_obj['first_name'] = first_name 
            poet_obj['middle_name'] = middle_name 
            poet_obj['last_name'] = last_name
            poet_obj['error'] = 'Not Found' 
            return poet_obj
        
        a_tag = search_result.select_one('div.mw-search-result-heading > a')
        href = a_tag.attrs['href']
        # print(f'{i} {poet_name}: {href}')
        # if 'list' in href:
        #     continue
        # H. D.
        # Check if the res appears to be a poet, x "tries" and if it is false return "poet not found"
        poet = None
        if await verify_poet(href=href, poet_name=poet_name, session=session, headers=headers):
            poet = await scrape_poet_data_wiki(poet_name=poet_name, href=href, session=session)
            # print(f'{i} {poet_name}: {poet}')
            # print(poet)
            error = None
            if poet != None:
                error = poet.get('error')
            if not poet or error is not None:
                # print('sjsj')
                first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
                poet_obj['first_name'] = first_name
                poet_obj['middle_name'] = middle_name
                poet_obj['last_name'] = last_name
                poet_obj['error'] = 'Not Found' 
                print('!JJJJLLLJJJJJLLLLJJJJJLLLL!')
                return poet_obj

            poet_obj = poet

        if poet_obj: 
            break
    
    # This may be able to be removed
    if poet_obj is None:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
        poet_obj['first_name'] = first_name
        poet_obj['middle_name'] = middle_name
        poet_obj['last_name'] = last_name
        poet_obj['error'] = 'Not Found' 
    else:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
        poet_obj['first_name'] = first_name
        poet_obj['middle_name'] = middle_name
        poet_obj['last_name'] = last_name
        poet_obj['error'] = None
    
    return poet_obj
     

async def verify_poet(href: str, poet_name: str, session, headers: dict[str,str]):
    wiki_url = f"https://en.wikipedia.org{href}"
    print('URL:', wiki_url)
    print('VERIFY:', poet_name)
    print(href, 'alkfjasl;fjk')
    
    # res = requests.get(wiki_url, headers=headers, allow_redirects=True)
    # https://en.wikipedia.org/w/index.php?title=Louise_Morey_Bowman&action=info
     # https://en.wikipedia.org/w/index.php?title=Elizabeth_Coatsworth&action=info
    # await asyncio.sleep(5)
   
    # if await verify_poet_info_page(wiki_url=wiki_url, headers=headers, session=session) == False:
    #     return False
    # ^ Local Description / Central Description Could contian whether or not the page is for a poet or writer
    # 'poet' 'writer' 'critic'
    # await asyncio.sleep(5)
    async with session.get(wiki_url, headers=headers, allow_redirects=True) as res:
        html_data = await res.text()

    href_test = href.lower()
    if ('list' in href_test and 'of' in href_test) or 'prize' in href_test or 'women' in href_test:
        return False
    


    soup = BeautifulSoup(html_data, 'html.parser')

    # percent correct
    
    h1 = soup.find('h1', class_='firstHeading mw-first-heading')
    # h1_text = h1.get_text().lower().split()
    h1_text_split = h1.get_text().lower().split()
    print(h1_text_split, 'checking the split')
    if 'biography' in h1_text_split:
        return False
    

    html_str = str(soup)
    if 'This is a list of prominent Punjabi people from the United Kingdom who may follow a variety of beliefs including Sikhism, Hinduism, Islam, Christianity or atheism. ' in html_str:
        return False

    if 'This is a list of notable Sikhs from the United Kingdom.' in html_str or 'This is an alphabetical list of internationally notable poets.' in html_str or 'poet' not in html_str or 'may refer to: ' in html_str: 
        return False
    print('***HERE')

    p = soup.find('p', class_=False)
    if p:
        if not verify_poet_from_p(p=p.get_text().lower()):
            print('Herrrre')
            return False
    print('^^^^^^^^^^^^^^')
    if p and '.' not in poet_name:
        p_text = p.text
        if poet_name in p_text:
            return True 

    
    # checking if the names are the same
    if h1:
        # breaking poet name param and poet name from page into parts
        h1_text = h1.text.lower()
        h1_split = h1_text.split()
        if h1_split[-1] == '(poet)':
            h1_split = h1_split[:-1]
        pn_split = poet_name.lower().split()
        print(pn_split, 'flsadjfls')

        # the case for names without periods
        if '.' not in poet_name:
            i = 0
            cnt = 0
            while i < len(h1_split):
                if h1_split[i] in pn_split:
                    cnt += 1

                i += 1
            # Different cases for judging similarity based on potential different lengths
            if len(h1_split) == len(pn_split):
                while i < len(h1_split):
                    if h1_split[i] in pn_split:
                        cnt += 1
                    i += 1
                if cnt != len(h1_split):
                    return False
            elif len(h1_split) > len(pn_split):
                print(h1_split[-1], 'jj')
                print(pn_split[-1], 'jj')
                if h1_split[0] != pn_split[0] or h1_split[-1] != pn_split[-1]:
                    return False
                
                while i < len(h1_split):
                    if h1_split[i] in pn_split:
                        cnt += 1
                    i += 1
                ratio = cnt / len(pn_split)
                if len(h1_split) == 1 and len(pn_split) > 1 and ratio < 1:
                    return False



                if ratio <= .39:
                    return False
            elif len(h1_split) < len(pn_split):
                while i < len(h1_split):
                    if h1_split[i] in pn_split:
                        cnt += 1
                    i += 1
                ratio = cnt / len(pn_split)
                if ratio <= .39:
                    return False


            ratio = cnt / len(pn_split)
            if ratio <= .39:
                return False
        
        # names that contain a period
        elif '.' in poet_name:
            # case for h1 names that would be split into an array of len(1) (ie. H.D.)
            surname_set = {'mrs.', 'mr.', 'ms.', 'dr.', 'prof.', 'sir', 'lady', 'lord', 'rev.', 'fr.', 'sr.', 'jr.', 'esq.'}

           
            # pn_split = poet_name.split()
            if h1_split[0] in surname_set:
                h1_split = h1_split[1:]        
            if h1_split[-1] in surname_set:
                h1_split = h1_split[:-1]

            if pn_split[0] in surname_set:
                pn_split = pn_split[1:]        
            if pn_split[-1] in surname_set:
                pn_split = pn_split[:-1]
            
            print(h1_split, '&&&&&&&')
            print(pn_split, '&&&&&&&')

            if len(h1_split) == 1:
                if poet_name.lower() != h1_text:
                    return False
            elif len(h1_split) == len(pn_split):
                i = 0
                cnt = 0
                while i < len(h1_split):
                    if '.' in h1_split[i] and '.' not in pn_split[i]:
                        if h1_split[i][0] == pn_split[i][0]:
                            print('.inH1')
                            cnt += 1
                    elif '.' in pn_split[i] and '.' not in h1_split[i]:
                        if h1_split[i][0] == pn_split[i][0]:
                            print('.inPNS')
                            cnt += 1
                    else:
                        if h1_split[i].lower() == pn_split[i]:
                            cnt += 1
                    i += 1
                print(cnt, 'count')
                print(h1_split, 'lenght')
                if cnt != len(h1_split):
                    return False
                # if h1_split[0] != pn_split[0] and h1_split[-1] != pn_split[-1]:
                #     return False
            elif len(h1_split) < len(pn_split):
                if h1_split[0] != pn_split[0] and h1_split[-1] != pn_split[-1]:
                    return False
            elif len(h1_split) > len(pn_split):
                 if h1_split[0] != pn_split[0] and h1_split[-1] != pn_split[-1]:
                    return False

    print('AHAHAHHAHAH')
    # J. F. C. Fuller
    return True

def verify_poet_from_p(p):
    print('verify_poet_from_p triggered')
    # res = requests.get(wiki_url, headers=headers, allow_redirects=True)
    # https://en.wikipedia.org/w/index.php?title=Louise_Morey_Bowman&action=info
    # https://en.wikipedia.org/w/index.php?title=Elizabeth_Coatsworth&action=info
    # /wiki/Alice_Corbin_Henderson
    

    occupation_set = {
        'writer', 'critic', 'poet', 'author', 'artist', 'playwright', 'novelist', 'essayist', 'lyricist', 
        'dramatist', 'journalist', 'biographer', 'satirist', 'librettist', 'storyteller', 'scribe', 'bard', 
        'versifier', 'rhymester', 'wordsmith',
        'writer,', 'critic,', 'poet,', 'author,', 'artist,', 'playwright,', 'novelist,', 'essayist,', 'lyricist,', 
        'dramatist,', 'journalist,', 'biographer,', 'satirist,', 'librettist,', 'storyteller,', 'scribe,', 'bard,', 
        'versifier,', 'rhymester,', 'wordsmith,',
        'writer.', 'critic.', 'poet.', 'author.', 'artist.', 'playwright.', 'novelist.', 'essayist.', 'lyricist.', 
        'dramatist.', 'journalist.', 'biographe.,', 'satirist.', 'librettist.', 'storyteller.', 'scribe.', 'bard.', 
        'versifier.', 'rhymester.', 'wordsmith.'
    }

    opening_article = {
        'is an', 'is a', 'was a', 'was an',
        'is the', 'was the',
        'is one', 'was one',
        'is best', 'was best',
        'is widely', 'was widely',
        'is perhaps', 'was perhaps',
        'is primarily', 'was primarily',
        'is known', 'was known',
        'is considered', 'was considered',
        'is regarded', 'was regarded',
        'is recognized', 'was recognized',
        'is remembered', 'was remembered',
        'is celebrated', 'was celebrated',
        'is noted', 'was noted',
        'is notable', 'was notable',
    }

    paragraph_parts = p.split()
    

    print(paragraph_parts)

    for i in range(1, len(paragraph_parts)):
        # poetential_article_string = clean_string(f'{paragraph_parts[i-1]} {paragraph_parts[i]}')
        poetential_article_string = f'{paragraph_parts[i-1]} {paragraph_parts[i]}'
        # word_cleaned_1 = clean_string(paragraph_parts[i])
        # word_cleaned_0 = clean_string(paragraph_parts[[i-1]])
        # poetential_article_string = f'{word_cleaned_0} {word_cleaned_1}'
        print(poetential_article_string)
        if poetential_article_string not in opening_article:
            continue
        print(i)
        if i + 3 < len(paragraph_parts):
            print(poetential_article_string)
            j = i + 1
            while j < i + 3:
                if paragraph_parts[j] in occupation_set:
                    print('()()(HERE)')
                    return True
                j += 1
    
    # for part in paragraph_parts:
    #     if part.lower() in occupation_set:
    #         return True
    
    return False


async def verify_poet_info_page(wiki_url, headers, session):
    print('verify_poet_info_page triggered')
    # res = requests.get(wiki_url, headers=headers, allow_redirects=True)
    # https://en.wikipedia.org/w/index.php?title=Louise_Morey_Bowman&action=info
    # https://en.wikipedia.org/w/index.php?title=Elizabeth_Coatsworth&action=info
    # /wiki/Alice_Corbin_Henderson
    endpoint = wiki_url.split('/')[-1]
    print(endpoint, '::::::::DfSDFS')


    url = f'https://en.wikipedia.org/w/index.php?title={endpoint}&action=info'
    for i in range(0,10):
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            html_data = await response.text()

        occupation_set = {
            'writer', 'critic', 'poet', 'author', 'artist', 'playwright', 'novelist', 'essayist', 'lyricist', 
            'dramatist', 'journalist', 'biographer', 'satirist', 'librettist', 'storyteller', 'scribe', 'bard', 
            'versifier', 'rhymester', 'wordsmith'
        }

        soup = BeautifulSoup(html_data, 'html.parser')
        if not soup:
            continue
            raise Exception(f'Status error: {response.status}')

        # not_found = soup.find('b')
        # if not_found:
        #     if not_found.get_text() == 'Wikipedia does not have an article with this exact name.':
        #         return False
        basic_information_table = soup.find('table', class_='wikitable mw-page-info')
        if not basic_information_table:
            await asyncio.sleep(180)
            continue
            # raise Exception(f'Status error: {response.status} 382')
            return False
        table_rows = basic_information_table.find_all('tr')
        for row in table_rows:
            tds = row.find_all('td')
            if not tds:
                continue
            header = tds[0]
            if not header: continue
            header_text = header.get_text().lower()
            if not header_text: continue
            if header_text != 'local description' and header_text != 'central description': continue
            description = tds[-1]
            if not description: continue
            description_text = description.get_text().lower()
            description_text_split = description_text.split()
            for part in description_text_split:
                if part.lower() in occupation_set:
                    return True
        return False

    return False

def compare_names_with_period(tag_name, poet_name):
    print('compare_names_with_period triggered')
    surname_set = {'mrs.', 'mr.', 'ms.', 'dr.', 'prof.', 'sir', 'lady', 'lord', 'rev.', 'fr.', 'sr.', 'jr.', 'esq.'}

    tag_name_split = tag_name.split()
    poet_name_split = poet_name.split()
    if tag_name_split[0] in surname_set:
        tag_name_split = tag_name_split[1:]        
    if tag_name_split[-1] in surname_set:
        tag_name_split = tag_name_split[:-1]

    if poet_name_split[0] in surname_set:
        poet_name_split = poet_name_split[1:]        
    if tag_name_split[-1] in surname_set:
        poet_name_split = poet_name_split[:-1]
        

        
    if len(tag_name_split) == 1:
        if poet_name.lower() != tag_name:
            return False
    elif len(tag_name_split) == len(poet_name_split):
        i = 0
        cnt = 0
        while i < len(tag_name_split):
            if '.' in tag_name_split[i] and '.' not in poet_name_split[i]:
                if tag_name_split[i][0] == poet_name_split[i][0]:
                    cnt += 1
            elif '.' in poet_name_split[i] and '.' not in tag_name_split[i]:
                if tag_name_split[i][0] == poet_name_split[i][0]:
                    cnt += 1
            else:
                if tag_name_split[i] == poet_name_split[i]:
                    cnt += 1
            i += 1
        
        if cnt != len(tag_name_split):
            return False
    elif len(tag_name_split) < len(poet_name_split):
        if (tag_name_split[0] != poet_name_split[0] and tag_name_split[-1] != poet_name_split[-1]) and (tag_name_split[0][0] != poet_name_split[0][0] and tag_name_split[-1][0] != poet_name_split[-1][0]):
            return False
    elif len(tag_name_split) > len(poet_name_split):
        if (tag_name_split[0] != poet_name_split[0] and tag_name_split[-1] != poet_name_split[-1]) and (tag_name_split[0][0] != poet_name_split[0][0] and tag_name_split[-1][0] != poet_name_split[-1][0]):
            return False
    
    return True




async def scrape_poet_data_wiki(poet_name: str, href: str, session):
    print('scrape_poet_data_wiki triggered')
    print('poet start::', poet_name)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    p_name_split = poet_name.split()
    p_name_search_format = '+'.join(p_name_split)
    p_name_wiki_format = '_'.join(p_name_split)

    

    wiki_url = f"https://en.wikipedia.org{href}"
    print(wiki_url)
    nationality_dict = {
        'England': 'English', 'U.S.': 'American', 'Switzerland': 'Swiss',
        'France': 'French', 'Germany': 'German', 'Italy': 'Italian',
        'Spain': 'Spanish', 'Russia': 'Russian', 'Canada': 'Canadian',
        'Australia': 'Australian', 'Ireland': 'Irish', 'Northern Ireland': 'Ireland', 
        'Scotland': 'Scottish', 'Wales': 'Welsh', 'Netherlands': 'Dutch', 
        'Belgium': 'Belgian', 'Austria': 'Austrian', 'Poland': 'Polish', 
        'Czech Republic': 'Czech', 'Sweden': 'Swedish', 'Norway': 'Norwegian', 
        'Denmark': 'Danish', 'Finland': 'Finnish', 'Greece': 'Greek', 'Portugal': 'Portuguese',
        'Japan': 'Japanese', 'China': 'Chinese', 'India': 'Indian','Brazil': 'Brazilian', 
        'Argentina': 'Argentinian', 'Mexico': 'Mexican', 'South Africa': 'South African', 
        'New Zealand': 'New Zealand', 'United Kingdom of Great Britain and Ireland' : 'British',
        'United States' : 'American', 'United Kingdom': 'British', 'Ukraine': 'Ukranian'
    }  # AI win moment  # AI win moment
    async with session.get(wiki_url, headers=headers, allow_redirects=True) as res:
        html_data = await res.text()

        poet_obj = {}

        if res.status != 200:
            raise Exception(f"Failed to fetch data for {poet_name}. Status code: {res.status}")
    print('80808080808080808')
    print('08080808080808080')
    print('80808080808080808')
    print('08080808080808080')
    
    soup = BeautifulSoup(html_data, 'html.parser')

    # all for when the poet wiki page is accessed 
    main = soup.find('main', class_='mw-body')

    main_content = main.select_one('div.mw-content-ltr.mw-parser-output')
    p = main_content.find('p', class_=False)

    header_tag = main.find('header', class_='mw-body-header')
    h1 = header_tag.find('h1')  # Name in h1
    name_text = h1.text  # Name text from page
    alt_names = []
    if name_text.lower() != poet_name.lower():
        # If it's likely a middle initial or abbreveated part is causing the inequality
        if '.' in poet_name:
            if compare_names_with_period(name_text, poet_name):
                alt_names.append(poet_name)
                poet_name = name_text
                print(poet_name, '---------')

                print('uuuuuuuuuuuu')
            else:
                alt_names.append(name_text)
                print('oooooooooooo')
            # if poet_name == al
            # name_text_split = name_text.lower().split()  # from wikipedia
            # poet_name_split = poet_name.lower().split()  # from param
           
            # i = 0
            # while i < len(poet_name_split):
            #     if '.' in poet_name_split[i]:
            #         break

            #     i += 1
            
            
            
            # if name_text_split[i][0] != poet_name_split[i][0]:
            #     print('------------') tentative removal
            #     return None
                
            
        else:
            name_text_split = name_text.split()
            poet_name_split = poet_name.split()  # from param
            # print(name_text_split)
            # print(poet_name_split)
            print('Here')
            # if p:
                
            if len(name_text_split) != len(poet_name_split):
                pass
            else:
                pass
    
    # main_content = main.select_one('div.mw-content-ltr.mw-parser-output')

    poet_obj['alt_names'] = alt_names
   
    
    # p = main_content.find('p', class_=False)
    # print(len(p.text))
    # print(p.text)
    # return
    # 
    if p and 'may refer to:' in p.text:
        error_text = 'Not found'
        raise Exception(error_text)

    # >> inital name here
    # 'clause' (if/else) that catches the greater proportion of inputs
    first_name, middle_name, last_name = None, None, None

    if '.' in poet_name:
        inital_name = handle_initial_names(poet_name=poet_name, h1_name=h1.text)
        if inital_name != '':
            first_name = inital_name
        else:
            first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
    else:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)

    # poet_obj['first_name'] = first_name
    # poet_obj['middle_name'] = middle_name
    # poet_obj['last_name'] = last_name
    print(alt_names)
    alt_name = get_alt_names(p=p, alt_names=alt_names)
    alt_names.append(alt_name)

    # if name has a "." and name other wise matched
    # AND character of . equals 
    # bio starts with name

    profile_picture_url = None

    info_box = main.select_one('table.infobox')
    # Getting poet details
    # Getting details when there is an info box
    if info_box:
        print('^^^^^^^^')
        info_box_keys = {'born', 'died', 'nationality'}
        img_tag = info_box.find('img')

        
        if img_tag:
            print('Here')
            profile_picture_url = await scrape_img_data_wiki(img_tag=img_tag, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers, session=session)
        info_box_labels = info_box.select('th.infobox-label')

        for info_box_label in info_box_labels: 
            info_box_key = info_box_label.text
            table_data = info_box_label.find_next_sibling('td')

            if info_box_key.lower() != 'born':
                continue

            if not table_data:
                continue
            
            birth_place = table_data.select_one('div.birthplace')
           
            
            birth_place_text = ''
            bp_href_text = ''
            if birth_place:
                birth_place_a = birth_place.find('a')
                if birth_place_a:
                    bp_href = birth_place_a.attrs.get('href')
                    if bp_href != 'href' or bp_href != None:
                        bp_href_text = bp_href
                birth_place_text = birth_place.text
            nationality_text = ''
            if bp_href_text != '':
                birth_country = await get_nationality_from_location_wiki_new(birth_place_href=bp_href_text, session=session)
                if birth_country != '':
                    nationality_text = nationality_dict[birth_country]
            else:
                # The way I see this now is that there is no HREF, therefore a search is required to get the nationality and birthplace
                # Going to do something sick here to get the 'birth place' when there is no Href
                
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                birth_country = ''
                if len(birth_place_text) > 1:
                    birth_place_text, birth_country = await get_nationality_from_wiki_search(birth_place_text=birth_place_text, session=session)
                
                if birth_country != '':
                    nationality_text = nationality_dict[birth_country]
                # raise Exception(birth_place_text)
                # birth_place_split = birth_place_text.split(',')
                # print(birth_place_split)
                # if len(birth_place_split) > 0:
                #     print('**************')
                #     if len(birth_place_split) == 2:
                #         nationality_text = 'American'
                #     elif len(birth_place_split) == 3:
                #         get_nationality_from_wiki_search(birth_place_text)

                #     else:
                #         birth_place_split_last = birth_place_split[-1].strip()
                #         nationality_text = nationality_dict[birth_place_split_last]

            # Balmont
            # 15 June [O.S. 3 June] 1867
            # Shuya, Russia
            bday = table_data.select_one('span.bday')
            bday_text = ''
            year_text = ''
            if bday:
                bday_text = bday.text
            else:
                contents = table_data.contents
                num_br = len([content for content in contents if isinstance(content, Tag) and content.name == 'br'])
                text_before_br = ''
                j = 0
                for i, content in enumerate(contents):
                    if hasattr(content, 'name'):
                        if content.name == 'br':
                            j += 1
                        elif isinstance(content, NavigableString):
                            text_before_br += content.strip()
                    elif isinstance(content, NavigableString): 
                        text_before_br += content.strip()

                    if j == num_br:
                        break
                
                year_text = text_before_br
                print('year_text', year_text)

           
            birth_date= format_date_to_us_long(year_text) if bday_text == '' else convert_iso_8601(iso_8601_date=bday_text)
            nationality = 'American' if 'Territory' in birth_place_text else nationality_text
            return get_poet_obj(poet_name=poet_name, birth_date=birth_date, nationality=nationality, birth_place=birth_place_text, profile_picture_url=profile_picture_url, alt_names=alt_names, error=None)
            # poet_obj['birth_date'] = format_date_to_us_long(year_text) if bday_text == '' else convert_iso_8601(iso_8601_date=bday_text)
            # poet_obj['nationality'] = 'American' if 'Territory' in birth_place_text else nationality_text
            # poet_obj['birth_place'] = birth_place_text
            # poet_obj['profile_picture_url'] = profile_picture_url
    # Getting poet details with no infobox
    else: 

        # find poetential portaigt down this path.. 
        # could use fig caption..
        # look for name + name (param) 
        # to find last name ( from name or name (param) ) or full name ( from name or name (param) )

        profile_picture_url = await scrape_img_from_body_wiki(soup=main, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers, session=session)
        print('--=-=-=-=-=-----')

        # Extract birthdate
        if not p:
            return None
        p_text = p.text
        bday_text = extract_date_from_p(p_text=p_text)
        bday_text = bday_text if bday_text != '' else ''

        if bday_text is not None and len(bday_text) > 0 and ('[' in bday_text or ']' in bday_text):
            bday_text = remove_brackets_from_string(bday_text)
        # print(bday_text)

        # "Bio Header" to obtain "birthplace" and "nationality"
        bio_header = main_content.find('div', class_='mw-heading mw-heading2')

        # if bio_header contains biography OR early life, the wikipedia "signals" for that

        birth_place_text = '' # leveraged for poet details
        birth_country = '' # leveraged for poet details
        nationality_text = '' # leveraged for poet details


        bio = bio_header.find_next_sibling('p')
        if bio:
            birth_place_text, birth_place_href = extract_birth_place_from_p_new(p=bio)
            birth_place_text = birth_place_text if birth_place_text != '' else ''
    

        if birth_place_text != '':
            birth_country = await get_nationality_from_location_wiki_new(birth_place_href=birth_place_href, session=session)
        
        if birth_country != '':
            nationality_text = nationality_dict.get(birth_country)
            # nationality_text = nationality_text if nationality_text != '' or na else '' 
        return get_poet_obj(poet_name=poet_name, birth_date=bday_text, nationality=nationality_text, birth_place=birth_place_text, profile_picture_url=profile_picture_url, alt_names=alt_names, error=None)


    return poet_obj

def format_full_name(poet_name: str):
    if poet_name is None or poet_name == '':
        return None, None, None
    # print(poet_name, 'in func')
    pn_split = poet_name.split()

    surname_set = {'mrs.', 'mr.', 'ms.', 'dr.', 'prof.', 'sir', 'lady', 'lord', 'rev.', 'fr.', 'sr.', 'jr.', 'esq.'}


    if pn_split[0].lower() in surname_set and pn_split[-1].lower() in surname_set:
        first_name, middle_name, last_name = format_full_name(poet_name=' '.join(pn_split[1:-1]))
        return first_name, middle_name, last_name
    
    elif pn_split[0].lower() in surname_set:
        first_name, middle_name, last_name = format_full_name(poet_name=' '.join(pn_split[1:]))
        return first_name, middle_name, last_name
    
    elif pn_split[-1].lower() in surname_set:
        first_name, middle_name, last_name = format_full_name(poet_name=' '.join(pn_split[:-1]))
        return first_name, middle_name, last_name
    
    elif len(pn_split) == 1:
        first_name = pn_split[0]
        return first_name, None, None

    elif len(pn_split) == 2:
        first_name = pn_split[0]
        last_name = pn_split[-1]
        return first_name, None, last_name

    else:
        first_name = pn_split[0]
        last_name = pn_split[-1]
        pn_split[1:-1]
        middle_name = ' '.join(pn_split[1:-1])
        
        return first_name, middle_name, last_name


def handle_initial_names(poet_name, h1_name):
    if '.' not in poet_name:
        return ''
    
    pn_split = poet_name.split()

    h1_split = h1_name.strip().split('.')

    # print(poet_name, 'before')
    # print(h1_name, 'before')
    # print(pn_split, 'before')
    # print(h1_split, 'before')

    # if len(pn_split) == len(h1_split):
    # if h1_split[-1] == '' and len(pn_split) == len(h1_split):
    if h1_split[-1] == '':
        # print(h1_name, 'in block')
        h1_split = h1_split[0:-1]
        i = 0
        n = len(pn_split)
        while i < n:
            if '.' not in pn_split[i]:
                return ''
            
            if pn_split[i][0:-1].lower() != h1_split[i].lower():
            # if ' '.join(pn_split[]i[i:-1]).lower() != h1_split[i].lower():
                return ''

            i += 1
        
        # ex. 'H. D.' -> 'H.D.'
        # print(h1_name, 'jhgjg')
        print(h1_split, '=========')
        print(pn_split, '=========')
        return h1_name
    else:
        return ''


def get_alt_names(p: Tag | NavigableString, alt_names: list):
    # p = soup.find('p', class_=False)
    p_text = p.text
    p_text_split = p_text.split('(')

    # print(p_text_split[0])

    # alt_names.append(p_text_split[0].strip())
    
    return p_text_split[0].strip()

#
async def scrape_img_data_wiki(img_tag: Tag | NavigableString, poet_name: str, p_name_wiki_format: str, headers: dict[str, str], session):
    async with wikimedia_sem_info_box:
        img_src = img_tag.attrs['src']
        # print(img_src)  ✅
        await asyncio.sleep(5)
        timeout = aiohttp.ClientTimeout(connect=60*5, sock_connect=60*5, sock_read=60*5)
        async with session.get(f'https:{img_src}', headers=headers, timeout=timeout) as res:
            image_data = await res.read()
        # res = requests.get(f'https:{img_src}', headers=headers, stream=True)

            if res.status != 200: 
                raise Exception(f"Failed to fetch image data for {poet_name}. Status code: {res.status}")

            poet_name_format = p_name_wiki_format.lower()
            file_path = f'tmp/{poet_name_format}_portrait.jpg'
            try:
                with open(file_path, 'wb') as f:  # open for writing - truncating the file first, binary mode
                    # res.raw.decode_content = True
                    # shutil.copyfileobj(res.raw, f)
                    f.write(image_data)

                profile_picture_url = upload_poet_to_s3(file=file_path, poet_name=poet_name_format)
                return profile_picture_url
            
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)


# The actual exit point....

#
async def scrape_img_from_body_wiki(soup: Tag | NavigableString, poet_name: str, p_name_wiki_format: str, headers: dict[str, str], session):
    async with wikimedia_sem_no_info_box:
        
        if not soup: return ''
        print('scrape_img_from_body_wiki triggered')
        # pot_imgs = soup.find_all('img', class_='mw-file-element')
        pot_figs = soup.find_all('figure', class_='mw-default-size')
        if not pot_figs:
            print('sfsladjf')
            return ''
        poet_name_parts = poet_name.split()
        img_src = ''

        # Find potential poet portraits from images from figure elements
        for pot_fig in pot_figs:
            pot_img = pot_fig.find('img', class_='mw-file-element')
            
            if pot_img:
                pot_img_attrs = pot_img.attrs
                pot_alt = pot_img_attrs.get('alt')
                print(pot_img_attrs)
                if pot_alt:
                    if poet_name_parts[0] in pot_alt or poet_name_parts[1] in pot_alt or 'portrait' in pot_alt:
                        img_src = pot_img.attrs['src']
                
                if img_src != '':
                    break

                pot_cap = pot_fig.find('figcaption')
                if img_src == '' and pot_cap is not None:
                    # print('pot_cap', pot_cap)
                    pot_cap_text = pot_cap.text
                    if len(poet_name_parts) > 1:
                        if poet_name_parts[0].lower() in pot_cap_text.lower() or poet_name_parts[1].lower() in pot_cap_text.lower():
                            img_src = pot_img.attrs['src']
                    else:
                        if poet_name_parts[0] in pot_cap_text:
                            img_src = pot_img.attrs['src']

            if img_src != '':
                break
        
        if img_src == '':
            return None
    

    timeout = aiohttp.ClientTimeout(connect=60*5, sock_connect=60*5, sock_read=60*5)
    # res = requests.get(f'https:{img_src}', headers=headers, stream=True)
    status = None
    image_data = None
    for i in range(0, 3):
        async with session.get(f'https:{img_src}', headers=headers, timeout=timeout) as res: 
            # -> ?
            # print(img_src, ':::::::')
            if res.status != 200:
                await asyncio.sleep(10)
                status = res.status
                continue
            else:
                image_data = await res.read()
                status = res.status
                break
            
            
          
    if 200 > status or 299 < status:
        raise Exception(f"Failed to fetch image data for {poet_name}. Status code: {res.status}")

    try: 
        poet_name_format = p_name_wiki_format.lower()
        file_path = f'tmp/{poet_name_format}_portrait.jpg'
        with open(file_path, 'wb') as f:  # open for writing - truncating the file first, binary mode
            # res.raw.decode_content = True
            # shutil.copyfileobj(res.raw, f)
            f.write(image_data)
        profile_picture_url =  upload_poet_to_s3(file=file_path, poet_name=poet_name_format)
        return profile_picture_url
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    # except:
    #     t

def get_poet_obj(
    poet_name: str | None ,  
    birth_date: str | None = None, 
    nationality: str | None = None, 
    birth_place: str | None = None, 
    profile_picture_url: str | None = None, 
    alt_names: list[str] | None = None, 
    error: str | None = None
) -> dict:
    print('get_poet_obj triggered')
    # first_name, middle_name, last_name = '', '', ''
    # if '.' in poet_name:
    #     inital_name = handle_initial_names(poet_name=poet_name, h1_name=h1.text)
    #     if inital_name != '':
    #         first_name = inital_name
    #     else:
    #         first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
    # else:
    #     first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
    print(profile_picture_url, ')()()()()()()()()()()()')
    first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
    if birth_place and nationality is None:
        birth_place = None
    poet_obj = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "birth_date": birth_date if birth_date != None or birth_date != '' else None,
        "nationality": nationality if nationality != None or nationality != '' else None,
        "birth_place": birth_place if birth_place != None or birth_place != '' else None,
        "alt_names": alt_names if alt_names != None else [],
        "profile_picture_url": profile_picture_url if profile_picture_url != None or profile_picture_url != '' else None,
        "error": error if error else None,
    }
    return poet_obj

def upload_poet_to_s3(file, poet_name):
    print('upload_poet_to_s3 triggered')
    """

    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False

    """

    bucket_name = 'lrt-pub-bucket'
    uuid_slice = str(uuid.uuid4())[:8]
    key = f'poets/{poet_name}_{uuid_slice}'
    portrait_url = f'https://d3eqbj00kgn0hf.cloudfront.net/{key}'

    # If S3 object_name was not specified, use file_name
    # if object_name is None:
    #     object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.resource('s3')

    try:
        s3_client.Bucket(bucket_name).upload_file(Filename=file, Key=key, ExtraArgs={'ContentType': 'image/jpeg'})

    except ClientError as e:
        logging.error(e)
        return None
    
    return portrait_url

#  ISO 8601 format '1883-11-10'
def convert_iso_8601(iso_8601_date: str):
    print('convert_iso_8601 triggered')
    iso_date_split = iso_8601_date.split('-')

    print(iso_8601_date, 'HAHAHAH')
    month_dict = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    if len(iso_date_split) == 1:
        return iso_8601_date
    # May have to have someting for non standard format, ie if either a date or month is missing
    return f'{month_dict[iso_date_split[1]]} {iso_date_split[2]}, {iso_date_split[0]}'

def format_date_to_us_long(date: str):
    print('format_date_to_us_long triggered')
    if date == None or date == '':
        return ''
    
    date_split_ = date.split()
    date_split = []

    for date_part in date_split_:
        dp = ''
        for p in date_part:
            if p.isalnum():
                dp += p
        date_split.append(dp)   

    
    month_dict = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    months_set = {'january', 'february', 'march', 'april', 'may', 'june', 
                  'july', 'august', 'september', 'october', 'november', 'december'}
    print('||||||||||||||||||||||||||||||')


    if len(date_split) == 0:
        return ''
    elif len(date_split) == 1:
        return date_split[0]
    elif len(date_split) == 2:
        if date_split[0] in months_set:
            return f'{date_split[0]}, {date_split[1]}'
        else:
            return f'{date_split[1]}, {date_split[0]}'
    else:
        if date_split[0].lower() in months_set:
            return f'{date_split[0]} {date_split[1]}, {date_split[2]}'
        
        # if date appears to be the first slice
        elif date_split[0].isnumeric() and len(date_split[0]) <= 2 and date_split[-1].isnumeric() and len(date_split[-1]) > 2:
            return f'{date_split[1]} {date_split[0]}, {date_split[-1]}'
        # if year appears to be the first slice
        elif date_split[0].isnumeric() and len(date_split[0]) > 2 and date_split[-1].isnumeric() and len(date_split[-1]) <= 2:
            return f'{date_split[1]} {date_split[0]}, {date_split[-1]}'
        else:
            return f'{date_split[1]} {date_split[2]}, {date_split[3]}'
            return f'{date_split[1]} {date_split[2]}, {date_split[3]}'

        # if len(date_split[0]) > 2:
        #     return f'{date_split[2]} {date_split[1]}, {date_split[0]}'

# 
def extract_date_from_p(p_text: str):
    print('extract_date_from_p triggered')
    months_set = {'January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'}
    
    pot_date_strings = []
    
    i = 0
    while i < len(p_text):
        if p_text[i] == '(':
            j = i + 1
            while p_text[j] != ')':
                j += 1
            pot_date_string = p_text[i+1:j]
            pot_date_strings.append(pot_date_string)
            i = j
        i += 1
    # print(pot_date_strings)
    for pot_date_string in pot_date_strings:
        pds_split = pot_date_string.split()
        # print(pot_date_string, 'afjklsd')
        if pds_split[0] in months_set:
            pds_target_arr = pds_split[0:3]
            return ' '.join(pds_target_arr)
        elif '–' in pds_split:
            pds_comma_split = pot_date_string.split('–')
            pot_bday = pds_comma_split[0].strip()
            pot_bday_split = pot_bday.split()
            if not pot_bday_split: continue
            print([pot_bday_split, 'fls;ajkslfjasldjfsa;ldjfsl;aj'])
            if len(pot_bday_split) == 3:
                return f'{pot_bday_split[1]} {pot_bday_split[0]}, {pot_bday_split[2]}'
            elif len(pot_bday_split) == 2:
                return f'{pot_bday_split[1]}, {pot_bday_split[0]}'

            # print(pot_bday, 'hola')

            # FloatingPointError
        else: continue

#
def remove_brackets_from_string(string: str) -> str:
    string_split = string.split()
    bracket_index_dict = {}
    for i, s in enumerate(string_split):
        if '[' in s or ']' in s:
            s_cleaned = []
            for j in range(len(s)):
                if s[j] == '[' or s[j] == ']': continue
                s_cleaned.append(s[j])
            if len(s_cleaned) > 0: 
                bracket_index_dict[i] = str(s_cleaned)
    
    for i in range(len(string_split)):
        if i in bracket_index_dict:
            string_split[i] = bracket_index_dict[i]
    
    return ' '.join(string_split)






# 
def extract_birth_place_from_p_new(p: Tag | NavigableString):
    print('extract_birth_place_from_p_new triggered')
    # p_split = p_text.split('.')[0]
    # print(p_text, " djdjjd ")
    # print(p)
    potential_locations = p.find_all('a')
    poetential_location_title = ''
    poetential_location_href = ''
    for potential_location in potential_locations:
        # print(potential_location)
        title = potential_location.get('title')
        if not title:
            continue
        # print(title)
        title_split = title.split()
        for part in title_split:
            if ',' in part or 'Territory' in part:
                href = potential_location.attrs['href']

                poetential_location_title = title
                poetential_location_href = href
                break

        if poetential_location_title != '':
            break
    
    
    return poetential_location_title, poetential_location_href

# 
def extract_birth_place_from_p(p_text: str):
    # immidiately use the parameter (in this one )
    p_split = p_text.split('.')
    # print(p_split[0])

    pot_birth_place = p_split[0]
    pot_birth_place_split = pot_birth_place.split()
    start_search_idx = None
    i = 0
    while i < len(pot_birth_place_split):
        if pot_birth_place_split[i] == 'born':
            start_search_idx = i
            break
        i += 1
    
    pot_locations = []
    pot_birth_place_split = pot_birth_place_split[i + 1:]
    i = 0
    while i < len(pot_birth_place_split):
        if ',' in pot_birth_place_split[i]:
            pot_location = (pot_birth_place_split[i], pot_birth_place_split[i+1])
            pot_locations.append(pot_location)
        i += 1
    

    # Something to verify that it's a place could be in the loop..
    # Clean "brackets" from date
    location = ''
    for pot_location in pot_locations:
        pot_city = pot_location[0]
        pot_state = pot_location[1]

        pot_state_clean = clean_string(value=pot_state)
        pl_string = pot_city + ' ' + pot_state_clean

        is_verified = verify_location_wiki(location=pl_string)
        if is_verified:
            location = pl_string
            break
    
    # print(location)
    return location

def verify_location_wiki_new(location: str) -> bool:

    pass

def verify_location_wiki(location: str) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    location_format = location.split()
    location_format = "_".join(location_format)

    url = f'https://en.wikipedia.org/wiki/{location_format}'
    res = requests.get(url, headers=headers, allow_redirects=True)

    soup = BeautifulSoup(res.content, 'html.parser')
    not_found = soup.find('noarticletext mw-content-ltr')

    return False if not_found else True

async def get_nationality_from_location_wiki_new(birth_place_href: str, session):
    print('get_nationality_from_location_wiki_new triggered')
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    url = f'https://en.wikipedia.org{birth_place_href}'
    print(url, '*******')
    # res = requests.get(url, headers=headers, allow_redirects=True)
    async with session.get(url, headers=headers) as res:
        html_content = await res.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    not_found = soup.find('noarticletext mw-content-ltr')

    if not_found: 
        return ''
    
    info_box = soup.find('table', class_='infobox')
    if not info_box:
        return None
    labels = info_box.find_all('th', class_='infobox-label')
    # https://en.wikipedia.org/wiki/Willard,_New_York *******
    # This is a place that doesnt have an 'Infobox'
    # I dont want to make the code to compensate for this right now


    print('WE MADE IT')
    data_text = ''
    for label in labels: 
        if label.text == 'Country':
            data = label.find_next_sibling('td')
            data_text = data.text.strip()
            break
    
    return data_text

# /opt/homebrew/bin/python3.13
async def get_nationality_from_wiki_search(birth_place_text, session):
    # get href for birth place wiki article
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    nationality_dict = {
        'England': 'English', 'U.S.': 'American', 'Switzerland': 'Swiss',
        'France': 'French', 'Germany': 'German', 'Italy': 'Italian',
        'Spain': 'Spanish', 'Russia': 'Russian', 'Canada': 'Canadian',
        'Australia': 'Australian', 'Ireland': 'Irish', 'Northern Ireland': 'Ireland', 
        'Scotland': 'Scottish', 'Wales': 'Welsh', 'Netherlands': 'Dutch', 
        'Belgium': 'Belgian', 'Austria': 'Austrian', 'Poland': 'Polish', 
        'Czech Republic': 'Czech', 'Sweden': 'Swedish', 'Norway': 'Norwegian', 
        'Denmark': 'Danish', 'Finland': 'Finnish', 'Greece': 'Greek', 'Portugal': 'Portuguese',
        'Japan': 'Japanese', 'China': 'Chinese', 'India': 'Indian','Brazil': 'Brazilian', 
        'Argentina': 'Argentinian', 'Mexico': 'Mexican', 'South Africa': 'South African', 
        'New Zealand': 'New Zealand', 'United Kingdom of Great Britain and Ireland' : 'British',
        'United States' : 'American', 'United Kingdom': 'British', 'Ukraine': 'Ukranian',
        'Bangladesh': 'Bangladeshi'
    }  # AI win moment

    birth_place_text_split = birth_place_text.split(',')
    address_idx = None
    # making a decision here on whether or not this includes an address or not
    for i, birth_place_part in enumerate(birth_place_text_split):
        birth_place_part_split = birth_place_part.split()
        for part in birth_place_part_split:
            if part.isnumeric():
                address_idx = i
                break
    
    if address_idx != None:
        birth_place_part_split = birth_place_part_split[i+1:]
    
    if birth_place_text_split[-1] in nationality_dict:
        birth_place_text_split = birth_place_text_split[:-1]
    
    # if birth_place_part_split
    stripped_split = []
    for i in birth_place_text_split:
        stripped_split.append(i.strip())
    birth_place_text_search_format_parts = []
    for birth_place_part in stripped_split:
        space_delimited = ''
        if ' ' in birth_place_part:
            space_delimited = '+'.join(birth_place_part.split())
            birth_place_text_search_format_parts.append(space_delimited)
        else:
            birth_place_text_search_format_parts.append(birth_place_part)
            

    birth_place_text_search_format = '%2C+'.join(birth_place_text_search_format_parts)
    href = await get_nationality_search_result(birth_place_text, birth_place_text_search_format=birth_place_text_search_format, session=session)

    # country = ''
    # state = ''
    # city = ''
    # county
    location_names = {'city', 'town', 'village', 'municipality', 'district', 'parish',
        'province', 'state', 'territory', 'prefecture', 'department',
        'canton', 'borough', 'township', 'commune', 'arrondissement', 'oblast',
        'governorate', 'emirate', 'kingdom', 'republic', 'country', 'nation', 
        'sovereign state', 'ceremonial county', 'province', 'constituent country', 'area',
        'region'}
    
    # scraping the actual page
    url = f'https://en.wikipedia.org/wiki/{href}'  # *
    async with session.get(url, headers=headers) as response:
        html_content = await response.text()
    # print(html_content)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    heading = soup.find('h1', class_='firstHeading mw-first-heading')
    if not heading:
        return '', ''
    heading_text = heading.text

    # body_content = soup.find('div', class_='mw-body-content')
    # paragraphs = body_content.find('p').text()
    # if not paragraphs:
    #     return 
    # p_text = body_content.find('p').text().lower()
    # likely_country_string = 'is a country'
    # if likely_country_string in p_text:
    #     # logic for setting birth place and nationality
    #     # input likely repersents a country
    #     return
    
    # city = None
    # likely_city_string = 'city'
    # if likely_city_string in p_text:
    #     # what I'd do if this were a city
    #     pass

    # likely_borough_string = 'borough'  # should be an href / <a>

    # likely_township_string = 'township' # should be an href / <a>

    # likely_municipality_string = 'municipality' # should be an href / <a>

    base_location = None
    location_dictionary = {}
    info_box = soup.find('table', class_='infobox')
    # when wiki page has no infobox
    if not info_box:
        return '', ''
    
    info_box_subheader = info_box.find('td', class_='infobox-subheader')
    # when infobox has no subheader
    if not info_box_subheader:
        # may add that original 'p' logic here
        body_content = soup.find('div', class_='mw-body-content')
        # paragraph = body_content.find('p').text()
        paragraph = body_content.find('p')
        if not paragraph:
            return '', ''
        poetential_location_links = paragraph.find_all('a')
        for link in poetential_location_links:
            link_text = link.get_text()
            if link_text and link_text.lower() in location_names:
                base_location = link_text.lower()
                break
        ## the act of being at 'one line' and jumping to another
        # this is when I could technically still run the dict function, but just get nationality
        if not base_location:
            return '', ''
        
    
    if not base_location:
        base_location = info_box_subheader.text.lower()
        # may add that original 'p' logic here
        # may add that in a method
        # return '', ''

    # location = ''
    info_box_rows = info_box.find_all('tr')
    for info_box_row in info_box_rows:
        info_box_row_header = info_box_row.find('th')
        if not info_box_row_header: continue
        info_box_row_details = info_box_row.find('td')
        if not info_box_row_details: continue
        info_box_row_header_text = info_box_row_header.text.strip()
        if not info_box_row_header_text: continue
        if info_box_row_header_text.lower() in location_names:
            location_dictionary[f'{info_box_row_header_text.lower()}'] = info_box_row_details.text.strip()
    
      
    # likely_birth_place = ''
    # likely_nationality = ''

    likely_birth_place, likely_nationality = get_birthplace_nationality_from_dict(heading_text=heading_text, base_location=base_location, location_dictionary=location_dictionary)
    print('@@@@@@@@@@@@0000000000000000@@@@@@@@@@@@@@@@@@@@@')

    return likely_birth_place, likely_nationality

    
    # threoretically, if something like 'city' is in the base location

def get_birthplace_nationality_from_dict(heading_text, base_location, location_dictionary):

    # country = location_dictionary.get('country')
    # if not country:
    #     # return logic
    #     return '', ''
    # # Splitting for birthplaces with commas
    print(location_dictionary)

    # the intended return values
    likely_birth_place = ''
    likely_nationality = ''

    # potential locations and associated significance
    location_significance = {
        'neighborhood': 0,
        'distict': 0,
        'area': 0,
        'hamlet': 1,
        'grant': 1,
        'plantation': 1,
        'village': 1,
        'parish': 1,
        'civil parish': 1,
        'town': 2,
        'city': 2,
        'independent city': 2,
        'borough':2,
        'township': 2,
        'townland': 2,
        'municiplaity': 3,
        'regional municipality': 3,
        'province': 4,
        'state': 4,
        'region': 5,
        'ceremonial county': 6,
        'territory': 6,
        'consituent country': 6,
        'country': 7,
        'sovereign state': 8 
    }

    # potential keys
    location_dict_keys = list(location_dictionary.keys())
    # print(location_dict_keys, 'flskfjlsj')
    # key significance dictionary
    location_dictionary_signinficance = [(key, location_significance[key]) for key in location_dict_keys if key in location_significance]
    print(location_dictionary_signinficance, 'flskjflskj')
    location_dictionary_signinficance_sorted = sorted(location_dictionary_signinficance, key=lambda loc_key_sig: loc_key_sig[1])

    #
    heading_text_split = base_location.split(',')
    # Whent the heading is already formatted favorably
    if len(heading_text_split) > 1:
        likely_birth_place = heading_text
        likely_nationality =  location_dictionary_signinficance_sorted[-1][0]  # logic for this  # some error with east sussex
        return likely_birth_place, likely_nationality
        
    # ranks

    # determine next in significance to base_location (base significance)
    base_value = None
    if base_location.lower() not in location_significance:
        print('@@@@@@@@@@@@0000000000i000000@@@@@@@@@@@@@@@@@@@@@')
        # exhaust potential matches
        location_significance_keys = list(location_significance.keys())
        for key in location_significance_keys:
            # print(key)
            if key not in base_location.lower():
                continue
            base_value = location_significance[key]
            break
        if not base_value:
            # Return when the birth_place cannot be determined
            #
            # likely_birth_place = ''
            likely_nationality = location_dictionary_signinficance_sorted[-1][0]
            return likely_birth_place, likely_nationality
    
    if not base_value:
        base_value = location_significance[base_location]
    
    print(location_dictionary_signinficance_sorted, ';;;;;;;;')
    parent_location = None
    # use base location's associated significance to get direct parent location 
    for loc_sig in location_dictionary_signinficance_sorted:
        if loc_sig[1] > base_value and location_dictionary[loc_sig[0]].lower() != heading_text.lower():
            print(loc_sig[0], '[[[[[[]]]]]]')
            parent_location = location_dictionary[loc_sig[0]]
            break
    
    if not parent_location:
        # Return when the birth_place cannot be determined
        #
        likely_nationality = location_dictionary_signinficance_sorted[-1][0]
        return likely_birth_place, likely_nationality 
    print(parent_location, '}}}}}}}]]]]]')


    likely_birth_place = f'{heading_text}, {parent_location}'
    likely_nationality = location_dictionary[location_dictionary_signinficance_sorted[-1][0]]  # some kind of country deunym dict

    return likely_birth_place, likely_nationality

    
    
    # if ('city' in base_location or 'borough' in base_location or 'town' in base_location or 'township' in base_location
    #     or 'municipality' in base_location or 'hamlet' in base_location or 'grant' in base_location
    #     or 'plantation' in base_location):
    #     soverign_state = base_location.get('sovereign state')
    #     if soverign_state:
    #         # UK nomenclature
    #         pass
        
    #     if country == 'United States':

    #         pass


    #     likely_birth_place = f'{base_location}, {location_dictionary['state'] or }'

    #     pass
    
    # if 'area' in base_location:
    #     likely_birth_place = f'{base_location}, {location_dictionary['region']}'
    #     # logic for nationality using 'country'

    
async def get_nationality_search_result(birth_place_text, birth_place_text_search_format, session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    url = f'https://en.wikipedia.org/w/index.php?search={birth_place_text_search_format}&title=Special%3ASearch&ns0=1&searchToken=9ik7q9wcaxv4hyb81y8tfv38'
    print(url)
    async with session.get(url, headers=headers) as response:
        html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    heading = soup.find('h1')
    if not heading:
        raise Exception('Not found location')
    
    if heading.text.lower() in birth_place_text.lower():
        redirect_url = str(response.url)
        redirect_url_split = redirect_url.split('/')
        print(redirect_url_split[-1], ':::::')
        return redirect_url_split[-1]
        # return 

    search_result = soup.find('li', class_="mw-search-result mw-search-result-ns-0")
    if search_result == None:
        raise Exception('Not found location')  # may do something different here
    a_tag = search_result.select_one('div.mw-search-result-heading > a')
    href = a_tag.attrs['href']

    return href



def get_nationality_from_location_wiki(location: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    # print(location, 'jdjdj')
    location_format = location.split()
    location_format = "_".join(location_format)

    url = f'https://en.wikipedia.org/wiki/{location_format}'
    res = requests.get(url, headers=headers, allow_redirects=True)

    soup = BeautifulSoup(res.content, 'html.parser')
    not_found = soup.find('noarticletext mw-content-ltr')

    if not_found: 
        return ''
    
    info_box = soup.find('table', class_='infobox')
    labels = info_box.find_all('th', class_='infobox-label')
    data_text = ''
    for label in labels: 
        if label.text == 'Country':
            data = label.find_next_sibling('td')
            data_text = data.text.strip()
            break
    
    return data_text




 
def clean_string(value: str):
    res = ''
    for v in value:
        if v.isalpha():
            
            res += v
            
    
    return res


# working toward automating this...

async def main():
    # poet = "Richard Aldington" ✅
    # poet = "William Vaughn Moody"  # ✅ + assuming nationality (american)
    # poet = "Lily Augusta Long" -- May not have found the page..
    
    # poet = "Lily Augusta Long"  # ✅
    # poet = "Lily A. Long"  # ✅
    # poet = "H.D." ✅
    # poet = "H. D." # ✅ verify poet
    # poet = "Margaret Widdemer"  # ✅
    # poet = "Madison Cawein"  # ✅
    # poet = "Ezra Pound"  # ✅
    # poet = "Joseph Campbell"  # ✅
    # poet = "Charles Hanson Towne"  # 
    # poet = "Grace Hazzard Conkling"  # ✅
    # poet = "Fannie Stearns Davis"  # ✅
    # poet = "Arthur Davison Ficke"  # ✅
    # poet = "Alice Meynell" ✅


    
    # try: 
    #     poet_obj = get_poet_data_wiki_entry(poet_name=poet)
    #     print(poet_obj)


    # except Exception as e:
    #     print(e)
    
    # data = None
    # with open('ouput__.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)

    # poet_names = []
    # for d in data:
    #     poet = d['poet']
    #     if poet not in poet_names:
    #         poet_names.append(poet)
  
    # poet_objs = []
    # # try:
    # #     # pass
    #     for i, poet in enumerate(poet_names):
    #         print(poet, f'curr: {i +1}/{len(poet_names)}')
    #         # print(poet, f'curr: {i +1}')
    #         poet_obj = get_poet_data_wiki_entry(poet_name=poet)
    #         poet_objs.append(poet_obj)

    #     errors = []
    #     flac = []
    #     for poet_obj in poet_objs:
    #         error = poet_obj.get('error')
    #         print(error)
    #         if error != None:
    #             print(poet_obj)
    #             print('\n')

        
    #     # for f in flac:
    #         # print(f)

    #     print('\n')
    #     # print('\n')
    #     # print('\n')

    #     # for e in errors:
    #     #     print(e)
    #     #     print('\n')

    # #     print(len(flac))
    # #     print(len(errors))
       

    # #     # WB Yeats



    # except Exception as e:
    #     print(e)
    try:
        sem = asyncio.Semaphore(30)
        

        poet_names = []
        with open('poets_new.json', 'r', encoding='utf-8') as f:
            poet_names = json.load(f)

        ## 
        # with open('404_poet_objs_new.json_birthplacesearch.json') as f:
        #     p_objs = json.load(f)
        
        # for p in p_objs:
        #     v = format_poet_name_from_obj(p)
        #     if not v: continue
        #     poet_names.append(v)
        ##

        # poet_names = []
        # for poet_name in poet_names_test:
        #     if '.' in poet_name:
        #         poet_names.append(poet_name)

        # poet_names = ['T. Sturge Moore'] error was '"East Sussex"'
        # poet_names = ['Elizabeth J. Coatsworth', Robert Redfield Jr., Florence D. Snelling] error was list index out of range
        # poet_names = ['Reginald H. Wilenski', ] error was list index out of range but found
        # H.D.
        # Charles Hanson -- poet error none all else empty / not found
        # emilia stuart lorimer -- poet error none all else empty / not found
        # helen dudley -- poet error none all else empty / not found
        # anita fitch -- poet error none all else empty / not found
        # kendall banning -- poet error none all else empty / not found
        # samuel mccoy -- poet error none all else empty / not found

        # Controls
        # {'first_name': 'Schuyler', 'middle_name': 'Van', 'last_name': 'Rensselaer', 'error': 'Not Found'}
        # {'first_name': 'E.', 'middle_name': None, 'last_name': 'W.', 'error': 'Not Found'}

        # Different error
        # {'alt_names': ['Edith Franklin Wyatt'], 'first_name': 'Edith', 'middle_name': None, 'last_name': 'Wyatt', 'birth_date': 'September 14, 1873', 'nationality': '', 'birth_place': '', 'profile_picture_url': None, 'error': None}


        # poet_names = poet_names[:10]
        # .. basically, i need to change my bucket policy to this ip
        # poet_names = ['James Branch Cabell', 'Conrad Aiken']
        # poet_names = ['Lew R. Sarett', "John R. C. Peyton", "A.N."]
        # poet_names = ['Lew r. Sarett']
        # poet_names = ['h.d.']
        # poet_names = ['Konstantin Balmont']  #bday thing
        # poet_names = ['Arthur Symons']  # list index out of range thing
        # poet_names = ['Ella Young']  # list index out of range thing
        # poet_names = ['Eve Brodlique Summers']  # list index out of range thing
        # poet_names = ['Stella Benson']  # list index out of range thing ✅
        # poet_names = ['Elizabeth J. Coatsworth']  # exists but not found
        # poet_names = ['Isidor Schneider']  # title ✅
        # poet_names = ['Alice Corbin Henderson']  # Not location found
        # poet_names = ['Robert Nichols']  # Not location found
        # poet_names = ['Robert Frost']  # Connecction timeout to host ✅
        # poet_names = ['Hubert Trench']  # Connecction timeout to host ✅
        # poet_names = ['Morris Bishop']  # None has no attribute find_all ✅
        # poet_names = ['Nancy Campbell']  # verify bug
        # poet_names = ['William Vaughn Moody'] # verify bug 
        # poet_names = ['Helen Hoyt']  # verify bug
        # poet_names = ['Robert Graves']  # verify bug
        # poet_names = ['Muriel Stuart ']  # verify bug len()
        # poet_names = ['James Stephens ']  # birthdate from body [] bug
        # poet_names = ['Robert Gilbert Welsh']  # false positve, dont know why # May have just fixed it
        # poet_names = ['Charles Badger Clark']  # found bug
        # poet_names = ['Lily A. Long'] # verify split bug (-> not found)
        ##
        # poet_names = ['T. Sturge Moore'] # t. sturge thing....  affects the method and the "outside"
        ## prelimarily fixed just, theres someting else wrong with it because he has no other poet details and the poet name (param) should be included in the alts
        # for d in data:
        #     poet = d['poet']
        #     if poet not in poet_names:
        #         poet_names.append(poet)
        # 2318 lines
    # "first_name": "William",
    # "middle_name": "Vaughn",
    # "last_name": "Moody"
        # something for jr in the name
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
    
        poet_objs = []

        async with aiohttp.ClientSession(headers=headers) as session:
            # for name in poet_names:
            poet_obj_tasks = [get_poet_data_wiki_entry(poet_name=poet_name, session=session, sem=sem) for poet_name in poet_names]
            poet_objs = await asyncio.gather(*poet_obj_tasks, return_exceptions=True)
            # print(len(poet_objs))
            # print(poet_objs)

        ##
        # for poet_obj in poet_objs:
        #     # error = poet_obj.get('error')
        #     error2 = poet_obj.get('profile_picture_url')
        #     if error == None and error2 == None:
        #         print(poet_obj)
        found = []
        errors = []
        not_found = []
    #     # for poet_obj in poet_objs:
    #     #     if isinstance(poet_obj, dict):
    #     #         error = poet_obj.get('error')
    #     #         # print('error', error)
    #     #         if error != None:
    #     #             not_found.append(poet_obj)
    #     #             continue
    #     #         found.append(poet_obj)
    #     #     else:
    #     #         continue
        poet_names_backup = []
        for poet_obj in poet_objs:
            if isinstance(poet_obj, dict):
                error = poet_obj.get('error')
                # print('error', error)
                if error != None:
                    if error.lower() != 'not found':
                        name = format_poet_name_from_obj(poet_obj=poet_obj)
                        poet_names_backup.append(name)
                    else:
                        not_found.append(poet_obj)
                    continue
                found.append(poet_obj)
            else:
                continue
        
        

        async with aiohttp.ClientSession() as session:
        # for name in poet_names:
            poet_obj_backup_tasks = [get_poet_data_wiki_entry(poet_name=poet_name, session=session, sem=sem) for poet_name in poet_names_backup]
            poet_objs_backup = await asyncio.gather(*poet_obj_backup_tasks, return_exceptions=True)
            print(len(poet_objs))
            print(poet_objs)
        
        for poet_obj in poet_objs_backup:
            if isinstance(poet_obj, dict):
                error = poet_obj.get('error')
                # print('error', error)
                if error != None:
                    if error.lower() != 'not found':
                        errors.append(poet_obj)
                    else:
                        not_found.append(poet_obj)
                    continue
                found.append(poet_obj)
            else:
                continue
            ##

        
        
        with open('poet_objs_new.json_birthplacesearch.json', 'w', encoding='utf-8') as f:
            json.dump(found, f, indent=2)
        with open('404_poet_objs_new.json_birthplacesearch.json', 'w', encoding='utf-8') as f:
            json.dump(not_found, f, indent=2)
        with open('errror_poet_objs_new.json_birthplacesearch.json', 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2)

        
        

    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())


# to remove
#   "Richard Untermeyer"

# wiki_wiki = wikipediaapi.Wikipedia('LaureatApi (wwdvlps@gmail.com)', 'en')

# page_py = wiki_wiki.page('Lily a long')

# print("Page - Exists: %s" % page_py.exists())

# # print(page_py.sections)

# for s in page_py.sections:
#     if s.title.lower() == 'biography':
#         print(s.text)

# # key words for determining if the page represents a poet
# poet_keywords = {'poet'}

# # nationality dictionary
# nationality_keywords = {}

# wiki logic
    
# ultimate laureate. poem scraper

# ‹main id="content" class="mw-body">  Primary content

# <table class="infobox vcard"> Infobox

# <span class="mw-default-size" typeof="mw:File/Frameless">
# <a href="/wiki/File:H.D._in_Tendencies_in_Modern_American_Poetry,_1917_-_cropped.jpg" class="mw-file-description" title="H.D. c. 1917">
# <img alt="H.D. c. 1917" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0c/H.D._in_Tendencies_in_Modern_American_Poetry%2C_1917_-_cropped.jpg/250px-H.D._in_Tendencies_in_Modern_American_Poetry%2C_1917_-_cropped.jpg" decoding="async" width="250" height="342" class="mw-file-element" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0c/H.D._in_Tendencies_in_Modern_American_Poetry%2C_1917_-_cropped.jpg/375px-H.D._in_Tendencies_in_Modern_American_Poetry%2C_1917_-_cropped.jpg 1.5x, //upload.wikimedia.org/wikipedia/commons/0/0c/H.D._in_Tendencies_in_Modern_American_Poetry%2C_1917_-_cropped.jpg 2x" data-file-width="418" data-file-height="572">
# </a>
# </span>
# <div class="infobox-caption" style="line-height:1.4em;">
# H.D. 
# <abbr title="circa">c.</abbr>
# <span style="white-space:nowrap;"> 1917</span>
# </div>

# Anyways this is how I get the image

# Search by name + "poet"
# Scrape if information available
# Want the first paragraph in a varible, to determine if
# key words indicating a poet are present
# exit if not


# if equal when split or someting (page titile)


# Want to find the infobox.. 
# The infobox will contain Name, Nationality, BD, DD, birthplace, etc
# if there is no infobox, scrape the first paragraph 

# HD -- name formatting, "nickname"




# infobox vcard
# th 'Born' or key (nationality, birthplace)
# ^ sibling td containg date* + location* or data needed
# seperated by 'br' 'birthplace may have birthplace tag ie div.birthplace

# def scrape_poet_data_wiki_og(poet_name: str):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
#     }

#     p_name_split = poet_name.split()
#     p_name_search_format = '+'.join(p_name_split)
#     p_name_wiki_format = '_'.join(p_name_split)

#     search_url = f"https://en.wikipedia.org/w/index.php?search={p_name_search_format}%22&title=Special%3ASearch&ns0=1"
#     wiki_url = f"https://en.wikipedia.org/wiki/{p_name_wiki_format}"

#     nationality_dict = {
#         'England': 'English', 'U.S.': 'American', 'Switzerland': 'Swiss',
#         'France': 'French', 'Germany': 'German', 'Italy': 'Italian',
#         'Spain': 'Spanish', 'Russia': 'Russian', 'Canada': 'Canadian',
#         'Australia': 'Australian', 'Ireland': 'Irish', 'Scotland': 'Scottish',
#         'Wales': 'Welsh', 'Netherlands': 'Dutch', 'Belgium': 'Belgian',
#         'Austria': 'Austrian', 'Poland': 'Polish', 'Czech Republic': 'Czech',
#         'Sweden': 'Swedish', 'Norway': 'Norwegian', 'Denmark': 'Danish',
#         'Finland': 'Finnish', 'Greece': 'Greek', 'Portugal': 'Portuguese',
#         'Japan': 'Japanese', 'China': 'Chinese', 'India': 'Indian',
#         'Brazil': 'Brazilian', 'Argentina': 'Argentinian', 'Mexico': 'Mexican',
#         'South Africa': 'South African', 'New Zealand': 'New Zealand',
#         'United Kingdom of Great Britain and Ireland' : 'British',
#         'United States' : 'American'
#     }  # AI win moment

#     res = requests.get(wiki_url, headers=headers, allow_redirects=True)

#     poet_obj = {}

#     if res.status_code != 200:
#         raise Exception(f"Failed to fetch data for {poet_name}. Status code: {res.status_code}")
    
#     soup = BeautifulSoup(res.content, 'html.parser')

#     # all for when the poet wiki page is accessed 
#     main = soup.find('main', class_='mw-body')

#     info_box = main.select_one('table.infobox.vcard')
#     if info_box:
#         info_box_keys = {'born', 'died', 'nationality'}
#         img_tag = info_box.find('img')

#         if img_tag:
#             scrape_img_data_wiki(img_tag=img_tag, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers)
        
#         info_box_labels = info_box.select('th.infobox-label')

#         for info_box_label in info_box_labels: 
#             info_box_key = info_box_label.text
#             table_data = info_box_label.find_next_sibling('td')

#             if info_box_key.lower() != 'born':
#                 continue

#             if not table_data:
#                 continue
            
#             birth_place = table_data.select_one('div.birthplace')
#             birth_place_text = ''
#             if birth_place:
#                 birth_place_text = birth_place.text


#             nationality_text = ''
#             birth_place_split = birth_place_text.split(',')
#             if len(birth_place_split) > 0:
#                 if len(birth_place_split) == 2:
#                     nationality_text = 'American'
#                 else:
#                     birth_place_split_last = birth_place_split[-1].strip()
#                     nationality_text = nationality_dict[birth_place_split_last]


#             bday = table_data.select_one('span.bday')
#             bday_text = ''
#             year_text = ''
#             if bday:
#                 bday_text = bday.text
#             else:
#                 print(str(table_data).split('<br/>')[0])
#                 contents = table_data.contents
#                 text_before_br = ''
#                 for i, content in enumerate(contents):
#                     if hasattr(content, 'name') and content.name == 'br':
#                         break
#                     if hasattr(content, 'strip'):  # it's a text node
#                         text_before_br += content.strip()
#                     print(f'{i}: {content}')
#                 year_text = text_before_br


#             # When 'US' isnt in the birth place text..
#             # When bday isnt in a standard format / iso8601


#             poet_obj['birth_date'] = year_text if bday_text == '' else convert_iso_8601(iso_8601_date=bday_text)
#             poet_obj['nationality'] = 'American' if 'Territory' in birth_place_text else nationality_text
#             poet_obj['birth_place'] = birth_place_text

#     else:   
#         main_content = main.select_one('div.mw-content-ltr.mw-parser-output')

#         # Extract birthdate
#         p = main_content.find('p')
#         p_text = p.text
#         bday_text = extract_date_from_p(p_text=p_text)

#         # "Bio Header" to obtain "birthplace" and "nationality"
#         bio_header = main_content.find('div', class_='mw-heading mw-heading2')

#         # if bio_header contains biography OR early life, the wikipedia "signals" for that
#         bio = bio_header.find_next_sibling('p')
#         bio_text = bio.text

#         birth_place_text = extract_birth_place_from_p(p_text=bio_text)
#         birth_country = ''
#         if birth_place_text != '':
#             birth_country = get_nationality_from_location_wiki(location=birth_place_text)
        
#         nationality_text = ''
#         if birth_country != '':
#             nationality_text = nationality_dict[birth_country]
        
#         poet_obj['birth_date'] = bday_text if bday_text != '' else ''
#         poet_obj['nationality'] = nationality_text if nationality_text != '' else ''
#         poet_obj['birth_place'] = birth_place_text if birth_place_text != '' else ''

#         # nationality
#         # birth_place
#         # Biography || Early life* - "Margaret Widdemer was born in Doylestown, Pennsylvania" 
#         # -- xx, xx
#         # -- seperate by .?

#         # print(bday_text)
#         # <div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr">
        
#     return poet_obj

# def format_full_name(poet_name: str, alt_names: list):
#     if poet_name is None or poet_name == '':
#         return '', '', ''
    
#     pn_split = poet_name.split()

#     if len(pn_split) == 1:
#         first_name = pn_split[0]
#         return first_name, '', ''

#     elif len(pn_split) == 2:
#         first_name = pn_split[0]
#         last_name = pn_split[-1]
#         return first_name, '', last_name

#     else:
#         first_name = pn_split[0]
#         last_name = pn_split[-1]

#         if '.' not in pn_split[1]:
#             middle_name = pn_split[1]
#             return first_name, middle_name, last_name
        
#         # May not actually need this... IF middle name is K. /initial, ie, it's fine
#         pot_alts = []
#         for alt in alt_names:
#             alt_split = alt.split()
#             if len(alt_split) != len(pn_split):
#                 continue

#             pot_alts.append(alt_split)
    
#     # elif len(pn_split) == 3:
#     #     first_name = pn_split[0]
#     #     last_name = pn_split[-1]

#     #     if '.' not in pn_split[1]:
#     #         middle_name = pn_split[1]
#     #         return first_name, middle_name, last_name
        
#     #     # May not actually need this... IF middle name is K. /initial, ie, it's fine
#     #     pot_alts = []
#     #     for alt in alt_names:
#     #         alt_split = alt.split()
#     #         if len(alt_split) != len(pn_split):
#     #             continue

#     #         pot_alts.append(alt_split)
# birth_country = ''
# if birth_place_text != '':
#     birth_country = get_nationality_from_location_wiki(location=birth_place_text) old method
    # nationality
    # birth_place
    # Biography || Early life* - "Margaret Widdemer was born in Doylestown, Pennsylvania" 
    # -- xx, xx
    # -- seperate by .?

    # print(bday_text)
    # <div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr">

# 4/26/26
# async def scrape_poet_data_wiki(poet_name: str, href: str, session):
#     print('scrape_poet_data_wiki triggered')
#     print('poet start::', poet_name)
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
#     }

#     p_name_split = poet_name.split()
#     p_name_search_format = '+'.join(p_name_split)
#     p_name_wiki_format = '_'.join(p_name_split)

    

#     wiki_url = f"https://en.wikipedia.org{href}"
#     print(wiki_url)
#     nationality_dict = {
#         'England': 'English', 'U.S.': 'American', 'Switzerland': 'Swiss',
#         'France': 'French', 'Germany': 'German', 'Italy': 'Italian',
#         'Spain': 'Spanish', 'Russia': 'Russian', 'Canada': 'Canadian',
#         'Australia': 'Australian', 'Ireland': 'Irish', 'Northern Ireland': 'Ireland', 
#         'Scotland': 'Scottish', 'Wales': 'Welsh', 'Netherlands': 'Dutch', 
#         'Belgium': 'Belgian', 'Austria': 'Austrian', 'Poland': 'Polish', 
#         'Czech Republic': 'Czech', 'Sweden': 'Swedish', 'Norway': 'Norwegian', 
#         'Denmark': 'Danish', 'Finland': 'Finnish', 'Greece': 'Greek', 'Portugal': 'Portuguese',
#         'Japan': 'Japanese', 'China': 'Chinese', 'India': 'Indian','Brazil': 'Brazilian', 
#         'Argentina': 'Argentinian', 'Mexico': 'Mexican', 'South Africa': 'South African', 
#         'New Zealand': 'New Zealand', 'United Kingdom of Great Britain and Ireland' : 'British',
#         'United States' : 'American'
#     }  # AI win moment
#     async with session.get(wiki_url, headers=headers, allow_redirects=True) as res:
#         html_data = await res.text()

#         poet_obj = {}

#         if res.status != 200:
#             raise Exception(f"Failed to fetch data for {poet_name}. Status code: {res.status}")
    
#     soup = BeautifulSoup(html_data, 'html.parser')

#     # all for when the poet wiki page is accessed 
#     main = soup.find('main', class_='mw-body')

#     main_content = main.select_one('div.mw-content-ltr.mw-parser-output')
#     p = main_content.find('p', class_=False)

#     header_tag = main.find('header', class_='mw-body-header')
#     h1 = header_tag.find('h1')  # Name in h1
#     name_text = h1.text
#     alt_names = []
#     if name_text != poet_name:
#         # If it's likely a middle initial or abbreveated part is causing the inequality
#         if '.' in poet_name:
#             name_text_split = name_text.lower().split()
#             poet_name_split = poet_name.lower().split()  # from param
           
#             i = 0
#             while i < len(poet_name_split):
#                 if '.' in poet_name_split[i]:
#                     break

#                 i += 1
            
#             # if name_text_split[i][0] != poet_name_split[i][0]:
#             #     print('------------') tentative removal
#             #     return None
                
            
#             alt_names.append(name_text)
#         else:
#             name_text_split = name_text.split()
#             poet_name_split = poet_name.split()  # from param
#             # print(name_text_split)
#             # print(poet_name_split)
#             print('Here')
#             # if p:
                
#             if len(name_text_split) != len(poet_name_split):
#                 pass
#             else:
#                 pass
    
#     # main_content = main.select_one('div.mw-content-ltr.mw-parser-output')

#     poet_obj['alt_names'] = alt_names
    
#     # p = main_content.find('p', class_=False)
#     # print(len(p.text))
#     # print(p.text)
#     # return
#     # 
#     if p and 'may refer to:' in p.text:
#         first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
#         poet_obj['first_name'] = first_name
#         poet_obj['middle_name'] = middle_name
#         poet_obj['last_name'] = last_name
#         poet_obj['error'] = 'Not found'
#         return poet_obj

#     # >> inital name here
#     # 'clause' (if/else) that catches the greater proportion of inputs
#     first_name, middle_name, last_name = None, None, None

#     if '.' in poet_name:
#         inital_name = handle_initial_names(poet_name=poet_name, h1_name=h1.text)
#         if inital_name != '':
#             first_name = inital_name
#         else:
#             first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
#     else:
#         first_name, middle_name, last_name = format_full_name(poet_name=poet_name)

    
#     poet_obj['first_name'] = first_name
#     poet_obj['middle_name'] = middle_name
#     poet_obj['last_name'] = last_name

#     alt_names = get_alt_names(p=p, alt_names=alt_names)

#     # if name has a "." and name other wise matched
#     # AND character of . equals 
#     # bio starts with name

#     profile_picture_url = None

#     info_box = main.select_one('table.infobox.vcard')
#     # Getting poet details
#     # Getting details when there is an info box
#     if info_box:
#         info_box_keys = {'born', 'died', 'nationality'}
#         img_tag = info_box.find('img')

        
#         if img_tag:
#             print('Here')
#             profile_picture_url = await scrape_img_data_wiki(img_tag=img_tag, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers, session=session)
        
#         info_box_labels = info_box.select('th.infobox-label')

#         for info_box_label in info_box_labels: 
#             info_box_key = info_box_label.text
#             table_data = info_box_label.find_next_sibling('td')

#             if info_box_key.lower() != 'born':
#                 continue

#             if not table_data:
#                 continue
            
#             birth_place = table_data.select_one('div.birthplace')
            
#             # print(birth_place, 'xxxx')
#             birth_place_text = ''
#             bp_href_text = ''
#             # print('Here')
#             if birth_place:
#                 birth_place_a = birth_place.find('a')
#                 if birth_place_a:
#                     bp_href = birth_place_a.attrs.get('href')
#                     if bp_href != 'href' or bp_href != None:
#                         bp_href_text = bp_href
#                 birth_place_text = birth_place.text
#                 # print('birth', birth_place_text)
#             # <div class="birthplace" style="display:inline">
#             #     ‹a href="/wiki/New York_City" title="New York City">
#             #     New York City</a>
#             # </div>

#             nationality_text = ''
#             if bp_href_text != '':
#                 birth_country = await get_nationality_from_location_wiki_new(birth_place_href=bp_href_text, session=session)
#                 if birth_country != '':
#                     nationality_text = nationality_dict[birth_country]

#             else:
#                 birth_place_split = birth_place_text.split(',')
#                 if len(birth_place_split) > 0:
#                     if len(birth_place_split) == 2:
#                         nationality_text = 'American'
#                     else:
#                         birth_place_split_last = birth_place_split[-1].strip()
#                         nationality_text = nationality_dict[birth_place_split_last]

#             # print('BBBBBB')
#             bday = table_data.select_one('span.bday')
#             bday_text = ''
#             year_text = ''
#             if bday:
#                 bday_text = bday.text
#             else:
#                 contents = table_data.contents
#                 num_br = len([content for content in contents if isinstance(content, Tag) and content.name == 'br'])
#                 # print(num_br)
#                 # print(contents)
#                 # print(contents[2].attrs)
#                 text_before_br = ''
#                 j = 0
#                 for i, content in enumerate(contents):
#                     # print(f'{i}: {content}')
#                     # print('-------')
#                     # print(hasattr(content, 'name'))

#                     # print(content.attrs)

#                     if hasattr(content, 'name'):
#                         # print(content)
#                         if content.name == 'br':
#                             j += 1
#                             # break
#                         elif isinstance(content, NavigableString):
#                             text_before_br += content.strip()
#                     elif isinstance(content, NavigableString): 
#                     # elif hasattr(content, 'strip'):  # it's a text node
#                         # print('))))))))))))))')
#                         # print(content)
#                         text_before_br += content.strip()

#                     if j == num_br:
#                         break
#                     # print('__________')
#                 year_text = text_before_br
#                 print('year_text', year_text)
                

#             # print('AAAAA')
#             # print(bday_text)
#             # When 'US' isnt in the birth place text..
#             # When bday isnt in a standard format / iso8601


#             poet_obj['birth_date'] = format_date_to_us_long(year_text) if bday_text == '' else convert_iso_8601(iso_8601_date=bday_text)
#             poet_obj['nationality'] = 'American' if 'Territory' in birth_place_text else nationality_text
#             poet_obj['birth_place'] = birth_place_text
#             poet_obj['profile_picture_url'] = profile_picture_url
#     # Getting poet details with no infobox
#     else: 

#         # find poetential portaigt down this path.. 
#         # could use fig caption..
#         # look for name + name (param) 
#         # to find last name ( from name or name (param) ) or full name ( from name or name (param) )

#         profile_picture_url = await scrape_img_from_body_wiki(soup=main, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers, session=session)

#         # Extract birthdate
#         if not p:
#             return None
#         p_text = p.text
#         bday_text = extract_date_from_p(p_text=p_text)
#         # print(bday_text)

#         # "Bio Header" to obtain "birthplace" and "nationality"
#         bio_header = main_content.find('div', class_='mw-heading mw-heading2')

#         # if bio_header contains biography OR early life, the wikipedia "signals" for that

#         birth_place_text = '' # leveraged for poet details
#         birth_country = '' # leveraged for poet details
#         nationality_text = '' # leveraged for poet details


#         bio = bio_header.find_next_sibling('p')
#         if bio:
#             birth_place_text, birth_place_href = extract_birth_place_from_p_new(p=bio)

#         if birth_place_text != '':
#             birth_country = await get_nationality_from_location_wiki_new(birth_place_href=birth_place_href, session=session)
        
#         if birth_country != '':
#             nationality_text = nationality_dict[birth_country]
        
#         poet_obj['birth_date'] = bday_text if bday_text != '' else ''
#         poet_obj['nationality'] = nationality_text if nationality_text != '' else ''  
#         poet_obj['birth_place'] = birth_place_text if birth_place_text != '' else ''
#         poet_obj['profile_picture_url'] = profile_picture_url


#     print('++++++++++______')
#     print('++++++++++______')  # from param

#     return poet_obj
[{'first_name': 'William', 'middle_name': 'Vaughan', 'last_name': 'Moody', 'error': None}, {'alt_names': ['Ezra Weston Loomis Pound'], 'first_name': 'Ezra', 'middle_name': None, 'last_name': 'Pound', 'birth_date': 'October 30, 1885', 'nationality': 'American', 'birth_place': 'Hailey, Idaho', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/ezra_pound_1dc88040', 'error': None}, {'first_name': 'Emilia', 'middle_name': 'Stuart', 'last_name': 'Lorimer', 'error': None}, {'alt_names': ['Dudley'], 'first_name': 'Helen', 'middle_name': None, 'last_name': 'Dudley', 'error': None}, {'alt_names': ['Grace Walcott Hazard Conkling'], 'first_name': 'Grace', 'middle_name': 'Hazard', 'last_name': 'Conkling', 'birth_date': 'February 07, 1878', 'nationality': 'American', 'birth_place': 'New York City', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/grace_hazard_conkling_cebdcec0', 'error': None}, {'alt_names': ['Joseph Campbell'], 'first_name': 'Joseph', 'middle_name': None, 'last_name': 'Campbell', 'birth_date': 'July 15, 1879', 'nationality': 'Ireland', 'birth_place': 'Belfast, Ireland', 'profile_picture_url': None, 'error': None}, {'alt_names': [], 'first_name': 'Charles', 'middle_name': 'Hanson', 'last_name': 'Towne', 'error': None}, {'alt_names': ['Richard Aldington'], 'first_name': 'Richard', 'middle_name': None, 'last_name': 'Aldington', 'birth_date': 'July 08, 1892', 'nationality': 'English', 'birth_place': 'Portsmouth, Hampshire, England', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/richard_aldington_cc314378', 'error': None}, {'first_name': 'Schuyler', 'middle_name': 'Van', 'last_name': 'Rensselaer', 'error': 'Not Found'}, {'alt_names': ['Lily Augusta Long', 'Lily Augusta Long'], 'first_name': 'Lily', 'middle_name': 'A.', 'last_name': 'Long', 'birth_date': '1862', 'nationality': 'American', 'birth_place': 'St. Paul, Minnesota', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/lily_a._long_6e30b64b', 'error': None}, {'alt_names': ['Harriet Monroe'], 'first_name': 'Harriet', 'middle_name': None, 'last_name': 'Monroe', 'birth_date': 'December 23, 1860', 'nationality': 'American', 'birth_place': 'Chicago, Illinois, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/harriet_monroe_a217b7a0', 'error': None}, {'alt_names': ['Margaret Widdemer'], 'first_name': 'Margaret', 'middle_name': None, 'last_name': 'Widdemer', 'birth_date': 'September 30, 1884', 'nationality': 'American', 'birth_place': 'Doylestown, Pennsylvania', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/margaret_widdemer_012d375f', 'error': None}, {'first_name': 'E.', 'middle_name': None, 'last_name': 'W.', 'error': 'Not Found'}, {'alt_names': ['William Butler Yeats'], 'first_name': 'William', 'middle_name': 'Butler', 'last_name': 'Yeats', 'birth_date': 'June 13, 1865', 'nationality': 'Irish', 'birth_place': 'Sandymount, County Dublin, Ireland', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/william_butler_yeats_133251b0', 'error': None}, {'alt_names': ['John Silas Reed'], 'first_name': 'John', 'middle_name': None, 'last_name': 'Reed', 'birth_date': 'October 22, 1887', 'nationality': 'American', 'birth_place': 'Portland, Oregon, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/john_reed_15da319e', 'error': None}, {'alt_names': ['College of Physicians and Surgeons'], 'first_name': 'George', 'middle_name': None, 'last_name': 'Sterling', 'birth_date': 'December 01, 1869', 'nationality': 'American', 'birth_place': 'Sag Harbor, Suffolk County, New York, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/george_sterling_c32feda0', 'error': None}, {'alt_names': ['Clark Ashton Smith'], 'first_name': 'Clark', 'middle_name': 'Ashton', 'last_name': 'Smith', 'birth_date': 'January 13, 1893', 'nationality': 'American', 'birth_place': 'Long Valley, California, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/clark_ashton_smith_04cf3ebc', 'error': None}, {'alt_names': ['Alice Corbin Henderson'], 'first_name': 'Alice', 'middle_name': None, 'last_name': 'Corbin', 'birth_date': 'April 16, 1881', 'nationality': 'American', 'birth_place': 'St. Louis, Missouri', 'profile_picture_url': None, 'error': None}, {'alt_names': ['Madison Julius Cawein'], 'first_name': 'Madison', 'middle_name': None, 'last_name': 'Cawein', 'birth_date': 'March 23, 1865', 'nationality': 'American', 'birth_place': 'Louisville, Kentucky, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/madison_cawein_84f3a680', 'error': None}, {'first_name': 'Anita', 'middle_name': None, 'last_name': 'Fitch', 'error': None}, {'first_name': 'Kendall', 'middle_name': None, 'last_name': 'Banning', 'error': None}, {'alt_names': ['Edith Franklin Wyatt'], 'first_name': 'Edith', 'middle_name': None, 'last_name': 'Wyatt', 'birth_date': 'September 14, 1873', 'nationality': '', 'birth_place': '', 'profile_picture_url': None, 'error': None}, {'alt_names': ['Ernest Percival Rhys'], 'first_name': 'Ernest', 'middle_name': None, 'last_name': 'Rhys', 'birth_date': 'July 17, 1859', 'nationality': 'English', 'birth_place': 'Islington, London, England', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/ernest_rhys_b5763b6b', 'error': None}, {'first_name': 'Roscoe', 'middle_name': 'W.', 'last_name': 'Brink', 'error': 'Not Found'}, {'alt_names': ['H.D.', 'Hilda Doolittle'], 'first_name': 'H.D.', 'middle_name': None, 'last_name': None, 'birth_date': 'September 10, 1886', 'nationality': 'American', 'birth_place': 'Bethlehem, Pennsylvania, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/h._d._0ec07085', 'error': None}, {'alt_names': ['Harold Witter Bynner'], 'first_name': 'Witter', 'middle_name': None, 'last_name': 'Bynner', 'birth_date': 'August 10, 1881', 'nationality': 'American', 'birth_place': 'New York City, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/witter_bynner_b467c553', 'error': None}, {'error': None}, {'alt_names': ['Frederic Ridgely Torrence'], 'first_name': 'Ridgely', 'middle_name': None, 'last_name': 'Torrence', 'birth_date': 'November 27, 1874', 'nationality': 'American', 'birth_place': 'Xenia, Ohio, U.S.', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/ridgely_torrence_3739ad62', 'error': None}, {'alt_names': ['Alice Christiana Gertrude Meynell'], 'first_name': 'Alice', 'middle_name': None, 'last_name': 'Meynell', 'birth_date': 'October 11, 1847', 'nationality': 'English', 'birth_place': 'Barnes, London, England,  United Kingdom of Great Britain and Ireland', 'profile_picture_url': 'https://d3eqbj00kgn0hf.cloudfront.net/poets/alice_meynell_71439b19', 'error': None}, {'first_name': 'Fannie', 'middle_name': 'Stearns', 'last_name': 'Davis', 'error': None}, {'first_name': 'Samuel', 'middle_name': None, 'last_name': 'McCoy', 'error': None}]