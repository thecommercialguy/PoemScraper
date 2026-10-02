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

# import aiohttp

def get_poet_data_wiki_entry(poet_name: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    p_name_split = poet_name.split()
    p_name_search_format = '+'.join(p_name_split)
    url = f'https://en.wikipedia.org/w/index.php?search={p_name_search_format}+poet&title=Special%3ASearch&profile=advanced&fulltext=1&ns0=1'

    res = requests.get(url, headers=headers, allow_redirects=True)

    soup = BeautifulSoup(res.content, 'html.parser')

    search_results = soup.find_all('li', class_="mw-search-result mw-search-result-ns-0")
    poet_obj = {}
    for i, search_result in enumerate(search_results):

        if i == 3: 
            first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
            poet_obj['first_name'] = first_name 
            poet_obj['middle_name'] = middle_name 
            poet_obj['last_name'] = last_name
            poet_obj['error'] = 'Not Found' 
            break
        
        a_tag = search_result.select_one('div.mw-search-result-heading > a')
        href = a_tag.attrs['href']
        print(href)
        # if 'list' in href:
        #     continue
        # H. D.
        # Check if the res appears to be a poet, x "tries" and if it is false return "poet not found"
        poet = None
        if verify_poet(href=href, poet_name=poet_name, headers=headers):
            poet = scrape_poet_data_wiki(poet_name=poet_name, href=href)
            print('out')
            # print(poet)
            if not poet:
                # print('sjsj')
                first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
                poet_obj['first_name'] = first_name
                poet_obj['middle_name'] = middle_name
                poet_obj['last_name'] = last_name
                poet_obj['error'] = 'Not Found' 
                return poet_obj

            poet_obj = poet

        if poet_obj: 
            break
    
    if poet_obj is None:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
        poet_obj['first_name'] = first_name
        poet_obj['middle_name'] = middle_name
        poet_obj['last_name'] = last_name
        poet_obj['error'] = 'Not Found' 
    else:
        poet_obj['error'] = None

    return poet_obj
        

def verify_poet(href: str, poet_name: str, headers: dict[str,str]):
    wiki_url = f"https://en.wikipedia.org/{href}"
    res = requests.get(wiki_url, headers=headers, allow_redirects=True)

    href_test = href.lower()
    if ('list' in href_test and 'of' in href_test) or 'prize' in href_test or 'women' in href_test:
        return False

    soup = BeautifulSoup(res.content, 'html.parser')

    # percent correct
    

    html_str = str(soup)
    if 'This is a list of prominent Punjabi people from the United Kingdom who may follow a variety of beliefs including Sikhism, Hinduism, Islam, Christianity or atheism. ' in html_str:
        return False

    if 'This is a list of notable Sikhs from the United Kingdom.' in html_str or 'This is an alphabetical list of internationally notable poets.' in html_str or 'poet' not in html_str or 'may refer to: ' in html_str: 
        return False

    p = soup.find('p', class_=False)
    if p and '.' not in poet_name:
        
        p_text = p.text
        if poet_name in p_text:
            return True 

    
    
    h1 = soup.find('h1', class_='firstHeading mw-first-heading')
    if h1 and '.' not in poet_name:
        print('lLlLlLlLlLlLlLlLlLlL')
        h1_text = h1.text.lower()
        h1_split = h1_text.split()
        pn_split = poet_name.lower().split()
        i = 0
        cnt = 0
        while i < len(h1_split):
            if h1_split[i] in pn_split:
                cnt += 1

            i += 1

        ratio = cnt / len(pn_split)
        if ratio <= .39:
            return False
    
    return True


def scrape_poet_data_wiki(poet_name: str, href: str):
    print('poet start:', poet_name)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    p_name_split = poet_name.split()
    p_name_search_format = '+'.join(p_name_split)
    p_name_wiki_format = '_'.join(p_name_split)


    # print(href)

    # if 'List' in p_name_split and 'of' in p_name_split:
    #     return None
    print()

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
        'United States' : 'American'
    }  # AI win moment

    res = requests.get(wiki_url, headers=headers, allow_redirects=True)

    poet_obj = {}
    # poet_obj['name'] = poet_name

    # poet_obj['lastName'] = poet_name_split[1]

    if res.status_code != 200:
        raise Exception(f"Failed to fetch data for {poet_name}. Status code: {res.status_code}")
    
    soup = BeautifulSoup(res.content, 'html.parser')

    # all for when the poet wiki page is accessed 
    main = soup.find('main', class_='mw-body')

    header_tag = main.find('header', class_='mw-body-header')
    h1 = header_tag.find('h1')  # Name in h1
    name_text = h1.text
    alt_names = []
    # print(name_text)
    # print(poet_name)
    if name_text != poet_name:
        # If it's likely a middle initial or abbreveated part is causing the inequality
        if '.' in poet_name:
            name_text_split = name_text.split()
            poet_name_split = poet_name.split()  # from param
            i = 0
            while i < len(poet_name_split):
                if '.' in poet_name_split[i]:
                    break

                i += 1
            
            if name_text_split[i][0] != poet_name_split[i][0]:
                return None
                
            
            alt_names.append(name_text)
        else:
            name_text_split = name_text.split()
            poet_name_split = poet_name.split()  # from param
            if len(name_text_split) != len(poet_name_split):
                
                pass
    

    poet_obj['alt_names'] = alt_names

    main_content = main.select_one('div.mw-content-ltr.mw-parser-output')

    p = main_content.find('p', class_=False)
    # print(len(p.text))
    # print(p.text)
    # return
    if p and 'may refer to:' in p.text:
        first_name, middle_name, last_name = format_full_name(poet_name=poet_name)
        poet_obj['first_name'] = first_name
        poet_obj['middle_name'] = middle_name
        poet_obj['last_name'] = last_name
        poet_obj['error'] = 'Not found'
        return poet_obj

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

    
    poet_obj['first_name'] = first_name
    poet_obj['middle_name'] = middle_name
    poet_obj['last_name'] = last_name

    alt_names = get_alt_names(p=p, alt_names=alt_names)

    # if name has a "." and name other wise matched
    # AND character of . equals 
    # bio starts with name

    profile_picture_url = None

    info_box = main.select_one('table.infobox.vcard')
    if info_box:
        info_box_keys = {'born', 'died', 'nationality'}
        img_tag = info_box.find('img')

        
        if img_tag:
            profile_picture_url = scrape_img_data_wiki(img_tag=img_tag, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers)
        
        info_box_labels = info_box.select('th.infobox-label')

        for info_box_label in info_box_labels: 
            info_box_key = info_box_label.text
            table_data = info_box_label.find_next_sibling('td')

            if info_box_key.lower() != 'born':
                continue

            if not table_data:
                continue
            
            birth_place = table_data.select_one('div.birthplace')
            
            # print(birth_place, 'xxxx')
            birth_place_text = ''
            bp_href_text = ''
            # print('Here')
            if birth_place:
                birth_place_a = birth_place.find('a')
                if birth_place_a:
                    bp_href = birth_place_a.attrs.get('href')
                    if bp_href != 'href' or bp_href != None:
                        bp_href_text = bp_href
                birth_place_text = birth_place.text
                # print('birth', birth_place_text)
            # <div class="birthplace" style="display:inline">
            #     ‹a href="/wiki/New York_City" title="New York City">
            #     New York City</a>
            # </div>

            nationality_text = ''
            if bp_href_text != '':
                birth_country = get_nationality_from_location_wiki_new(birth_place_href=bp_href_text)
                if birth_country != '':
                    nationality_text = nationality_dict[birth_country]

            else:
                birth_place_split = birth_place_text.split(',')
                if len(birth_place_split) > 0:
                    if len(birth_place_split) == 2:
                        nationality_text = 'American'
                    else:
                        birth_place_split_last = birth_place_split[-1].strip()
                        nationality_text = nationality_dict[birth_place_split_last]


            bday = table_data.select_one('span.bday')
            bday_text = ''
            year_text = ''
            if bday:
                bday_text = bday.text
            else:
                contents = table_data.contents
                text_before_br = ''
                for i, content in enumerate(contents):
                    if hasattr(content, 'name') and content.name == 'br':
                        break
                    if hasattr(content, 'strip'):  # it's a text node
                        text_before_br += content.strip()
                    print(f'{i}: {content}')
                year_text = text_before_br


            # When 'US' isnt in the birth place text..
            # When bday isnt in a standard format / iso8601


            poet_obj['birth_date'] = year_text if bday_text == '' else convert_iso_8601(iso_8601_date=bday_text)
            poet_obj['nationality'] = 'American' if 'Territory' in birth_place_text else nationality_text
            poet_obj['birth_place'] = birth_place_text
            poet_obj['profile_picture_url'] = profile_picture_url
    else: 

        # find poetential portaigt down this path.. 
        # could use fig caption..
        # look for name + name (param) 
        # to find last name ( from name or name (param) ) or full name ( from name or name (param) )

        profile_picture_url = scrape_img_from_body_wiki(soup=main, poet_name=poet_name, p_name_wiki_format=p_name_wiki_format, headers=headers)

        # Extract birthdate
        # p = main_content.find('p')
        if not p:
            return None
        p_text = p.text
        bday_text = extract_date_from_p(p_text=p_text)
        # print(bday_text)

        # "Bio Header" to obtain "birthplace" and "nationality"
        bio_header = main_content.find('div', class_='mw-heading mw-heading2')

        # if bio_header contains biography OR early life, the wikipedia "signals" for that
        bio = bio_header.find_next_sibling('p')
        bio_text = bio.text

        # birth_place_text = extract_birth_place_from_p(p_text=bio_text)
        birth_place_text, birth_place_href = extract_birth_place_from_p_new(p=bio)

        birth_country = ''
        if birth_place_text != '':
            birth_country = get_nationality_from_location_wiki_new(birth_place_href=birth_place_href)
    
        # birth_country = ''
        # if birth_place_text != '':
        #     birth_country = get_nationality_from_location_wiki(location=birth_place_text) old method
        
        nationality_text = ''
        if birth_country != '':
            nationality_text = nationality_dict[birth_country]
        
        poet_obj['birth_date'] = bday_text if bday_text != '' else ''
        poet_obj['nationality'] = nationality_text if nationality_text != '' else ''
        poet_obj['birth_place'] = birth_place_text if birth_place_text != '' else ''
        poet_obj['profile_picture_url'] = profile_picture_url

        # nationality
        # birth_place
        # Biography || Early life* - "Margaret Widdemer was born in Doylestown, Pennsylvania" 
        # -- xx, xx
        # -- seperate by .?

        # print(bday_text)
        # <div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr">
        
    return poet_obj

