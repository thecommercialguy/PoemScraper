import asyncio
import aiohttp
import requests
import json
# from definitionsScrape import main as scrape_definitions_main
from get_poets_data import format_full_name
# from scraper import main as scrape_poems_main
# from word_api import upload_words_to_laureate

poem_upload_sem = asyncio.Semaphore(20)


async def upload_poems_by_poet_name(poet_name: str, poems: list, session):
    # Check if poet exists in DB
    ## Exists - obtain ID
    ## Doesnt - Scrape + obtain ID
    poet_id = ''
    try: 
        poet_obj = await get_poet_by_name(poet_name=poet_name, session=session)
        if not poet_obj:
            return
        poet_id = poet_obj.get('id')
        if not poet_id: return 
     

        # upload poems to laureate_db asynchronously
        poem_tasks = [upload_poem(poet_id=poet_id, poem=poem, session=session) for poem in poems]
        poem_results = await asyncio.gather(*poem_tasks, return_exceptions=True)

        return {'id': poet_id, 'poet_name': poet_name, 'results': poem_results, 'error': None}
    except Exception as e:
        print(f"Error uploading poems for poet {poet_name}: {e}")
        return {'poet_name': poet_name, 'results': None, 'error': e}
    # print(poem_results)

async def upload_words():
    pass

async def upload_poet(poet, session):
    headers = {'User-Agent': 'MyPythonApp/1.0', 'Accept': 'application/json'}
    url = 'http://localhost:3000/api/poets'
    try:
        async with session.post(url, json=poet, headers=headers) as response:
            data = await response.json()
            # print(data)
            # if int(data['code']) != 200:
            #     return f'eror {poet}'

            return data['data']
    except Exception as e:
        print(f"Error adding poet {poet['first_name']} to laureate.: {e}")
        return e

async def get_poet_by_name(poet_name: str, session):
    headers = {'User-Agent': 'MyPythonApp/1.0', 'Accept': 'application/json'}
    first_name, middle_name, last_name = format_full_name(poet_name=poet_name)

    # first_name = '' if first_name is None else first_name
    # middle_name = '' if middle_name is None else middle_name
    # last_name = '' if last_name is None else last_name
    params = {}
    if first_name:
        params['first_name'] = first_name
    if middle_name:
        params['middle_name'] = middle_name
    if last_name:
        params['last_name'] = last_name

    url = f'http://localhost:3000/api/poets/names'
    try:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            # print(data, 'fdjkl')
            return data['data']
    except Exception as e:
        print(f"Error getting poet {poet_name} by name.: {e}")

async def upload_poem(poet_id: str, poem, session):
    async with poem_upload_sem:
        if poet_id == None or poet_id == '':
            return f'{poem['poet']}: no id'
        headers = {'User-Agent': 'MyPythonApp/1.0', 'Accept': 'application/json'}
        poem_obj = poem.copy()  # Shallow copy
        poem_obj['poet_id'] = poet_id
        del poem_obj['poet']
        # print(poem_obj)
        url = f"http://localhost:3000/api/poems/scraper"
        try:
            async with session.post(url, json=poem_obj, headers=headers) as response:
                data = await response.json()
            if int(data['code']) != 201:
                return f'eror {poem_obj['title']}'
            print(data['data'])
            return data['data']['title']
        except Exception as e:
            print(f"Error uploading poem {poem['title']} to laureate.: {e}")
            return e
        # return {'poet_name': poet_name, 'results': None, 'error': e}






# async def upload_poems(session):
async def upload_poems():
    # ac = 2
    file_name = 'output_new.json'
    with open(file=file_name, mode='r', encoding='utf-8') as f:
        poems = json.load(f)
    # print(poems)
    # with open(file='poet_objs_new_.json', mode='r', encoding='utf-8') as f:
    #     poems = json.load(f)



    # p_set = {'Alice Corbin', 'Ezra Pound', 'William Butler Yeats', 'Arthur Davison Ficke', 'Ernest Rhys', 'Agnes Lee', 'John Reed', 'Witter Brynner', 'Alfred Noyes', 'George Sterling', 'Clark Ashton Smith', 'Margaret Widdmer', 'Richard Aldignton', 'Madison Cawein', 'Alice Meynell', 'Grace Hazard Conkling', 'H.D.', 'Ridgely Torrence', 'Edmund Kemper Broadus', 'Witter Bynner', 'Margaret Widdemer'}

    # p_list = []
    # for p in poems:
    #     pt = p['poet']
    #     if pt in p_set:
    #         continue
    #     p_list.append(p)
    
    # che = set()
    # for p in p_list:
    #     if p['poet'] not in che:
    #         print(p['poet'], '\n')
    #         che.add(p['poet'])
        
            
    #     Lily A. Long 

    # Margaret Widdemer ++

    # Witter Bynner ++

    # Edmund Kemper Broadus ++
    # print(p_list)
    # 4f575225-36ae-411c-8674-75adc947bff9 H.D.
    # c562b794-d50a-4dc8-ab0f-bc402e4a17ca
    # 780716e4-ceaa-4ada-961c-4e3b93a1cbb3 hermes
    # poems = [
    #     {
    #     "title": "Test poem",
    #     "poet": "H.D.",
    #     "stanzas": [
    #         [
    #             "But more than the many-foamed ways",
    #             "Of the sea,",
    #             "I know him",
    #             "Of the triple path-ways,",
    #             "Hermes,",
    #             "Who awaiteth."
    #         ],
    #     ],
    #     "source": "Poetry",
    #     "date_published": "JANUARY, 1913"
    # },
    # ]
  
    
    poet_poem_dict = {}
    for poem in poems:
        poet_poem_dict.setdefault(poem['poet'], []).append(poem)

    # print(poet_poem_dict.keys())
    # return
    # for poem in poems:
    #     if poem['poet'] == 'Lily A. Long':
    #         poet_poem_dict.setdefault(poem['poet'], []).append(poem)
            

    try:
        async with aiohttp.ClientSession() as session:
            # await upload_poem(poet_id='ee115940-5b75-43e1-8707-4c15c78762ae', poem=poems[0], session=session)
            poem_result_tasks = [upload_poems_by_poet_name(poet_name=poet, poems=poems, session=session) for poet, poems in poet_poem_dict.items()]
            poem_results = await asyncio.gather(*poem_result_tasks, return_exceptions=True)
        print('complete')
        for i, res in enumerate(poem_results):
            print(f'{i} : {res}')
            print('\n')
           
        # print(poem_results)
        # print(len(poems))
        # print(len(poet_poem_dict.keys()))

    except Exception as e:
        print(f"Error uploading poems: {e}")

async def upload_poets():

    with open(file='poet_objs_new_.json', mode='r', encoding='utf-8') as f:
        poets = json.load(f)

    async with aiohttp.ClientSession() as session:
            # await upload_poem(poet_id='ee115940-5b75-43e1-8707-4c15c78762ae', poem=poems[0], session=session)
            poet_tasks = [upload_poet(poet=poet, session=session) for poet in poets]
            poet_results = await asyncio.gather(*poet_tasks, return_exceptions=True)
    
    print(poet_results)


async def main():
    # await upload_poets()
    await upload_poems()




if __name__ == "__main__":
    asyncio.run(main())