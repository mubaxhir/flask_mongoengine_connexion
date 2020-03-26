# Import of the required librairies

import os
import conf
from datetime import datetime
from core.basic_algorithm import Dataset_core
from flask import jsonify
from models.datasets_model import Dataset_mongo,Datacontent_mongo
from models.decks_model import Deck_dataset_item,Deck_chart_item,Deck_mongo
from mongoengine import connect
from uuid import uuid4
from werkzeug.utils import secure_filename


# Connnection to the MongoDB database

connect(db=conf.DB, host = conf.MONGODB_HOST)


time_now = datetime.now()


# Definition of a function for the POST verb of the /datasets endpoint

def post_dataset_with_file(source_file):

    # Generation of source_filename (secure name) and stored_filename (UUID4) and dataset_name

    source_filename, file_ext = os.path.splitext(source_file.filename)
    dataset_name = secure_filename(source_filename)
    dataset_name = dataset_name.replace("_", " ")
    source_filename = secure_filename(source_filename+file_ext)
    generated_name = uuid4()
    stored_filename = str(str(generated_name) + file_ext)


    # Storage of file in storage folder

    file_path = str(conf.STORAGE_FOLDER)+stored_filename

    while os.path.exists(file_path):

        file_path = str(conf.STORAGE_FOLDER)+"%s%s" % (str(generated_name), file_ext)
        generated_name = uuid4()

    source_file.save(file_path)

    # Check of the file extension against allowed extensions and check of file size against the maximum file size

    if (file_ext in str(conf.ALLOWED_EXTENSION) and os.stat(file_path).st_size <= int(conf.MAX_FILE_SIZE)):

        # If checks are succesful
        # Generation of the dataset with the Dataset_core class of the core algorithm

        generated_dataset = Dataset_core(file_path)

        # Definition and saving of the MongoDB Dataset document

        dataset_document = Dataset_mongo(
            dataset_name=dataset_name,
            dataset_columns=generated_dataset.columns,
            dataset_rows=generated_dataset.rows,
            source_filename=source_filename,
            stored_filename=generated_dataset.filename,
            dataset_headers=generated_dataset.headers,
            dataset_metrics_headers=generated_dataset.metrics_headers,
            dataset_attributes_headers=generated_dataset.attributes_headers,
            date_created=time_now.isoformat(),
            date_last_modified=time_now.isoformat()
            )

        dataset_document.save()

        # Generation of the datacontent with the Dataset_core class of the core algorithm

        generated_dataset.generate_content()

        # Definition and saving of the MongoDB Datacontent document

        datacontent_document = Datacontent_mongo(
            dataset_id=dataset_document,
            datacontent_values = generated_dataset.values,
            date_created=time_now.isoformat(),
            date_last_modified=time_now.isoformat()
            )

        datacontent_document.save(validate=False)

        # Insertion of the reference to the Datacontent document into the Dataset document

        dataset_document.datacontent_id = datacontent_document

        dataset_document.save()

        # Return of the Dataset's id

        return dataset_document.to_json()

    # Operations if checks are not succesful

    else:

        # Removal of the stored file from the storage folder

        os.remove(file_path)

        # Return of the 400 response

        return jsonify(error = 'File not supported', status = 400, message = 'Provided source_file not supported (extension or size)')


# Definition of a function for the GET verb of the /datasets endpoint

def get_datasets():

    # Retrieval of all datasets in array

    try:

        return [dataset_document.to_json() for dataset_document in Dataset_mongo.objects()]

    # Return of the 400 response

    except:

        return jsonify(error = 'Bad request', status = 400, message = 'Invalid request')


# Definition of a function for the GET verb of the /datasets/{dataset_id} endpoint

def get_dataset_by_id(dataset_id):

    # Retrieval of indicated dataset

    try:

        dataset_document = Dataset_mongo.objects.get(pk=dataset_id)

        return dataset_document.to_json()

    # Return of the 404 response

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the GET verb of the /datasets/{dataset_id}/datacontent endpoint