def format_full_name(poet_name: str):
    if poet_name is None or poet_name == '':
        return None, None, None
    print(poet_name, 'in func')
    pn_split = poet_name.split()

    surname_set = {'mrs.', 'mr.', 'ms.', 'dr.', 'prof.', 'sir', 'lady', 'lord', 'rev.', 'fr.', 'sr.', 'jr.', 'esq.'}



    if pn_split[0].lower() in surname_set:
        first_name, middle_name, last_name = format_full_name(poet_name=' '.join(pn_split[1:]))
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
        return h1_name
    else:
        return ''
   


def get_alt_names(p: Tag | NavigableString, alt_names: list):
    # p = soup.find('p', class_=False)
    p_text = p.text
    p_text_split = p_text.split('(')

    # print(p_text_split[0])
    alt_names.append(p_text_split[0].strip())
    
    # return alt_names

#
def scrape_img_data_wiki(img_tag: Tag | NavigableString, poet_name: str, p_name_wiki_format: str, headers: dict[str, str]):
    img_src = img_tag.attrs['src']

    res = requests.get(f'https:{img_src}', headers=headers, stream=True)

    if res.status_code != 200: 
        raise Exception(f"Failed to fetch image data for {poet_name}. Status code: {res.status_code}")

    poet_name_format = p_name_wiki_format.lower()
    file_path = f'tmp/{poet_name_format}_portrait.jpg'
    try:
        with open(file_path, 'wb') as f:  # open for writing - truncating the file first, binary mode
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, f)

        profile_picture_url = upload_poet_to_s3(file=file_path, poet_name=poet_name_format)

        return profile_picture_url
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# The actual exit point....

