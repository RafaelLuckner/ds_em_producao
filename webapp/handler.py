import os
import pickle
import pandas as pd
from flask import Flask, request, Response
from rossmann.Rossmann import Rossmann

# load model
model = pickle.load( open('model/model_russmann.pkl', 'rb'))

# initialize API
app = Flask(__name__)

@app.route( '/machine_learning_api/predict', methods = ['POST'])
def rossmann_predict():
    test_json = request.get_json()

    if test_json: # there is data
        if isinstance( test_json, dict): #unique example
            test_raw = pd.DataFrame(test_json, index=[0])

        else: # multiple example 
            test_raw = pd.DataFrame(test_json, columns= test_json[0].keys() )

        # instance Rossmann class
        pipeline = Rossmann()

        # data cleaning
        df1 = pipeline.data_cleaning( test_raw )

        # feature engeneering 
        df2 = pipeline.feature_engeneering(df1)

        # data preparation
        df3 = pipeline.data_preparation(df2)

        # prediction 
        df_response = pipeline.get_prediction(model, test_raw, df3)
        return df_response

    else: 
        return Response('{}', status = 200, mimetype = 'application/json')

if __name__ == '__main__':
    port = os.environ.get('PORT',5000)
    
    app.run('0.0.0.0', port = port)













