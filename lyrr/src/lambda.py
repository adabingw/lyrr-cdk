from data import collect, get_artist
from model import generator, get_model
from constants import get_hf_write, get_hf_read

def handler(event, context):
    print(event)
    path = event['path']
        
    if path == '/artist':
        print("getting artist")
        if event['queryStringParameters'] is None:
            return {
                'statusCode': 404
            }

        artists = get_artist(event['queryStringParameters']['artist_name'])
        
        print(artists)
        
        return {
            'statusCode': 200,
            'body': artists
        }
        
    if path == '/lyrics':
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
            'body': generated_lyrics
        }
    
    if path == '/train':
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
                'body': event['path']
            }
        except: 
            return {
                'statusCode': 500,
                'body': event['path']
            }
        
    
    return {
        'statusCode': 500,
        'body': event['path']
    }

