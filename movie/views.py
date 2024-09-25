from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import os
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np


from .models import Movie

# Create your views here.

def home(request):
    #return HttpResponse('<h1>welcome to home page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name': 'Salomé Serna'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})

def about(request):
    #return HttpResponse('<h1>welcome to About page</h1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})


def statistics_view(request):
    matplotlib.use('Agg')
    # Obtener todas las películas
    all_movies = Movie.objects.all()
    
    # Crear un diccionario para almacenar la cantidad de películas por género
    movie_counts_by_genre = {}
    
    # Filtrar las películas por género y contar la cantidad de películas por género
    for movie in all_movies:
        if movie.genre:  # Asegúrate de que el género no esté vacío
            genres = movie.genre.split(',')  # Suponiendo que los géneros están separados por comas
            first_genre = genres[0].strip()  # Tomar el primer género y eliminar espacios en blanco
            
            if first_genre in movie_counts_by_genre:
                movie_counts_by_genre[first_genre] += 1
            else:
                movie_counts_by_genre[first_genre] = 1
    
    # Ancho de las barras
    bar_width = 0.5
    # Posiciones de las barras
    bar_positions = range(len(movie_counts_by_genre))
    
    # Crear la gráfica de barras
    plt.bar(bar_positions, movie_counts_by_genre.values(), width=bar_width, align='center')
    
    # Personalizar la gráfica
    plt.title('Movies per Genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_genre.keys(), rotation=90)
    
    # Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)
    
    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    
    # Convertir la gráfica a base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    # Renderizar la plantilla statistics.html con la gráfica

    return render(request, 'statistics.html', {'graphic': graphic})


def recommend(request):
    recomended_movie = None
    load_dotenv(r'C:\Users\USUARIO\Desktop\INGENIERA\Cuarto Semestre\Taller_copia_p1\moviereviewsproject\movie\management\commands\api_keys.env')
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get('openai_api_key'),   
        )
    
    movie = Movie.objects.all()
    movie = list(movie)
    def get_embedding(text, model="text-embedding-3-small"):
        text = text.replace("\n", " ")
        return client.embeddings.create(input = [text], model=model).data[0].embedding
    
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    req = request.GET.get('recomendation_required')
    emb = get_embedding(req)

    sim = []
    for i in range(len(movie)):
        movie_embedding = movie[i].emb
        movie_embedding_float = list(np.frombuffer(movie_embedding))
        sim.append(cosine_similarity(emb, movie_embedding_float)) 
    sim = np.array(sim)
    idx = np.argmax(sim)
    recomended_movie = movie[idx]
    
    return render(request, 'recomendations.html', {'recomended_movie': recomended_movie})


def recommendations_movie(request):
    return render(request, 'recomendations.html')