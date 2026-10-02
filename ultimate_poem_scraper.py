# Get poems
# Scrape words + Upload words + Check if exist (via poems)
# Scrape Poets (via poems)
# Post poems w/ Poet ID (if exists)
# -- Create poets (if they exist)
# -- Upload poem w/ poet ID

# a way to do it where it 'waits' for me to make edits to the poems list
# and I can continue when I'm done..
import asyncio
import aiohttp
import requests
import json
# from definitionsScrape import main as scrape_definitions_main
from get_poets_data import get_poet_data_wiki_entry, format_full_name
# from scraper import main as scrape_poems_main
# from word_api import upload_words_to_laureate


async def upload_poems_by_poet_name(poet_name: str, poems: list, session):
    # Check if poet exists in DB
    ## Exists - obtain ID
    ## Doesnt - Scrape + obtain ID
    poet_id = ''
    poet_obj = await get_poet_by_name(poet_name=poet_name, session=session)
    try: 
        if not poet_obj:
            print('poet obj not exist')
            scrape_obj = await get_poet_data_wiki_entry(poet_name=poet_name, session=session)
            print(poet_obj, '|||||||||')
            print(scrape_obj, '\n')
            if scrape_obj == None:
                return
            poet_obj = await upload_poet(poet=scrape_obj, session=session)
            print(poet_obj, '!!!!!!!!!!!!!!')
        
        if poet_obj == None:
            return
        poet_id = poet_obj.get('id')
     

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
    url = 'http://localhost:3000/poets'
    try:
        async with session.post(url, json=poet, headers=headers) as response:
            data = await response.json()
            # print(data)
            # if int(data['code']) != 200:
            #     return f'eror {poet}'

            return data['data']
    except Exception as e:
        print(f"Adding poet {poet['first_name']} to laureate.: {e}")
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
    
    with open(file='poet_objs_new.json_birthplacesearch.json', mode='r', encoding='utf-8') as f:
    # with open(file='ouput__.json', mode='r', encoding='utf-8') as f:
        poems = json.load(f)

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


async def main():
    # await scrape_definitions_main()
    # await upload_words_to_laureate()

    # ######

    # await scrape_poets_main()
    await upload_poems()




if __name__ == "__main__":
    asyncio.run(main())



