import requests
import numpy as np

key = '3e45014c6465df422ec100f100892125'
token = '56527009f8e75488442c4d88417af348c86e32e03d2852286f0d0fe580c45051'

class Card:
    def __init__(self, name, group, label):
        self.name = name
        self.group = group
        self.board = self.group.board
        self.id = None
        self.label = label

    def make(self):
        url = "https://api.trello.com/1/cards"
        query = {"idList": self.group.id, "idLabels": self.board.labels[self.label], "name": self.name, "key": key, "token": token}
        response = requests.request("POST", url, params=query)
        self.id = response.json()['id']

class Group:
    def __init__(self, name, board, cards):
        self.name = name
        self.board = board
        self.cards = self.build_cards(cards)
        self.id = None

    def build_cards(self, cards):
        card_list = []
        for card in cards:
            card_list.append(Card(card['name'], self, card['label']))
        return card_list

    def make(self):
        url = "https://api.trello.com/1/lists"
        query = {"name": self.name, "idBoard": self.board.id, "key": key, "token": token}
        response = requests.request("POST", url, params=query).json()
        self.id = response['id']
        for card in self.cards:
            card.make()

class Board:
    def __init__(self, name, groups):
        self.name = name
        self.labels = self.parse_labels(groups)
        self.groups = self.build_groups(groups)

    def build_groups(self, groups):
        group_list = []
        for group in groups:
            group_list.append(Group(group['name'], self, group['cards']))
        return group_list

    def make(self):
        url = 'https://api.trello.com/1/boards'
        query = {'name': self.name, 'defaultLabels': 'false', 'defaultLists': 'false', 'key': key, 'token': token}
        response = requests.request("POST", url, params = query).json()
        self.id = response['id']
        self.make_labels()
        for group in reversed(self.groups):
            group.make()

    def parse_labels(self, groups):
        labels = set()
        for group in groups:
            for card in group['cards']:
                labels.add(card['label'])
        return labels

    def make_labels(self):
        labels = {}
        for label in self.labels:
            url = "https://api.trello.com/1/labels"
            query = {"name": "", "color": label, "idBoard": self.id, "key": key, "token": token}
            response = requests.request("POST", url, params=query)
            labels[label] = response.json()['id']
        self.labels = labels

    def invite(self, name, email):
        url = "https://api.trello.com/1/boards/{}/members".format(self.id)
        query = {"email": email, "key": key, "token": token}
        payload = "{\"fullName\":\"" + name + "\"}"
        headers = {
            'type': "admin",
            'content-type': "application/json"
            }
        response = requests.request("PUT", url, data=payload, headers=headers, params=query)


if __name__ == "__main__":
    groups = [{'name': 'group 1', 'cards': [{'name':'a card', 'label': 'pink'}, {'name': 'another card', 'label': 'green'}]},
        {'name': 'group 2', 'cards': [{'name': 'a 2nd list card', 'label': 'pink'}, {'name': 'a 2nd 2nd list card', 'label': 'yellow'}]}]
    
    board = Board('testBoard', groups)
    print('board built')
    board.make()