#
def scrape_img_from_body_wiki(soup: Tag | NavigableString, poet_name: str, p_name_wiki_format: str, headers: dict[str, str]):
    if not soup: return ''
    print('scrape img from body')
    # pot_imgs = soup.find_all('img', class_='mw-file-element')
    pot_figs = soup.find_all('figure', class_='mw-default-size')

    poet_name_parts = poet_name.split()
    img_src = ''

    # Find potential poet portraits from images from figure elements
    for pot_fig in pot_figs:
        pot_img = pot_fig.find('img', class_='mw-file-element')
        
        if pot_img:
            pot_img_attrs = pot_img.attrs
            pot_alt = pot_img_attrs.get('alt')
            
            if pot_alt:
                if poet_name_parts[0] in pot_alt or poet_name_parts[1] in pot_alt:
                    img_src = pot_img.attrs['src']

            pot_cap = pot_fig.find('figcaption')
            if img_src == '' and pot_cap is not None:
                # print('pot_cap', pot_cap)
                pot_cap_text = pot_cap.text
                if poet_name_parts[0] in pot_cap_text or poet_name_parts[1] in pot_cap_text:
                    img_src = pot_img.attrs['src']

        if img_src != '':
            break
    

    if img_src == '':
        return None


    res = requests.get(f'https:{img_src}', headers=headers, stream=True)

    if res.status_code != 200: 
        raise Exception(f"Failed to fetch image data for {poet_name}. Status code: {res.status_code}")
    
    poet_name_format = p_name_wiki_format.lower()
    file_path = f'tmp/{poet_name_format}_portrait.jpg'

    try: 
        with open(file_path, 'wb') as f:  # open for writing - truncating the file first, binary mode
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, f)

        profile_picture_url =  upload_poet_to_s3(file=file_path, poet_name=poet_name_format)
        return profile_picture_url
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    
def upload_poet_to_s3(file, poet_name):
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

