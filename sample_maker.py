import requests
import json
import io
import os

def poem_samples():
    url = 'http://localhost:3000/poems'
    res = requests.get(url=url)
    
    path = '/Users/williamw/projects/nativeproject/my-app/poemSamples.json'

    # Check if path is absolute
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    with open(path, 'w', encoding='utf-8') as f:
        data = res.json()
        json.dump(data['data'], f, ensure_ascii=False, indent=4)



def poet_samples():
    url = 'http://localhost:3000/poets'
    res = requests.get(url=url)
    
    path = '/Users/williamw/projects/nativeproject/my-app/poetSamples.json'

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    with open(path, 'w', encoding='utf-8') as f:
        data = res.json()
        json.dump(data['data'], f, ensure_ascii=False, indent=4)

    # Removed unnecessary requests.get() call

def main():
    poet_samples()
    poem_samples()

if __name__ == "__main__":
    main()