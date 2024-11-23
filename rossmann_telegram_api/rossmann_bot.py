import os
import json
import time
import requests
import pandas as pd 
from flask import Flask, request, Response

import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


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

def delete_message(chat_id, message_id, token):
    url = f"https://api.telegram.org/bot{token}/deleteMessage"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Mensagem {message_id} deletada com sucesso.")
    else:
        print(f"Falha ao deletar mensagem {message_id}. Status Code: {response.status_code}")

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
    url = 'https://ds-em-producao-n8qd.onrender.com/machine_learning_api/predict'

    header = {'Content-type': 'application/json'}

    r = requests.post(url, data=data, headers=header)
    r.raise_for_status()
    
    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1

def parse_message(message):
    chat_id = message['message']['chat']['id']
    message_id = message['message']['message_id']

    if 'text' in message['message']:

        store_id = message['message']['text']

        store_id = store_id.replace('/' , '')
        if store_id == 'start':
            send_message(chat_id, "Hello! I am the sales prediction bot. Send a store number to receive the sales forecast!")
            msg = ("To activate the prediction algorithm, click on the link and return to Telegram: https://ds-em-producao-n8qd.onrender.com")
            send_message(chat_id, msg)
            msg = ("This process may take a few minutes")
            send_message(chat_id, msg)
            return chat_id, store_id, message_id

        try:
            store_id = int(store_id)

        except ValueError:
            store_id = 'error'

        return chat_id, store_id, message_id
    
    else:
        send_message(chat_id, 'Message is not text. deleted...')
        delete_message(chat_id, message_id, TOKEN)
        return None, None, None

def create_chart(data, store_id):
    data['date'] = pd.to_datetime(data['date'])

    sales = data['prediction']
    start_date = data['date'][0]
    dates = data['date']

    fig, ax = plt.subplots(figsize=(14, 8))

    bar_color = '#A6ACAF'  # Cinza
    highlight_color = '#C0392B'  # Vermelho 


    bars = ax.bar(dates, sales, label=f'Store {store_id}', color=bar_color, edgecolor='#778899', linewidth=1.5)

    df = pd.DataFrame({'date': dates, 'sales': sales})

    # coluna nome dia da semana
    df['weekday'] = df['date'].dt.strftime('%A')

    # coluna número da semana
    df['week'] = df['date'].dt.isocalendar().week

    # dia com mais vendas por semana
    top_days_per_week = df.loc[df.groupby('week')['sales'].idxmax()]

    # Plot valores e dias da semana de maior faturamento 
    for _, row in top_days_per_week.iterrows():
        ax.annotate(f"${row['sales']:,.0f}", 
                    (row['date'], row['sales']), 
                    textcoords="offset points", 
                    xytext=(-5, 10), ha='center', fontsize=12, color=highlight_color, fontweight='bold')
        ax.annotate(f"{row['weekday']}", 
                    (row['date'], row['sales']), 
                    textcoords="offset points", 
                    xytext=(-5, 25), ha='center', fontsize=12, color='black')  

    # formato das datas no eixo X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

    # intervalo para as datas no eixo X 
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True) 
    ax.spines['bottom'].set_visible(True)  
    ax.xaxis.label.set_visible(False)

    # subindo o eixo y
    ax.set_ylim(0, sales.max() * 1.2)

    # Melhorando a grade
    ax.grid(True, linestyle='--', alpha=0.5)

    # Caixa total de vendas
    total_sales = df['sales'].sum()
    plt.text(0.98, 1, f'Total Sales: ${total_sales:,.0f}', ha='right', va='top', fontsize=20, 
            bbox=dict(facecolor='white', edgecolor=highlight_color, boxstyle='round,pad=0.7', alpha=1), fontweight='normal', transform=ax.transAxes)


    ax.set_title(' ', fontsize=10, color='#2C3E50',y=1) 
    # ax.set_xlabel('Date', fontsize=12, color='#2C3E50') 
    ax.set_ylabel(f'Predicted Sales for Store {store_id}', fontsize=14, color='#2C3E50')  


    filepath = f'temp_chart_{store_id}.png'
    plt.savefig(filepath)
    plt.close()  

    return filepath

def send_chart(chat_id, filepath):
    url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
    with open(filepath, 'rb') as photo:
        r = requests.post(url, data={'chat_id': chat_id}, files={'photo': photo})

    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("Gráfico enviado com sucesso!")
    else:
        print(f"Erro ao enviar gráfico: {r.text}")


# API initialize 
app = Flask(__name__) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.get_json()
        print(f"Payload recebido: {message}")

        chat_id, store_id, message_id = parse_message(message)
        print(f"Store_ID: {store_id}")

        if store_id not in ['error', 'start']:
            # Lading data
            data = load_dataset(store_id)
                        
            # Prediction
            if data != 'error':
                i=0
                while True:
                    try:
                        d1 = predict(data)
                        break
                    except Exception as e:
                        i+=1
                        print(i)
                        if i%18==0:
                            send_message(chat_id, "Please, activate the algorithm with the link. To info send the /start message")
                        time.sleep(10)
                        if i==36:
                            send_message(chat_id, "time exceeded")
                            delete_message(chat_id, message_id, TOKEN)
                            break


                # Calculation
                d2 = d1[['store', 'prediction']].groupby('store').sum('prediction').reset_index()

                # Criar e enviar gráfico
                filepath = create_chart(d1, store_id)
                send_chart(chat_id, filepath)

                # Send message    
                msg = (f'Store Number {d2["store"].values[0]}: will sell ${d2["prediction"].values[0]:,.2f} in the next 6 weeks')
                send_message(chat_id, msg)

                os.remove(filepath)
                return Response('OK', status=200)
            else:
                send_message(chat_id, 'Store Not Available')
                return Response('OK', status=200)
        else:
            if store_id == 'start':
                return Response('OK', status=200)
            else:
                send_message(chat_id, 'Store ID is Wrong')
                return Response('OK', status=200)
    else:
        return '<h1>Rossman Telegram BOT | <a href="https://t.me/TheRossmannBot" target="_blank">link</a></h1>'
if __name__ == '__main__':

    port = os.environ.get('PORT',5000)
    app.run(host='0.0.0.0', port =port)

