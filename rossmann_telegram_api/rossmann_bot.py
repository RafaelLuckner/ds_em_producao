import os
import json
import requests
import pandas as pd 
from flask import Flask, request, Response

# constans 
TOKEN =  '7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM'

# # info about the bot
# https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/getMe

# # get uptade 
# https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/getUpdates

# # webhook 
# https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/setWebhook?url=https://38bc9190bea9b0.lhr.life

# # webhook render
# https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/setWebhook?url=https://bot-telegram-nqm9.onrender.com


# # send Message
# https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/sendMessage?chat_id=6056307810&text=Hi Biruliru, I am doing good, tks!

# 6056307810

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/'
    url = url + f'sendMessage?chat_id={chat_id}&'
    
    r = requests.post(url, json={'text':text})
    print(f'Status Code {r.status_code}')

    return None
    

    # send Message
    # https://api.telegram.org/bot7805674894:AAF4Ykx5n5QlERyhtI7L7c-brdVkqNKi3bM/sendMessage?chat_id=6056307810&text=Hi Biruliru, I am doing good, tks!


def load_dataset(store_id):
    # loading test dataset
    df10 = pd.read_csv('test.csv')
    df_store_raw = pd.read_csv('store.csv')
    # merge test dataset + store
    df_test = pd.merge(df10, df_store_raw, how = 'left', on= 'Store')

    df_test = df_test[df_test['Store'] == store_id]

    if df_test.empty:
        return 'error'
     
    # remove closed days
    df_test = df_test[df_test['Open']!= 0]
    df_test = df_test[~df_test['Open'].isnull()]
    df_test = df_test.drop('Id', axis=1)

    # convert DataFrame to json
    data = json.dumps(df_test.to_dict( orient = 'records'))
    return data


def predict(data):
        # API Call
    url = 'https://ds-em-producao-n8qd.onrender.com/rossmann/predict'

    header = {'Content-type': 'application/json'}

    r = requests.post(url, data = data, headers = header)

    print('Status Code {}'.format( r.status_code ))

    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1


def parse_message(message):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']
    
    store_id = store_id.replace('/' , '')

    try:
        store_id = int(store_id)

    except ValueError:
        store_id = 'error'


    return chat_id, store_id


# API initialize 
app = Flask(__name__) 

@app.route( '/', methods = ['GET', 'POST'])

def index():
    if request.method == 'POST':
        message = request.get_json()
        print(f"Payload recebido: {message}")

        chat_id, store_id = parse_message(message)

        if store_id != 'error':
            # lading data
            data = load_dataset(store_id)
            # prediction
            if data != 'error':
                d1 = predict(data)

                # calculation
                d2 = d1[['store','prediction']].groupby('store').sum('prediction').reset_index()

                # send message    

                msg = (f'Store Number {d2["store"].values[0]}: will sell ${d2["prediction"].values[0]:,.2f} in the next 6 weeks')

                send_message(chat_id, msg)
                return Response( 'OK', status = 200)
            
            else:
                send_message(chat_id, 'Store Not Available')
                return Response( 'OK', status = 200)       
             
        else: 
            send_message(chat_id, 'Store ID is Wrong')
            return Response( 'OK', status = 200)

    else:
        return '<h1> Rossman Telegran BOT </h1>'


if __name__ == '__main__':
    port = os.environ.get('PORT',5000)
    app.run(host='0.0.0.0', port =port)




