import aiohttp
import json
import asyncio
import unicodedata


word_api_sem = asyncio.Semaphore(20)

async def upload_words_to_laureate():

    with open("high_freq_words_testt.json", "r", encoding='utf-8') as infile:
        word_objs = json.load(infile)

    # word_objs = word_objs[]
    # word_objs = word_objs[1:10]
    # print(word_objs)
    async with aiohttp.ClientSession() as session:
        upload_tasks = [upload_word_to_laureate(word_obj, session) for word_obj in word_objs]
        upload_results = await asyncio.gather(*upload_tasks, return_exceptions=False)

        # print(word_obj['word'])
        print(upload_results)
        

async def upload_word_to_laureate(word_obj, session):
    url = f"http://localhost:3000/api/words"
    async with word_api_sem:

        # print(word_obj['word'])

        async with session.post(url, json=word_obj) as response:
            data = await response.json()
        
        return data
    
async def get_all_words_from_api():
    base_url = 'http://localhost:3000'
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{base_url}/api/words') as res:
            data = await res.json()
        

    with open('word_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def main():
    await upload_words_to_laureate()
    # await get_all_words_from_api()
    # 2020
    # Processed poems in 136.35690266700112 seconds
    # Processed 2020 words in 92.25724187499145 seconds

    # ch = '—'
    # ch_normal = '-'
    # print(unicodedata.name(ch)) 

if __name__ == "__main__":
    asyncio.run(main())