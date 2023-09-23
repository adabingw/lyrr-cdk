import requests
import aiohttp
import lyricsgenius
import re
import pathlib
from transformers import AutoModelForCausalLM
from datasets import Dataset, DatasetDict, load_dataset
import random
import numpy as np
from bs4 import BeautifulSoup

CLIENT_ACCESS_TOKEN = '8_KCUXgztIdF9QL3rGPjHjLKDe06BLJg8teuBYGOpGB_jp5GusBkBsgInkaykm3o'
EPOCHS = 25
NAMESPACE = 'adabingw'
MODEL_NAME = 'lyrr-lorde'

# gets list of artist's songs from lyricgenius
def artist_songs(artist_id, per_page=50, page=None, sort='popularity'):
    url = f'https://api.genius.com/artists/{artist_id}/songs?sort={sort}&per_page={per_page}&page={page}'
    headers = {
        'Authorization': f'Bearer {CLIENT_ACCESS_TOKEN}'
    }
    data = requests.get(
        url,
        headers=headers, 
        stream=True
    ).json()
    return data['response']

# get list of artist's song urls
def get_artist_song_urls(artist_id, artist_name):
    urls = []
    next_page = 1
    print("🍚 Brewing songs")
    while next_page is not None:
        data = artist_songs(artist_id, per_page=50, page=next_page)
        next_page = data['next_page']
        
        for song in data['songs']:
            urls.append(song['url'])
    print("🍶 Songs brewed!")
    
    for url in urls[:]: 
        artist_song_name = url.split('/')[-1].lower()
        artist_lower = ''.join(artist_name.lower().split(' '))
        text = ''.join(artist_song_name.split('-'))
        
        if "remix" in url: 
            urls.remove(url)
            
        # trim some of the unwanted songs
        elif 'discography' in url or \
            'videography' in url or \
            'annotated' in url or \
            'discography' in url or \
            'version' in url or \
            'demo' in url or \
            'instrumental' in url or \
            'unreleased' in url or \
            'translation' in url or \
            '-live-' in url or \
            'radio-mix' in url: 
            urls.remove(url) 
        
        elif text[:len(artist_lower)] != artist_lower:
            urls.remove(url)
    
    return urls

# get lyrics from song
def _get_lyrics(song_url):
    text = requests.get(song_url, stream=True).text
    html = BeautifulSoup(text.replace('<br/>', '\n'), 'html.parser')
    div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
    if div is None:
      return None

    lyrics = div.get_text()

    # getting rid of strange things in the lyric scrapper
    lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
    lyrics = re.sub('\n{2}', '\n', lyrics)  # Gaps between verses
    lyrics = str(lyrics.strip('\n'))
    lyrics = lyrics.replace('\n', " ")
    lyrics = lyrics.replace("EmbedShare URLCopyEmbedCopy", "").replace("'", "")
    lyrics = re.sub("[\(\[].*?[\)\]]", "", lyrics)
    lyrics = re.sub(r'\d+$', '', lyrics)
    lyrics = str(lyrics).lstrip().rstrip()
    lyrics = str(lyrics).replace("\n\n", "\n")
    lyrics = str(lyrics).replace("\n\n", "\n")
    lyrics = re.sub(' +', ' ', lyrics)
    lyrics = str(lyrics).replace('"', "")
    lyrics = str(lyrics).replace("'", "")
    lyrics = str(lyrics).replace("*", "")
    return str(lyrics)

def get_lyrics(url):
    return _get_lyrics(url)

# creates a dataset object from lyrics
def create_dataset(lyrics):
    dataset = {}
    dataset['train'] = Dataset.from_dict({'text': list(lyrics)})
    datasets = DatasetDict(dataset)
    del dataset
    return datasets

def collect_data(artist, genius): 
    if artist is not None:
        artist_dict = genius.artist(artist.id)['artist']
        artist_name = str(artist_dict['name'])
        artist_url = str(artist_dict['url'])
        
        print("Artist name:", artist_name)
        print("Artist url:", artist_url)
        print("Artist id:", artist.id)

        datasets = None
        array = None 
        print("Check existing dataset first...")

        # try to get a database from hugging_face first
        try: 
            url = f"https://huggingface.co/datasets/{NAMESPACE}/{MODEL_NAME}/tree/main"
            data = requests.get(url).text
            if data != "Not Found":
                datasets = load_dataset(f"{NAMESPACE}/{MODEL_NAME}")
                print("Dataset downloaded!")
        except: 
            pass 
        
        if datasets == None:
            print("Dataset does not exist!")
            urls = get_artist_song_urls(artist.id, artist_name)
        
            data = [] 
            print("Getting lyrics...")
            datasets = load_dataset(f"{NAMESPACE}/{MODEL_NAME}")
            for url in urls: 
                lyrics = get_lyrics(url)                 
                if lyrics is not None: 
                    
                    # skip lyrics that are too short
                    if len(lyrics) < 800:
                        continue 
                    
                    # get rid of garbage text at beginning of lyrics
                    index = lyrics.find("Lyrics") + len("Lyrics")
                    lyrics = lyrics[index:]
                    
                    # get rid of garbage text at end of lyrics
                    if lyrics[len(lyrics) - 5:] == "Embed":
                        i = len(lyrics) - 6
                        while lyrics[i].isdigit() and i > 0: 
                            i -= 1
                        
                        lyrics = lyrics[:i]
                    
                    if '//' in lyrics: 
                        continue
                        
                    data.append(lyrics)
                    
            datasets = create_dataset(data) 
            datasets.push_to_hub(f"{NAMESPACE}/{MODEL_NAME}")
            # create database
            print("Dataset created!")
        
        array = datasets['train']['text']
        assert array is not None
        
        train_percentage = 0.85
        validation_percentage = 0.15
        test_percentage = 0
        
        random.shuffle(array)
        train, validation, test = np.split(array, 
            [int(len(datasets['train']['text'])*train_percentage), 
                int(len(datasets['train']['text'])*(train_percentage + validation_percentage))])
        
        datasets = DatasetDict(
            {
                'train': Dataset.from_dict({'text': list(train)}),
                'validation': Dataset.from_dict({'text': list(validation)}),
                'test': Dataset.from_dict({'text': list(test)})
            }
        )            
        return datasets
    else:
        import Exception
        raise Exception("Artist is None")

def collect(artist_name = "Lana del Ray"): 
    genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)
    artist = genius.search_artist(artist_name, max_songs=0, get_full_info=False) 
    datasets = collect_data(artist, genius)
    print(datasets)
    return datasets

def get_artist(artist_name = "Lana del Ray"):
    genius = lyricsgenius.Genius(CLIENT_ACCESS_TOKEN)
    artist = genius.search_artist(artist_name, max_songs=0, get_full_info=True) 
    artist_dict = genius.artist(artist.id)['artist']        
    MODEL_NAME = "lyrr-" + artist_dict["name"].replace(" ", "").lower()
    found = False
    
    try: 
        # tries to find see if the model exists TODO: find a better way to do this
        model = AutoModelForCausalLM.from_pretrained(f"{NAMESPACE}/{MODEL_NAME}", cache_dir=pathlib.Path(MODEL_NAME).resolve())
        found = True
    except:
        found = False
        
    return {
        'name': artist_dict["name"],
        'image': artist_dict["image_url"],
        'id': artist.id,
        'exists': found
    }

if __name__ == "__main__":
    collect()
