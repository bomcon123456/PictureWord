import json
import urllib.request
from enum import Enum
import base64


class DeckEnum(Enum):
    GET_DECK_NAMES_AND_ID = "deckNamesAndIds"
    GET_DECKS_OF_CARDS = "getDecks"
    CREATE_DECKS = "createDeck"


class ModelEnum(Enum):
    GET_MODEL_NAMES_AND_ID = "modelNamesAndIds"
    GET_MODEL_FIELD_NAMES = "modelFieldNames"
    CREATE_MODEL = "createModel"


class NoteEnum(Enum):
    ADD_NOTE = "addNote"
    ADD_NOTES = "addNotes"
    DELETE_NOTES = "deleteNotes"


class MediaEnum(Enum):
    STORE_MEDIA_FILE = "storeMediaFile"
    RETRIEVE_MEDIA_FILE = "retrieveMediaFile"
    DELETE_MEDIA_FILE = "deleteMediaFile"


class AnkiConnector:
    def __init__(self):
        self.anki_url = 'http://localhost:8765'
        self.anki_connect_version = 6

    def _verify_audio(self, audio):
        res = []
        if audio is not None:
            keys = audio.keys()
            if all(k in keys for k in ["url", "filename", "fields"]):
                res = audio
            else:
                raise Exception("Invalid audio dict.")
        return res

    def _request(self, action, **params):
        return {
            'action': action,
            'params': params,
            'version': self.anki_connect_version
        }

    def _invoke(self, action, **params):
        requestJson = json.dumps(self._request(
            action, **params)).encode('utf-8')
        response = json.load(urllib.request.urlopen(
            urllib.request.Request(self.anki_url, requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']

    def get_decks(self):
        return self._invoke(DeckEnum.GET_DECK_NAMES_AND_ID.value)

    def get_decks_of_cards(self, cards):
        params = {
            "cards": cards
        }
        return self._invoke(DeckEnum.GET_DECKS_OF_CARDS.value, **params)

    def create_deck(self, name):
        params = {
            "deck": name
        }
        return self._invoke(DeckEnum.CREATE_DECKS.value, **params)

    def get_models(self):
        return self._invoke(ModelEnum.GET_MODEL_NAMES_AND_ID.value)

    def get_model_field_names(self, model_name):
        params = {
            "modelName": model_name
        }
        return self._invoke(ModelEnum.GET_MODEL_NAMES_AND_ID.value, **params)

    def createModel(self, model_name, field_order, cardTemplates, css=None):
        params = {
            "modelName": model_name,
            "inOrderFields": field_order,
            "cardTemplates": cardTemplates
        }
        if css is not None:
            params["css"] = css
        return self._invoke(ModelEnum.CREATE_MODEL.value, **params)

    def add_note(self, deck_name, model_name, fields, tags=None, audio=None):
        """
            Add note to a deck with model
            fields: a dict with keys is the field_name, values is the field_value
            tags: array of string tags
            audio: dict with url, filename, skipHash (optional), fields (an array of fields when the audio will be played)
        """
        audio = self._verify_audio(audio)
        params = {
            "note": {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": fields
            },
            "options": {
                "allowDuplicate": False
            },
            "tags": [] if tags is None else tags,
            "audio": [] if audio is None else audio
        }
        return self._invoke(NoteEnum.ADD_NOTE.value, **params)

    def delete_note(self, ids):
        params = {
            "notes": ids
        }
        return self._invoke(NoteEnum.DELETE_NOTES.value, **params)

    def store_media_file(self, file_name, data=None, url=None):
        params = {
            "filename": file_name
        }
        if data and url:
            raise Exception("Only data or url.")
        elif data:
            params["data"] = data
        elif url:
            params["url"] = url
        else:
            raise Exception("Insufficient data for media.")

        return self._invoke(MediaEnum.STORE_MEDIA_FILE.value, **params)

    def retrive_media_file(self, file_name):
        params = {
            "filename": file_name
        }

        return self._invoke(MediaEnum.RETRIEVE_MEDIA_FILE.value, **params)

    def delete_media_file(self, file_name):
        params = {
            "filename": file_name
        }

        return self._invoke(MediaEnum.DELETE_MEDIA_FILE.value, **params)

    @staticmethod
    def convert_image_to_base64(image_src):
        with open(image_src, "rb") as image:
            result = base64.b64encode(image.read())
        return result


if __name__ == "__main__":
    c = AnkiConnector()
    params = {
        "note": {
            "deckName": "test",
            "modelName": "2. Picture Words",
            "fields": {
                "Word": "Test",
                "Picture": '<img src="paste-5093831213178.jpg">',
                "Gender, Personal Connection, Extra Info (Back side)": "nope",
                "Pronunciation (Recording and/or IPA)": "/asd",
                "Test Spelling? (y = yes, blank = no)": "y"
            },
            "options": {
                "allowDuplicate": False
            },
            "tags": [],
            "audio": []
        }
    }
    res = c.invoke(NoteEnum.ADD_NOTE.value, **params)
    print(res)