def get_datacontent_for_dataset_id(dataset_id):

    # Retrieval of the indicated datacontent

    try:

        # Retrieval of the datacontent_id through the dataset of the indicated dataset_id

        datacontent = Dataset_mongo.objects.get(pk=dataset_id).datacontent_id

        # Retrieval of the datacontent by datacontent_id

        response = Datacontent_mongo.objects.get(pk=datacontent.pk)

        return response.to_json()

    # Return of the 404 response

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the GET verb of the /datasets/{dataset_id}/attribute_values endpoint

def get_attribute_values_for_dataset_id(dataset_id, attribute):

    try:

        dataset = Dataset_mongo.objects.get(pk=dataset_id)

        if attribute not in dataset.dataset_attributes_headers:

            return jsonify(error = 'Bad request', status = 400, message = 'Attribute not found in the requested dataset_id')

        else:

            datacontent = Dataset_mongo.objects.get(pk=dataset_id).datacontent_id

            pipeline = [
                {
                    '$unwind': {
                        'path': '$datacontent_values',
                        'preserveNullAndEmptyArrays': True
                    }
                }, {
                    '$project': {
                        'datacontent_values.'+attribute: 1,
                        '_id': 0
                    }
                }, {
                '$group': {
                    '_id': {
                        str(attribute): '$datacontent_values.'+attribute
                    },
                }
                }, {
                '$sort': {
                    '_id': 1
                    }
                }
            ]

            data_cursor = Datacontent_mongo.objects(pk=datacontent.pk).aggregate(*pipeline)

            return {"attribute":attribute, "dataset_id":dataset_id, "values":[x["_id"][attribute] for x in data_cursor]}

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the GET verb of the /datasets/{dataset_id}/chart_suggestions endpoint

def get_chart_suggestions_for_dataset_id(dataset_id):

    chart_suggestions_values=[]

    try:

        dataset = Dataset_mongo.objects.get(pk=dataset_id)

        for x in dataset.dataset_metrics_headers:

            suggestions = []

            for y in dataset.dataset_attributes_headers:

                suggestions.append({'metric':x, 'attribute': y, 'suggestion_name':str(x) + " by " + str(y)})

            chart_suggestions_values.append({
                "metric":x,
                "suggestions":suggestions
            })

        return jsonify({"dataset_id":dataset_id, "chart_suggestions_values":chart_suggestions_values})

    except:

        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the PATCH verb of the /datasets/{dataset_id} endpoint

def patch_dataset_by_id(body,dataset_id, op, path, value=None):

    path = path.split('/')

    try:

        if(op == "replace" and path[-1] == 'dataset_name' ):
            body_dataset_name = secure_filename(str(body["dataset_name"]))
            body_dataset_name = body_dataset_name.replace("_", " ")
            Dataset_mongo.objects(pk=dataset_id).update(set__dataset_name = body_dataset_name,set__date_last_modified = time_now.isoformat())
            dataset = Dataset_mongo.objects.get(pk=dataset_id)
            return jsonify({"dataset_name":dataset.dataset_name})

        else:

            return jsonify(error = 'Bad request', status = 400, message = 'Invalid request or parameter')

    except Exception as e:
        print(e)
        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')


# Definition of a function for the DELETE verb of the /datasets/{dataset_id} endpoint

def delete_dataset_by_id(dataset_id):

    try:

        dataset = Dataset_mongo.objects(pk=dataset_id)

        datacontent = Datacontent_mongo.objects(pk=str(dataset.get(pk=dataset_id).datacontent_id.pk))

        decks = Deck_mongo.objects(deck_datasets__dataset_id=dataset_id)

        for deck in decks:

            datasets = list(deck.deck_datasets)

            for data in datasets:

                if(str(data.dataset_id.pk) == dataset_id):

                    datasets.remove(data)

            Deck_mongo.objects(pk=str(deck.pk)).update(set__deck_datasets = datasets,set__date_last_modified = time_now.isoformat())

        dataset.delete()

        datacontent.delete()

        return jsonify(status = 204, message = 'Succesful Dataset deletion')

    except Exception as e:
        print(e)
        return jsonify(error = 'Resource not found', status = 404, message = 'Dataset with requested dataset_id not found')
