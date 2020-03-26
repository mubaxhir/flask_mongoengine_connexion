from mongoengine import StringField,ReferenceField,DictField,Document,DateTimeField,EmbeddedDocument,EmbeddedDocumentField,ListField,IntField
from models.datasets_model import Dataset_mongo

# Charts model for API v0.2.5
#
# A MongoDB **chart** document's schema is represented by the **Chart_mongo** class with the following fields:
# - chart_title: the title of the Chart
# - chart_metric: the metric of the Chart (Y-axis)
# - chart_attribute: the attribute of the Chart (X-axis)
# - dataset_id: the dataset from which values are queried.

class Chart_filter_item(EmbeddedDocument):
    filter_number = IntField(required=True)
    attribute = StringField(required=True)
    filter_values = ListField(StringField(), required=True)

    def to_json(self):
        return dict({
            "filter_number": self.filter_number,
            "attribute": self.attribute,
            "filter_values": self.filter_values
        })

# Definition of the Chart_mongo class

class Chart_mongo(Document):
    chart_title = StringField(required=True)
    chart_metric = StringField(required=True)
    chart_attribute = StringField(required=True)
    dataset_id = ReferenceField(Dataset_mongo)
    chart_data = DictField()
    filters = ListField(EmbeddedDocumentField(Chart_filter_item))
    date_created = DateTimeField(required=True)
    date_last_modified = DateTimeField(required=True)
    meta = {'collection': 'Charts'}

    def to_json(self):
        return dict({
            "chart_id": str(self.pk),
            "chart_title":self.chart_title,
            "chart_metric":self.chart_metric,
            "chart_attribute":self.chart_attribute,
            "dataset_id": str(self.dataset_id.pk),
            "chart_data": dict(self.chart_data),
            "filters" : [x.to_json() for x in list(self.filters)],
            "date_created": self.date_created,
            "date_last_modified": self.date_last_modified
        })
