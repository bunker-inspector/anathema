from handler import Handler
import json


class CharacterHandler(Handler):
    def __init__(self, r):
        self.r = r

    def accepts(self, message):
        return
