import requests

import common

url = 'http://localhost:5000'


class Client(object):
    def __init__(self, username, epoch, private_key, public_key):
        self.username = username
        self.private_key = private_key
        self.public_key = public_key
        self.epoch = epoch
        self.my_keys = {}
        self.their_keys = {}
        self.circuits = {}

    def register(self):
        r = requests.post(url+'/register', data={
            'username': self.username,
            'public_key': self.public_key}).json()
        return r['success']

    def users(self):
        r = requests.get(url+'/users').json()
        return r['users']

    def initiate(self, user):
        key = common.DH_get_key_pair()
        r = requests.post(url+'/sendkey', data={
            'me': self.username,
            'them': user,
            'epoch': self.epoch,
            'key': key[1]}).json()

        if r['success']:
            self.my_keys[user] = key[0]

        return r['success']

    def get_key(self, user):
        r = requests.get(url+'/getkey', data={
            'me': self.username,
            'them': user,
            'epoch': self.epoch}).json()

        if r['success']:
            self.their_keys[user] = r['key']

        return r['success']

    def send_circuit(self, user, choice):
        if user not in self.my_keys or user not in self.their_keys:
            print "Keys are not ready yet (call initiate and get_key first)"
            return None

        shared_key = common.DH_get_shared(self.my_keys[user], self.their_keys[user])
        c = common.generate_circuit(shared_key, choice, self.username < user)
        r = requests.post(url+'/sendcircuit', data={
            'me': self.username,
            'them': user,
            'epoch': self.epoch,
            'wa': c['wa'],
            'wb': c['wb'],
            'r1': c['r1'],
            'r2': c['r2'],
            'r3': c['r3'],
            'r4': c['r4'],
            'choice': c['choice'],
            }).json()

        if r['success']:
            self.circuits[user] = c
        return r['success']

    def get_result(self, user):
        r = requests.get(url+'/result', data={
            'me': self.username,
            'them': user,
            'epoch': self.epoch}).json()

        if r['success']:
            c = self.circuits[user]
            if r['result'] == c['true']:
                return True
            elif r['result'] == c['false']:
                return False
        return None
