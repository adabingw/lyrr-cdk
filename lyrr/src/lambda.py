from data import collect, get_artist
from model import generator, get_model
from constants import get_hf_write, get_hf_read
import json

def handler(event, context):
    print(event)
    path = ""
    try:
        path = event['path']
    except: 
        return {
            'statusCode': 200,
            'body': str(event)
        }
        
    if path == '/lyrr-backend/artist':
        print("getting artist")
        if event['queryStringParameters'] is None:
            return {
                'statusCode': 404
            }

        artists = get_artist(event['queryStringParameters']['artist_name'])
        
        print(artists)
        
        return {
            'statusCode': 200,
            # 'headers': {
            #     "Access-Control-Allow-Origin": "*", # // Required for CORS support to work
            #     "Access-Control-Allow-Credentials": True #, // Required for cookies, authorization headers with HTTPS
            # },
            'body': str(artists)
        }
        
    if path == '/lyrr-backend/lyrics':
        print("getting lyrics")
        if event['queryStringParameters'] is None: 
            return {
                'statusCode': 404
            }
            
        lyrics = event['queryStringParameters']['lyrics']
        artist = event['queryStringParameters']['artist'] 
        
        print(lyrics)
        print(artist)
        
        generated_lyrics = generator(text=lyrics, name=artist)
        return {
            'statusCode': 200,
            # 'headers': {
            #     "Access-Control-Allow-Origin": "*", # // Required for CORS support to work
            #     "Access-Control-Allow-Credentials": True #, // Required for cookies, authorization headers with HTTPS
            # },
            'body': generated_lyrics
        }
    
    if path == '/lyrr-backend/train':
        print("training model")
        if event['queryStringParameters'] is None: 
            return {
                'statusCode': 404
            }
        
        artist = event['queryStringParameters']['artist']
        try: 
            get_model(artist)
            return {
                'statusCode': 200,
                # 'headers': {
                #     "Access-Control-Allow-Origin": "*", # // Required for CORS support to work
                #     "Access-Control-Allow-Credentials": True #, // Required for cookies, authorization headers with HTTPS
                # },
                'body': event['path']
            }
        except: 
            return {
                'statusCode': 500,
                'body': str(event)
            }
        
    
    return {
        'statusCode': 500,
        'body': str(event)
    }

