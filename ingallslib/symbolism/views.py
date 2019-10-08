from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import json

from .filters import year_list
from .filters import author_list
from .filters import lang_list
import pymongo

#client = pymongo.MongoClient('192.168.1.198', 27017 )
client = pymongo.MongoClient('18.224.196.7', 27017 )
db = client['ingalls_data']
collection = db['articles']

# Create your views here.
def home(request):

    if 'sort' in request.GET:
        #Variable with either contain 1 or -1
        sorting_direction = int(request.GET["sort"])
        search_results = collection.find().limit(350).sort('year', sorting_direction)
        search_results_count = collection.find().count()
    else:
        search_results = collection.find().limit(350)
        search_results_count = collection.find().count()


    year_options = collection.distinct("year")
    author_options = collection.distinct("author")
    lang_options = collection.distinct("lang")


    context = {

    'searchresults':search_results,
    'searchresultscount':search_results_count,
    'yearoptions':year_list,
    'authoroptions':author_list,
    'langoptions': lang_list,
    'filterform': {}
    };


    return render (request, 'symbolism/results.html', context);


def discover(request):

    current_path = request.get_full_path()

    #For the case that someone presses 'apply' filter when no selections have been made
    if dict(request.GET) == {'term': ['']}:
        return redirect("/")


    #If sort is in current path, query MongoDB based on sorting direction
    if 'sort' in current_path:
        filter_form = dict(request.GET)

        #Variable will either contain 1 or -1
        sorting_direction = filter_form["sort"]

        #Remove sort key/value from filter form dictionary so that mongodb can use it in query string
        del filter_form["sort"]

        #Arrange data from filter_form so that it fits the required format for the MongoDB query
        query_array = []

        for key, value in filter_form.items():
            #The term/sort cannot be formated like the rest for the MongoDB query string
            if key == 'term' or key == 'sort':
                continue
            query_array.append({ key: {'$in': value}})

        if request.GET['term'] is not '':
            query_array.append({'$text':{'$search': request.GET['term'] }})

        search_results = collection.find( { '$and': query_array } ).sort('year', int(sorting_direction[0]))
        search_results_count = collection.find( { '$and': query_array } ).count()

    else:
        filter_form = dict(request.GET)
        #Arrange data from form so that it fits the required format for the MongoDB query
        query_array = []
        for key, value in filter_form.items():
            #The term cannot be formated like the rest, it must be formatted as $text $search for MongoDB
            if key == 'term':
                continue
            query_array.append({ key: {'$in': value}})
        #If a term is in the request object, pass it to the MongoDB query string
        print(request.GET['term'])
        if request.GET['term'] is not '':
            query_array.append({'$text':{'$search': request.GET['term'] }})

        search_results = collection.find( { '$and': query_array } )
        search_results_count = collection.find( { '$and': query_array } ).count()


    search_results = list(search_results)
    author_options = collection.distinct("author")
    year_options = collection.distinct("year")
    lang_options = collection.distinct("lang")

    context = {

    'currentpath':current_path,
    'currentterm': request.GET['term'],
    'filterform': filter_form,
    'searchresults': search_results,
    'searchresultscount': search_results_count,
    'yearoptions': year_options,
    'authoroptions':author_options,
    'langoptions':lang_options
    };

    return render (request, 'symbolism/results.html', context)

def artworktest(request):
    #Import art data
    with open('symbolism/artwork.json') as file:
        data = json.load(file)

    context = {'artwork': data['artworkdata'] }

    return render(request, 'symbolism/test.html', context )
