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

    try:
        r = requests.post(url, data=data, headers=header, timeout=120)
        r.raise_for_status()
    
    
    except Exception as e:
        print(f"Erro ao fazer POST: {e}")
        print("Tentando reativar a API...")
        r = requests.get('https://ds-em-producao-n8qd.onrender.com/machine_learning_api/predict', timeout=120)
        print("Ativando API!")
        time.sleep(60)

        if r.status_code == 200:
            print("API ativada com sucesso!")
            predict(data)
        else:
            print(f"Falha ao acessar a API. Status Code: {r.status_code}")

    print('Status Code {}!!'.format( r.status_code ))

    d1 = pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1

def parse_message(message):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace('/' , '')
    if store_id == 'start':
        send_message(chat_id, "Hello! I am the sales prediction bot. Send a store number to receive the sales forecast!")
        send_message(chat_id, "On the first interaction after a long period of inactivity, the response might take up to a minute.")
        return chat_id, store_id

    try:
        store_id = int(store_id)

    except ValueError:
        store_id = 'error'


    return chat_id, store_id

def create_chart(data, store_id):
    data['date'] = pd.to_datetime(data['date'])

    sales = data['prediction']
    start_date = data['date'][0]
    dates = data['date']

    # Criando a figura e o eixo
    fig, ax = plt.subplots(figsize=(14, 8))

    # Paleta de cores
    bar_color = '#A6ACAF'  # Cinza
    highlight_color = '#C0392B'  # Vermelho 

    # Criando o gráfico de barras com cores personalizadas (cinza)
    bars = ax.bar(dates, sales, label=f'Store {store_id}', color=bar_color, edgecolor='#778899', linewidth=1.5)

    # Criando um DataFrame para manipulação
    df = pd.DataFrame({'date': dates, 'sales': sales})

    # Adicionando uma coluna com o nome do dia da semana
    df['weekday'] = df['date'].dt.strftime('%A')

    # Adicionando uma coluna com o número da semana
    df['week'] = df['date'].dt.isocalendar().week

    # Encontrando o dia com mais vendas por semana
    top_days_per_week = df.loc[df.groupby('week')['sales'].idxmax()]

    # Plotando os valores e os dias da semana dos dias de maior faturamento por semana
    for _, row in top_days_per_week.iterrows():
        ax.annotate(f"${row['sales']:,.0f}", 
                    (row['date'], row['sales']), 
                    textcoords="offset points", 
                    xytext=(-5, 10), ha='center', fontsize=12, color=highlight_color, fontweight='bold')
        ax.annotate(f"{row['weekday']}", 
                    (row['date'], row['sales']), 
                    textcoords="offset points", 
                    xytext=(-5, 25), ha='center', fontsize=12, color='black')  

    # Configurando o formato das datas no eixo X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

    # Definindo o intervalo para as datas no eixo X (semanal)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(True) 
    ax.spines['bottom'].set_visible(True)  
    ax.xaxis.label.set_visible(False)

    # Ajustando as margens
    ax.set_ylim(0, sales.max() * 1.2)

    # Melhorando a grade
    ax.grid(True, linestyle='--', alpha=0.5)

    # Calculando o total de vendas
    total_sales = df['sales'].sum()

    # Adicionando a caixa com o total de vendas no canto superior direito
    plt.text(0.98, 1, f'Total Sales: ${total_sales:,.0f}', ha='right', va='top', fontsize=20, 
            bbox=dict(facecolor='white', edgecolor=highlight_color, boxstyle='round,pad=0.7', alpha=1), fontweight='normal', transform=ax.transAxes)


    ax.set_title(' ', fontsize=10, color='#2C3E50',y=1)  # Título em cinza escuro
    # ax.set_xlabel('Date', fontsize=12, color='#2C3E50')  # Rótulo X em cinza escuro
    ax.set_ylabel(f'Predicted Sales for Store {store_id}', fontsize=14, color='#2C3E50')  # Rótulo Y em cinza escuro

    # Salvando o gráfico como imagem
    filepath = f'temp_chart_{store_id}.png'
    plt.savefig(filepath)
    plt.close()  # Fecha o gráfico para economizar memória

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

        chat_id, store_id = parse_message(message)
        print(f"Store_ID: {store_id}")

        if store_id not in ['error', 'start']:
            # Lading data
            data = load_dataset(store_id)
            
            # Prediction
            if data != 'error':
                    
                d1 = predict(data)

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




