'''
    Author: Ryan Sharp
    Date: 03/17/2017

    Module declaring base functionality for classes and attributes.  Wraps mongo functionality
'''
from models.database import get_collection
import datetime
import abc


class Attribute(object):
    def __init__(self, name, allowed_types, islist=False, required=False, val=None):
        self.name = name
        self.allowed_types = allowed_types
        self.islist = islist
        self.required = required
        def run_parse(curr_val):
            '''
            Parses dictionary value into class attribute
            '''
            if issubclass(self.allowed_types[0], BaseClass):
                return self.allowed_types[0](curr_val)
            if type(curr_val) in self.allowed_types:
                return curr_val
            return None
        if islist and isinstance(val, list):
            self.value = [run_parse(x) for x in val]
        else:
            self.value = run_parse(val)
        self.transactions = []

    def get_name(self):
        return self.name

    def get_allowed_types(self):
        return self.allowed_types

    def update_val(self, val):
        if self.islist:
            raise Exception("Cannot update val, use append or remove")
        if type(val) in self.allowed_types:
            self.value = val

    def get_val(self):
        return self.value

    def serialize(self):
        def run_serialize(curr_val):
            if issubclass(self.allowed_types[0], BaseClass):
                return curr_val.serialize_data()
            else:
                return curr_val
        val = self.value
        if val is not None:
            if self.islist:
                return [run_serialize(x) for x in self.value]
            return run_serialize(self.value)
        if self.required:
            raise AttributeError("Field: {0}, cannot be null".format(self.name))
        return val

    def apply_transaction(self, operation, value):
        if self.islist:
            if operation == "$pop" and len(self.value) > 0:
                if value == 1:
                    self.value = self.value[:-1]
                elif value == -1:
                    self.value = self.value[1:]
            elif operation == "$push":
                self.value.append(value)
        else:
            if operation == "$inc":
                self.value += value
            if operation == "$mul":
                self.value *= value
            if operation == "$set":
                self.value = value
        if hasattr(value, "serialize_data"):
            value = value.serialize_data()
        self.transactions.append({operation: {self.get_name(): value}})


class BaseClass(object):
    __metaclass = abc.ABCMeta

    def __init__(self, data):
        self._id = data.get("_id", None)
        self.created = data.get("created", datetime.datetime.now())
        self.modified = data.get("modified", None)

    @abc.abstractmethod
    def _get_collection(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _get_properties(self):
        raise NotImplementedError()

    def serialize_data(self):
        '''
        Prepares class properties to be saved to file or db
        '''
        rdict = {}
        for prop in self._get_properties():
            rdict[prop.get_name()] = prop.serialize()
        rdict["created"] = self.created
        rdict["modified"] = datetime.datetime.now()
        return rdict

    def serialize_for_json(self):
        data = self.serialize_data()
        data["created"] = data["created"].strftime("%c")
        data["modified"] = data["modified"].strftime("%c")
        return data

    def get_named_list(self):
        if not hasattr(self, "named_list"):
            self.named_list = [attribute.get_name() for attribute in self._get_properties()]
        return self.named_list

    def get_property(self, prop):
        if prop in self.get_named_list():
            return self._get_properties()[self.get_named_list().index(prop)]
        return None

    def set_attribute(self, prop_name, new_val):
        if prop_name in self.get_named_list():
            attribute = self._get_properties()[self.get_named_list().index(prop_name)]
            attribute.update_val(new_val)

    def commit(self):
        serialized = self.serialize_data()
        collection = get_collection(self._get_collection())
        if self._id:
            while True:
                update = {}
                for attribute in self._get_properties():
                    try:
                        transaction = attribute.transactions.pop(0)
                        key = transaction.keys()[0]
                        if key not in update:
                            update[key] = {}
                        update[key][attribute.get_name()] = transaction[key][attribute.get_name()]
                    except IndexError:
                        pass
                if not update:
                    break
                collection.update({"_id": self._id}, update)
        else:
            collection.insert_one(serialized)
