from bs4 import BeautifulSoup
import requests
import json
import re
import time
import aiohttp
import asyncio
import itertools
from playwright.async_api import async_playwright
import playwright_stealth

async def get_poets_from_jstor():
    url = 'https://www.jstor.org/journal/poetry'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Keep False for debugging
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Chicago',
        )
        page = await context.new_page()
        
        # Apply stealth - likely one of these patterns:
        stealth = playwright_stealth.Stealth()
        await stealth.apply_stealth_async(page)
        # OR: await stealth.apply(page)
        # OR: stealth.apply_sync(page)  # if no async version
        
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        print(html[:3000])
        
        input("Press Enter to close browser...")
        await browser.close()
        

async def get_poets_from_jstor_dep():
    url = 'https://www.jstor.org/journal/poetry'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            html_data = await response.text()

        master_source = BeautifulSoup(html_data, 'html.parser')
        print(master_source)

        master_source_main = master_source.find('main')

        master_source_container = master_source_main.find('div', class_='accordion-container')

        # master_source_decade_containers = master_source_container.find_all('details', class_='decade')



        # year_volume_heading = master_source_decade_container.find_all('li', class_='year-volume-heading')
        # year_volume_heading = master_source_decade_container.find_all('li', class_='year-volume-heading')

        # year_volume_list = year_volume_heading.find_all('ol', class_='year-volume-list')  # contains 'data-issues' ie 1919
        year_volume_lists = master_source_container.find_all('ol', class_='year-volume-list')  # contains 'data-issues' ie 1919
        year_volume_lists_filtered = []
        for year_volume_list in year_volume_lists:
            data_issue = year_volume_list.get('data-issues')
            if int(data_issue) < 1920:
                year_volume_lists_filtered.append(year_volume_list)

        # concurrency (will have a certain amount of inner looping)
        

        href_tasks = [get_hrefs(year_volume_list_filtered, session) for year_volume_list_filtered in year_volume_lists_filtered]
        href_lists = await asyncio.gather(*href_tasks, return_exceptions=False)


        # hrefs as volumes
        hrefs = itertools.chain(href_lists)


        # retreiving poet names from volumes
        poet_name_lists_tasks = [get_poets(href, session) for href in hrefs]
        poet_name_lists = await asyncio.gather(*poet_name_lists_tasks, return_exceptions=False)

        # list of poet names
        poet_names = itertools.chain(poet_name_lists)

    return set(poet_names)








    # li_containing_doi = year_volume_list.find_all('li')  # contains 'data-doi' -> containing usable href ie '10.2307/i20572376'






    

    # start of concurrent process



# Get hrefs from li.data_doi -> [href]
async def get_hrefs(year_volume_list, session):
    lis = year_volume_list.find_all('li')
    hrefs = []
    for li in lis:
        data_doi = li.get('data-doi')
        hrefs.appened(data_doi.split('/')[-1])


    return hrefs


# returns list of poets mentioned in the volume
async def get_poets(endpoint: str, session):
    url = f'https://www.jstor.org/stable/{endpoint}'

    async with session.get(url) as response:
        html_data = await response.text()
    
    # source_toc_class = 'toc-export-list'  # ol.
    # source_toc_wrapper_class = 'toc-content-wrapper'  # --> li > div.
    # source_toc_contrib_class = 'contrib'  # --> div. (contains poet text)


    soup = BeautifulSoup(html_data, 'html.parser')

    source_toc = soup.find('ol', class_='toc-export-list')
    source_toc_wrappers = source_toc.select('li > div.toc-content-wrapper')
    
    poet_names = {}
    for source_toc_wrapper in source_toc_wrappers:
        contrib = source_toc_wrapper.find('div', class_='contrib')
        if not contrib:
            continue
        poet_name = contrib.get_text(strip=True)
        if poet_name not in poet_names:
            poet_names.add(poet_name)

    return list(poet_names)



async def get_poets_from_pf():
    url = 'https://www.poetryfoundation.org/poetrymagazine/archive'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    async with aiohttp.ClientSession(
        headers=headers,
        max_line_size=32768,      # 32KB
        max_field_size=32768
    ) as session:
        async with session.get(url) as response:
            html_data = await response.text()

        
        soup = BeautifulSoup(html_data, 'html.parser')
    
        # year volume sections (volumes released in a given year)
        year_volume_sections = soup.find_all('div', class_='relative w-full scroll-smooth lg:pb-16')

        year_volume_sections_filtered = []
        for year_volume_section in year_volume_sections:
            # year volume section loop logic 
            year_div = year_volume_section.find('div', class_='absolute -mt-24 lg:-mt-80')
            year_text = year_div.get('id')
            if not year_text:
                continue
            if int(year_text) > 1920:
                continue
            year_volume_sections_filtered.append(year_volume_section)
        
        
        href_tasks = [get_hrefs_from_volume(year_volume_section) for year_volume_section in year_volume_sections_filtered]
        href_lists = await asyncio.gather(*href_tasks, return_exceptions=False)
         # hrefs for volumes
        hrefs = itertools.chain.from_iterable(href_lists)
        # hrefs_list = list(hrefs)
        # print(hrefs_list)

        # return
        # retreiving poet names from volumes
        poet_name_lists_tasks = [get_poets_from_volume(href, session) for href in hrefs]
        poet_name_lists = await asyncio.gather(*poet_name_lists_tasks, return_exceptions=False)

        
        poet_names = itertools.chain.from_iterable(poet_name_lists)
        # poet_names_list = list(poet_names)
        # for poet in poet_names:
        #     print(poet)
        # return
        poet_names_set = set()
        for poet_name in poet_names:
            # print(poet_name)
            if poet_name in poet_names_set:
                continue
            poet_names_set.add(poet_name)
        poet_names_list = list(poet_names_set)
        




        return poet_names_list


                


        pass



async def get_hrefs_from_volume(year_volume_section):
    year_volumes_ul = year_volume_section.find('ul', class_='flex w-full flex-wrap')
    year_volume_links = year_volumes_ul.select('li > a')

    hrefs = []
    for year_volume_link in year_volume_links:

        # year volume item logic for getting href
        if not year_volume_link:
            continue
        href = year_volume_link.get('href')
        if not href:
            continue
        hrefs.append(href)


    return hrefs


async def get_poets_from_volume(href, session):
    url = f'https://www.poetryfoundation.org{href}'
    print(url)
    async with session.get(url) as response:
        html_data = await response.text()

    soup = BeautifulSoup(html_data, 'html.parser')

    potential_poet_names = soup.find_all('span', class_='type-attribution text-gray-600')

    poet_names = set()
    for potential_poet_name in potential_poet_names:
        poet_name = potential_poet_name.get_text(strip=True)
        if not poet_name: continue
        if poet_name in poet_names: continue
        poet_names.add(poet_name)

    return poet_names

async def dump_poets(poets: list):
    with open('poets_new.json', 'w') as f:
        json.dump(poets, f, indent=2)

async def get_poets_from_json():
    with open('poets_new.json', 'r') as f:
        return json.load(f)
        
    

def get_poems_by_poet():
    pass



async def main():
    # poets = await get_poets_from_pf()
    # await dump_poets(poets)
    poets = await get_poets_from_json()

    # upload poets...

    print(len(poets))




if __name__ == "__main__":
    asyncio.run(main())