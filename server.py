from flask import Flask, request
import ssl
import json
import base64

import common

# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# context.load_cert_chain('domain.crt', 'domain.key')

application = Flask(__name__)
users = {}
results = {}
diffie = {}
circuits = {}

@application.route('/')
def hello():
    return '\n'.join([
        "Hello World! This is the know-nothing dating service.",
        "POST /register"])


@application.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    public_key = request.form['public_key']

    if username in users:
        if users[username] != public_key:
            return json.dumps({
                'success': False,
                'error': 'User already exists'
                })

    users[username] = public_key
    return json.dumps({
        'success': True,
        })


@application.route('/users', methods=['GET', 'POST'])
def get_users():
    return json.dumps({
        'success': True,
        'users': users
        })


@application.route('/sendkey', methods=['POST'])
def send_key():
    me = request.form['me']
    them = request.form['them']
    epoch = int(request.form['epoch'])
    key = request.form['key'] # g^a in base64 encoding

    if epoch not in diffie:
        diffie[epoch] = {}

    if (me, them) in diffie[epoch] and diffie[epoch][(me, them)] != key:
        return json.dumps({
            'success': False,
            'error': 'Already sent key for this epoch & user'
            })

    diffie[epoch][(me, them)] = key
    return json.dumps({
        'success': True,
        })


@application.route('/sendcircuit', methods=['POST'])
def send_circuit():
    me = request.form['me']
    them = request.form['them']
    epoch = int(request.form['epoch'])
    wa, wb = request.form['wa'], request.form['wb']
    r1, r2 = request.form['r1'], request.form['r2']
    r3, r4 = request.form['r3'], request.form['r4']
    choice = request.form['choice']

    if epoch not in circuits:
        circuits[epoch] = {}

    if (me, them) in circuits[epoch]:
        # already sent
        return json.dumps({
            'success': False,
            })

    circuits[epoch][(me, them)] = [wa, wb, r1, r2, r3, r4, choice]

    if (them, me) in circuits[epoch]:
        if me < them:
            verify_params = (
               map(base64.b64decode, circuits[epoch][(me, them)]),
               map(base64.b64decode, circuits[epoch][(them, me)]))
        else:
            verify_params = (
               map(base64.b64decode, circuits[epoch][(them, me)]),
               map(base64.b64decode, circuits[epoch][(me, them)]))
        result = common.verify(*verify_params)

        if epoch not in results:
            results[epoch] = {}
        results[epoch][(me, them)] = result
        results[epoch][(them, me)] = result

    return json.dumps({
        'success': True,
        })


@application.route('/getkey', methods=['GET', 'POST'])
def get_key():
    me = request.form['me']
    them = request.form['them']
    epoch = int(request.form['epoch'])

    if epoch not in diffie:
        return json.dumps({
            'success': False,
            })

    if (them, me) in diffie[epoch]:
        return json.dumps({
            'success': True,
            'key': diffie[epoch][(them, me)]
            })

    return json.dumps({
        'success': False,
        })


@application.route('/result', methods=['GET', 'POST'])
def get_result():
    me = request.form['me']
    them = request.form['them']
    epoch = int(request.form['epoch'])

    if epoch in results:
        if (me, them) in results[epoch]:
            return json.dumps({
                'success': True,
                'result': results[epoch][(me, them)]
                })

    return json.dumps({
        'success': False,
        })


if __name__ == "__main__":
    application.run(debug=True, threaded=False)
