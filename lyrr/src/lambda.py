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
            'headers': {
                'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(event)
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
            'headers': {
                'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(artists)
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
            'headers': {
                'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
                'Access-Control-Allow-Credentials': True,
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
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
                'headers': {
                    'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
                    'Access-Control-Allow-Credentials': True,
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
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

