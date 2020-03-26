# Import of the required librairies

from datetime import datetime
import conf
from flask import jsonify
from models.datasets_model import Dataset_mongo
from models.decks_model import Deck_dataset_item,Deck_chart_item,Deck_mongo
from models.charts_model import Chart_mongo
from mongoengine import connect
from werkzeug.utils import secure_filename


# Connnection to the MongoDB database

connect(db=conf.DB, host = conf.MONGODB_HOST)


time_now = datetime.now()


# Definition of a function for the POST verb of the /decks endpoint

def post_deck(body, include_name=None, include_dataset=None):

    try:

        datasets = []
        name = str(conf.DEFAULT_DECK_NAME)

        if include_dataset == True:
            datasets.append({"dataset_id":str(body["dataset_id"])})

        if include_name == True:
            name = secure_filename(str(body["deck_name"]))
            name = name.replace("_", " ")

        deck_document = Deck_mongo(
            deck_name = name,
            deck_datasets=datasets,
            deck_charts=[],
            date_created=time_now.isoformat(),
            date_last_modified=time_now.isoformat()
            )

        deck_document.save()

        return jsonify({"deck_id":str(deck_document.pk)})

    # Return of the 400 response

    except Exception as e:
        print(e)
        return jsonify(error = 'Bad request', status = 400, message = 'Invalid request or parameter')


# Definition of a function for the GET verb of the /decks endpoint

def get_decks():

    try:

        return [deck_document.to_json_condensed() for deck_document in Deck_mongo.objects]

    # Return of the 404 response

    except:

        return jsonify(error = 'Bad request', status = 400, message = 'Invalid request')


# Definition of a function for the GET verb of the /decks/{deck_id} endpoint

def get_deck_by_id(deck_id, extended=None):

    try:

        deck_document = Deck_mongo.objects.get(pk=deck_id)

        if (extended==True):
            return deck_document.to_json_ext()
        else:
            return deck_document.to_json_condensed()

    # Return of the 404 response

    except:

        return jsonify(error = 'Resource not found',status = 404,message = 'Deck with requested deck_id not found')


# Definition of a function for the PATCH verb of the /decks/{deck_id} endpoint

def patch_deck_by_id(body,deck_id, op, path, value=None):

     # Spliting the dataset ID or chart ID from path in list
     # e.g: "/deck_dataset/8f65fg65fg65f6f" = ["","deck_dataset","8f65fg65fg65f6f"]

    path = path.split('/')

    try:

        # Checks for all 4 operations

        if(op == "add" and path[-1] == 'deck_datasets'):
            datasets = list(Deck_mongo.objects.get(pk=deck_id).deck_datasets)
            datasets.append({"dataset_id":str(body["dataset_id"])})
            Deck_mongo.objects(pk=deck_id).update(set__deck_datasets = datasets,set__date_last_modified = time_now.isoformat())
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.to_json_condensed()

        elif (op == "replace" and path[-1] == 'deck_name'):
            body_deck_name = secure_filename(str(body["deck_name"]))
            body_deck_name = body_deck_name.replace("_", " ")
            Deck_mongo.objects(pk=deck_id).update(set__deck_name = body_deck_name,set__date_last_modified = time_now.isoformat())
            deck = Deck_mongo.objects.get(pk=deck_id)
            return jsonify({"deck_name":deck.deck_name})

        elif (op=="remove" and path[-2] == "deck_datasets"):
            datasets = list(Deck_mongo.objects.get(pk=deck_id).deck_datasets)
            for dataset in datasets:
                if(str(dataset.dataset_id.pk) == path[-1]):
                    datasets.remove(dataset)
            deck = Deck_mongo.objects(pk=deck_id)
            if deck:
                deck = deck.get(pk=deck_id)
                deck.update(set__deck_datasets = datasets,set__date_last_modified = time_now.isoformat())
                deck.save()
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.to_json_condensed()

        elif (op=="remove" and path[-2] == "deck_charts"):
            charts = list(Deck_mongo.objects.get(pk=deck_id).deck_charts)
            for chart in charts:
                if(str(chart.chart_id.pk) == path[-1]):
                    charts.remove(chart)
            deck = Deck_mongo.objects(pk=deck_id)
            if deck:
                deck = deck.get(pk=deck_id)
                deck.update(set__deck_charts = charts,set__date_last_modified = time_now.isoformat())
                deck.save()
            deck = Deck_mongo.objects.get(pk=deck_id)
            return deck.to_json_condensed()


        # If checks are not true, then return of the 400 response

        else:

            return jsonify(error = 'Bad request', status = 400, message = 'Invalid request or parameter')

    # If deck_id not found, then return of the 400 response

    except Exception as e:
        print(e)
        return jsonify(error = 'Resource not found', status = 404, message = 'Deck with requested deck_id not found')


# Definition of a function for the DELETE verb of the /decks/{deck_id} endpoint

def delete_deck_by_id(deck_id):

    try:

        deck = Deck_mongo.objects(pk=deck_id)

        for chart in deck.get(pk=deck_id).deck_charts:

            Chart_mongo.objects(pk=chart.chart_id.pk).delete()

        deck.delete()

        return jsonify(status = 204, message = 'Succesful Deck deletion')

    except Exception as e:
        print(e)
        return jsonify(error = 'Resource not found', status = 404, message = 'Deck with requested deck_id not found')
