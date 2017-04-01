from models.base import Attribute, BaseClass


class CraigslistRecord(BaseClass):
    def __init__(self, data):
        BaseClass.__init__(self, data)
        self.properties = [
            Attribute("post_id", [str, unicode], required=True, val=data.get("post_id")),
            Attribute("article_content", [str, unicode], required=True, val=data.get("article_content")),
            Attribute("found", [bool], required=True, val=data.get("found", False)),
        ]
        self.collection = "CraigslistRecords"

    def _get_properties(self):
        return self.properties

    def _get_collection(self):
        return self.collection
