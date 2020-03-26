from mongoengine import StringField,ListField,ReferenceField,Document,EmbeddedDocument,EmbeddedDocumentField,DateTimeField
from models.datasets_model import Dataset_mongo
from models.charts_model import Chart_mongo

# Decks model for API v0.2.5
#
# A MongoDB **deck** document's schema is represented by the **Deck_mongo** class with the following fields:
# - deck_datasets: the list of datasets of the Deck
# - deck_charts: the list of charts of the Deck.

# Definition of the Deck_mongo class

class Deck_dataset_item(EmbeddedDocument):
    dataset_id = ReferenceField(Dataset_mongo)

class Deck_chart_item(EmbeddedDocument):
    chart_id = ReferenceField(Chart_mongo)

class Deck_mongo(Document):
    deck_name = StringField(required=True)
    deck_datasets = ListField(EmbeddedDocumentField(Deck_dataset_item))
    deck_charts = ListField(EmbeddedDocumentField(Deck_chart_item))
    date_created = DateTimeField(required=True)
    date_last_modified = DateTimeField(required=True)
    meta = {'collection': 'Decks'}

    def to_json_ext(self):
        return dict({
            "deck_id": str(self.pk),
            "deck_name": str(self.deck_name),
            "deck_datasets": [{"dataset_id":str(x.dataset_id.pk)} for x in self.deck_datasets],
            "deck_charts": [{"chart":x.chart_id.to_json()} for x in self.deck_charts],
            "deck_charts_number": len(self.deck_charts),
            "date_created": self.date_created,
            "date_last_modified": self.date_last_modified
        })

    def to_json_condensed(self):
        return dict({
            "deck_id": str(self.pk),
            "deck_name": str(self.deck_name),
            "deck_datasets": [{"dataset_id":str(x.dataset_id.pk)} for x in self.deck_datasets],
            "deck_charts": [{"chart_id":str(x.chart_id.pk)} for x in self.deck_charts],
            "deck_charts_number": len(self.deck_charts),
            "date_created": self.date_created,
            "date_last_modified": self.date_last_modified
        })
