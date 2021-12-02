import json
import os

class Manipulator(object):

    def __init__(self, path):
        self.path = path

    def get_data(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
        return data