#
def convert_iso_8601(iso_8601_date: str):
    iso_date_split = iso_8601_date.split('-')

    month_dict = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }

    # May have to have someting for non standard format, ie if either a date or month is missing
    return f'{month_dict[iso_date_split[1]]} {iso_date_split[2]}, {iso_date_split[0]}'

#
def extract_date_from_p(p_text: str):
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
            if len(pot_bday_split) == 3:
                return f'{pot_bday_split[1]} {pot_bday_split[0]}, {pot_bday_split[2]}'
            elif len(pot_bday_split) == 2:
                return f'{pot_bday_split[1]}, {pot_bday_split[0]}'

            # print(pot_bday, 'hola')

            # FloatingPointError
        else: continue

# 
def extract_birth_place_from_p_new(p: Tag | NavigableString):
    # p_split = p_text.split('.')[0]
    # print(p_text, " djdjjd ")
    potential_locations = p.find_all('a')
    poetential_location_title = ''
    poetential_location_href = ''
    for potential_location in potential_locations:
        # print(potential_location)
        title = potential_location.attrs['title']
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

def get_nationality_from_location_wiki_new(birth_place_href: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    url = f'https://en.wikipedia.org{birth_place_href}'
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

def main():
    # poet = "Richard Aldington" ✅
    # poet = "William Vaughn Moody"  # ✅ + assuming nationality (american)
    # poet = "Lily Augusta Long" -- May not have found the page..
    # poet = "Alice Meynell" ✅
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
    poet = "Arthur Davison Ficke"  # ✅


    
    try: 
        poet_obj = get_poet_data_wiki_entry(poet_name=poet)
        print(poet_obj)


    except Exception as e:
        print(e)
    
    # data = None
    # with open('ouput__.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)

    # poet_names = []
    # for d in data:
    #     poet = d['poet']
    #     if poet not in poet_names:
    #         poet_names.append(poet)
  
    # poet_objs = []
    # try:
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


    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()




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