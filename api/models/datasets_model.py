from mongoengine import StringField, IntField, ListField, DictField, ReferenceField, Document,DateTimeField

# Datasets model for API v0.2.5
#
# A MongoDB **dataset** document's schema is represented by the **Dataset_mongo** class with the following fields:
# - dataset_name: the name of the dataset
# - source_filename: the name of the input file including its extension
# - stored_filename: the name of the file in the storage folder
# - dataset_rows: the count of rows of the Excel file
# - dataset_columns: the count of columns of the Excel file
# - dataset_headers: the list of columns headers of the Excel file
# - datacontent_id: the related datacontent.
#
# A MongoDB **datacontent** document's schema is represented by the **Datacontent_mongo** class with the following fields:
# - dataset_id: the related dataset
# - datacontent_values: the values of the related dataset.

# Definition of the Dataset_mongo class

class Dataset_mongo(Document):
    dataset_name = StringField(required=True)
    source_filename = StringField(required=True)
    stored_filename = StringField(required=True)
    dataset_rows = IntField(required=True)
    dataset_columns = IntField(required=True)
    dataset_headers = ListField(StringField(), required=True)
    dataset_metrics_headers = ListField(StringField(), required=True)
    dataset_attributes_headers = ListField(StringField(), required=True)
    datacontent_id = ReferenceField('Datacontent_mongo')
    date_created = DateTimeField(required=True)
    date_last_modified = DateTimeField(required=True)
    meta = {'collection': 'Datasets'}

    def to_json(self):
        return dict({
            "dataset_id": str(self.pk),
            "dataset_name": self.dataset_name,
            "stored_filename": self.stored_filename,
            "source_filename": self.source_filename,
            "dataset_rows": self.dataset_rows,
            "dataset_columns": self.dataset_columns,
            "dataset_headers": self.dataset_headers,
            "dataset_metrics_headers":self.dataset_metrics_headers,
            "dataset_attributes_headers":self.dataset_attributes_headers,
            "datacontent_id": str(self.datacontent_id.pk),
            "date_created": self.date_created,
            "date_last_modified": self.date_last_modified
        })

# Definition of the Datacontent_mongo class

class Datacontent_mongo(Document):
    dataset_id = ReferenceField(Dataset_mongo)
    datacontent_values = DictField()
    date_created = DateTimeField(required=True)
    date_last_modified = DateTimeField(required=True)
    meta = {'collection': 'Datacontent'}

    def to_json(self):
        return dict({
            "datacontent_id": str(self.pk),
            "dataset_id": str(self.dataset_id.pk),
            "datacontent_values":self.datacontent_values,
            "date_created": self.date_created,
            "date_last_modified": self.date_last_modified
        })