# poems = [
#         {
#             "title": "SYMBOLS",
#             "poet": "Alice Corbin",
#             "stanzas": [
#                 [
#                     "Who was it built the cradle of wrought gold?",
#                     "A druid, chanting by the waters old.",
#                     "Who was it kept the sword of vision bright?",
#                     "A warrior, falling darkly in the fight.",
#                     "Who was it put the crown upon the dove?",
#                     "A woman, paling in the arms of love.",
#                     "Oh, who but these, since Adam ceased to be,",
#                     "Have kept their ancient guard about the Tree?"
#                 ]
#             ],
#             "source": "Poetry",
#             "date_published": "DECEMBER, 1912"
#         },
#         {
#             "title": "THE STAR",
#             "poet": "Alice Corbin",
#             "stanzas": [
#                 [
#                     "I saw a star fall in the night,",
#                     "And a grey moth touched my cheek;",
#                     "Such majesty immortals have,",
#                     "Such pity for the weak."
#                 ]
#             ],
#             "source": "Poetry",
#             "date_published": "DECEMBER, 1912"
#         },
#         {
#             "title": "LOVE-SONGS OF THE OPEN ROAD",
#             "poet": "Kendall Banning",
#             "stanzas": [
#                 [
#                     "MORNING"
#                 ],
#                 [
#                     "The morning wind is wooing me; her lips have swept my brow.",
#                     "Was ever dawn so sweet before? the land so fair as now?",
#                     "The wanderlust is luring to wherever roads may lead,",
#                     "While yet the dew is on the hedge. So how can I but heed?"
#                 ],
#                 [
#                     "The forest whispers of its shades; of haunts where we have been,—",
#                     "And where may friends be better made than under God's green inn?",
#                     "Your mouth is warm and laughing and your voice is calling low,",
#                     "While yet the dew is on the hedge. So how can I but go?"
#                 ],
#                 [
#                     "NOON"
#                 ],
#                 [
#                     "The bees are humming, humming in the clover;",
#                     "The bobolink is singing in the rye;",
#                     "The brook is purling, purling in the valley,",
#                     "And the river's laughing, radiant, to the sky!"
#                 ],
#                 [
#                     "The buttercups are nodding in the sunlight;",
#                     "The winds are whispering, whispering to the pine;",
#                     "The joy of June has found me; as an aureole it's crowned me",
#                     "Because, oh best belovèd, you are mine!"
#                 ],
#                 [
#                     "NIGHT"
#                 ],
#                 [
#                     "In Arcady by moonlight,",
#                     "(Where only lovers go),",
#                     "There is a pool where only",
#                     "The fairest roses grow."
#                 ],
#                 [
#                     "Why are the moonlit roses",
#                     "So sweet beyond compare?",
#                     "Among their purple shadows",
#                     "My love is waiting there."
#                 ],
#                 [
#                     "————————"
#                 ],
#                 [
#                     "To Arcady by moonlight",
#                     "The roads are open wide,",
#                     "But only joy can enter",
#                     "And only joy abide."
#                 ],
#                 [
#                     "There is the peace unending",
#                     "That perfect faith can know—",
#                     "In Arcady by moonlight,",
#                     "Where only lovers go."
#                 ]
#             ],
#             "source": "Poetry",
#             "date_published": "JANUARY, 1913"
#         },
#         {
#             "title": "A SONG OF HAPPINESS",
#             "poet": "Ernest Rhys",
#             "stanzas": [
#                 [
#                     "Ah Happiness:",
#                     "Who called you \"Earandel\"?",
#                     "(Winter-star, I think, that is);",
#                     "And who can tell the lovely curve",
#                     "By which you seem to come, then swerve",
#                     "Before you reach the middle-earth?",
#                     "And who is there can hold your wing,",
#                     "Or bind you in your mirth,",
#                     "Or win you with a least caress,",
#                     "Or tear, or kiss, or anything—",
#                     "Insensate happiness?"
#                 ],
#                 [
#                     "Once I thought to have you",
#                     "Fast there in a child:",
#                     "All her heart she gave you,",
#                     "Yet you would not stay.",
#                     "Cruel, and careless,",
#                     "Not half reconciled,",
#                     "Pain you cannot bear;",
#                     "When her yellow hair",
#                     "Lay matted, every tress;",
#                     "When those looks of hers,",
#                     "Were no longer hers,",
#                     "You went: in a day",
#                     "She wept you all away."
#                 ],
#                 [
#                     "Once I thought to give",
#                     "You, plighted, holily—",
#                     "No more fugitive,",
#                     "Returning like the sea:",
#                     "But they that share so well",
#                     "Heaven must portion Hell",
#                     "In their copartnery:",
#                     "Care, ill fate, ill health,",
#                     "Came we know not how",
#                     "And broke our commonwealth.",
#                     "Neither has you now."
#                 ],
#                 [
#                     "Some wait you on the road,",
#                     "Some in an open door",
#                     "Look for the face you show'd",
#                     "Once there—no more.",
#                     "You never wear the dress",
#                     "You danced in yesterday;",
#                     "Yet, seeming gone, you stay,",
#                     "And come at no man's call:",
#                     "Yet, laid for burial,",
#                     "You lift up from the dead",
#                     "Your laughing, spangled head."
#                 ],
#                 [
#                     "Yes, once I did pursue",
#                     "You, unpursuable;",
#                     "Loved, longed for, hoped for you—",
#                     "Blue-eyed and morning brow'd.",
#                     "Ah, lovely happiness!",
#                     "Now that I know you well,",
#                     "I dare not speak aloud",
#                     "Your fond name in a crowd;",
#                     "Nor conjure you by night,",
#                     "Nor pray at morning-light,",
#                     "Nor count at all on you:"
#                 ],
#                 [
#                     "But, at a stroke, a breath,",
#                     "After the fear of death,",
#                     "Or bent beneath a load;",
#                     "Yes, ragged in the dress,",
#                     "And houseless on the road,",
#                     "I might surprise you there.",
#                     "Yes: who of us shall say",
#                     "When you will come, or where?",
#                     "Ask children at their play,",
#                     "The leaves upon the tree,",
#                     "The ships upon the sea,",
#                     "Or old men who survived,",
#                     "And lived, and loved, and wived.",
#                     "Ask sorrow to confess",
#                     "Your sweet improvidence,",
#                     "And prodigal expense",
#                     "And cold economy,",
#                     "Ah, lovely happiness!"
#                 ]
#             ],
#             "source": "Poetry",
#             "date_published": "JANUARY, 1913"
#         },
#         {
#             "title": "HELEN IS ILL",
#             "poet": "Roscoe W. Brink",
#             "stanzas": [
#                 [
#                     "When she is ill my laughter cowers;",
#                     "An exile with a broken rhyme,",
#                     "My head upon the breast of time,",
#                     "I hear the heart-beat of the hours;",
#                     "I close my eyes without a sigh;",
#                     "The vision of her flutters by",
#                     "As glints the light of Mary's eyes",
#                     "Upon the lakes in Paradise."
#                 ],
#                 [
#                     "I seem to reach an olden town",
#                     "And enter at the sunset gate;",
#                     "And as the streets I hurry down,",
#                     "I find the men are all elate,",
#                     "As if an angel of the Lord",
#                     "Had passed with dearest word and nod,",
#                     "Remembered like a yearning chord",
#                     "Of songs the people sing to God;",
#                     "I come upon the sunrise gate—",
#                     "As silent as her listless room—",
#                     "There seven beggers sing and wait",
#                     "And this the song that breaks the gloom:"
#                 ],
#                 [
#                     "God a 'mercy is most kind;",
#                     "She the fairest passed this way;",
#                     "We the lowest were not blind;",
#                     "God a 'mercy bless the day."
#                 ]
#             ],
#             "source": "Poetry",
#             "date_published": "JANUARY, 1913"
#         },
#     ]