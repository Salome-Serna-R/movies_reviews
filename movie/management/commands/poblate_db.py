from django.core.management.base import BaseCommand
from movie.models import Movie
import json
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(r'C:\Users\USUARIO\Desktop\INGENIERA\Cuarto Semestre\Taller_copia_p1\moviereviewsproject\movie\management\commands\api_keys.env')
client = OpenAI(
        api_key=os.environ.get('openai_api_key'),
)
        
def get_embedding(text, client, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding


class Command(BaseCommand):
    help = 'Poblate the database with JSON file data'

    def handle(self, *args, **kwargs):
        json_file_path = r'C:\Users\USUARIO\Desktop\INGENIERA\Cuarto Semestre\Taller_Proyecto1\moviereviewsproject\movie\management\commands\movie_descriptions.json'
        # Load data from the JSON file
        with open(json_file_path, 'r') as file:
            movies = json.load(file)       

        
        for movie in movies:
            Movie.objects.create(
                title=movie['title'],
                description=movie['description'],
                image = f"movie/images/m_{movie['title']}.png",
                genre=movie['genre'],
                year=movie['year'],
                emb = np.array(get_embedding(movie['description'], client)).tobytes(),
            )
                
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated item embeddings'))        
        
