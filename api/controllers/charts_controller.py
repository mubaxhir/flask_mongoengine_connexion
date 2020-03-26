# Import of the required librairies

import conf
from datetime import datetime
from flask import jsonify
from mongoengine import connect
from models.charts_model import Chart_mongo,Chart_filter_item
from models.datasets_model import Dataset_mongo,Datacontent_mongo
from models.decks_model import Deck_dataset_item,Deck_chart_item,Deck_mongo


# Connnection to the MongoDB database

connect(db=conf.DB, host=conf.MONGODB_HOST)

time_now = datetime.now()


# Definition of a function for the POST verb of the /charts endpoint

def post_chart(body):

    try:

        title = body["chart_metric"] + " by " + body["chart_attribute"]

        datacontent = Dataset_mongo.objects.get(pk=body["dataset_id"]).datacontent_id

        pipeline = [
            { '$unwind': "$datacontent_values"
            },
            { '$match' : 
                {'datacontent_values.'+ x['attribute'] : { '$in' : x['filter_values'] }  for x in body['filters']}   
            },
            { '$project':
                { 'datacontent_values.'+body["chart_attribute"]:1, 'datacontent_values.'+body["chart_metric"]:1 }
            },         
            { '$group' :
                { '_id' : { body["chart_attribute"] : '$datacontent_values.'+body["chart_attribute"]},
                body["chart_metric"] : { '$sum' : '$datacontent_values.'+body["chart_metric"] }
                }
            },
            { '$sort':
                { '_id': 1 }
            }
        ]

        data_cursor = Datacontent_mongo.objects(pk=datacontent.pk).aggregate(*pipeline)

        data = {str(x["_id"][str(body["chart_attribute"])]) :x[str(body["chart_metric"])] for x in data_cursor}

        filters = [Chart_filter_item(filter_number=x["filter_number"],attribute=x["attribute"],filter_values=x["filter_values"]) for x in body['filters']]
        
        chart_document = Chart_mongo(
            chart_title=str(title),
            dataset_id=body["dataset_id"],
            chart_metric=body["chart_metric"],
            chart_attribute=body["chart_attribute"],
            chart_data=data,
            filters = filters,
            date_created=time_now.isoformat(),
            date_last_modified=time_now.isoformat()
            )

        chart_document.save()

        Deck_mongo.objects(pk=body["deck_id"]).update(push__deck_charts=Deck_chart_item(chart_id=chart_document.pk),set__date_last_modified = time_now.isoformat())

        return chart_document.to_json()

    # Return of the 400 response

    except Exception as e:
        print(e)
        return jsonify(error = 'Bad request', status = 400, message = 'Invalid request or parameter')


# Definition of a function for the GET verb of the /charts/{chart_id} endpoint

def get_chart_by_id(chart_id):

    try:

        chart_document = Chart_mongo.objects.get(pk=chart_id)

        return chart_document.to_json()

    # Return of the 404 response

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Chart with requested chart_id not found')


# Definition of a function for the PUT verb of the /charts/{chart_id} endpoint

def put_chart_by_id(chart_id,body):

    try:

        title = body["chart_metric"] + " by " + body["chart_attribute"]

        datacontent = Dataset_mongo.objects.get(pk=body["dataset_id"]).datacontent_id

        pipeline = [
            { '$unwind': "$datacontent_values"
            },
            { '$match' : 
                {'datacontent_values.'+ x['attribute'] : { '$in' : x['filter_values'] }  for x in body['filters']}   
            },
            { '$project':
                { 'datacontent_values.'+body["chart_attribute"]:1, 'datacontent_values.'+body["chart_metric"]:1 }
            },
            { '$group' :
                { '_id' : { body["chart_attribute"] : '$datacontent_values.'+body["chart_attribute"]},
                body["chart_metric"] : { '$sum' : '$datacontent_values.'+body["chart_metric"] }
                }
            },
            { '$sort':
                { '_id': 1 }
            }
        ]

        data_cursor = Datacontent_mongo.objects(pk=datacontent.pk).aggregate(*pipeline)

        data = {x["_id"][str(body["chart_attribute"])] :x[str(body["chart_metric"])] for x in data_cursor}

        try:

            filters = [Chart_filter_item(filter_number=x["filter_number"],attribute=x["attribute"],filter_values=x["filter_values"]) for x in body['filters']]

            chart_document = Chart_mongo.objects.get(pk = chart_id)
            chart_document.chart_title = title
            chart_document.chart_metric = body["chart_metric"]
            chart_document.chart_attribute = body["chart_attribute"]
            chart_document.chart_data = data
            chart_document.filters = filters
            chart_document.date_last_modified = time_now.isoformat()
            chart_document.save()

            return chart_document.to_json()

        # Return of the 404 response

        except Exception as e:
            print(e)
            return jsonify(error = 'Resource not found', status = 404, message = 'Chart with requested chart_id not found')

    # Return of the 400 response

    except:

            return jsonify(error = 'Bad request', status = 400, message = 'Invalid request or parameter')


# Definition of a function for the DELETE verb of the /charts/{chart_id} endpoint

def delete_chart_by_id(chart_id):

    try:

        decks = Deck_mongo.objects(deck_charts__chart_id=chart_id)

        for deck in decks:

            charts = list(deck.deck_charts)

            for data in charts:

                if(str(data.chart_id.pk) == chart_id):

                    charts.remove(data)

            Deck_mongo.objects(pk=str(deck.pk)).update(set__deck_charts = charts,set__date_last_modified = time_now.isoformat())

        Chart_mongo.objects(pk=chart_id).delete()

        return jsonify(status = 204, message = 'Succesful Chart deletion')

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Chart with requested chart_id not found')
