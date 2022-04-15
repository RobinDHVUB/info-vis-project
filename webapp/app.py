import os

from flask import Flask, render_template, request, jsonify

from bokeh.client import pull_session
from bokeh.embed import server_document
import mne
import ast

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # pull a new session from a running Bokeh server


    # generate a script to load the customized session
    #script = server_document(url='http://localhost:5006/bokeh_app', arguments={"eeg":"fp,p2,f4"})



    return render_template('index.html',
                           #script=script,
                           title="Info Viz Example",
                           paragraph_title="Testing123")


patients = [
    {'id': 0,
     'name': 'patient 0',
     'age': 23,
     'gender': 'man'},
    {'id': 1,
     'name': 'patient 1',
     'age': 29,
     'gender': 'woman'}] # hier data van patients (age, gender, etc)

# http://localhost:5000/patients?id=0&id=1
@app.route('/patients', methods=['GET'])
def get_patients():
    if 'id' in request.args:
        id = request.args.getlist('id')

    else:
        return "Error: No id field provided. Please provide patient id"

    results = []

    for patient in patients:
        for patient_id in id:
            if patient['id'] == int(patient_id):
                results.append(patient)

    # return render_template('template', patients = results)
    return jsonify(results)

@app.route('/data', methods=['GET'])
def show_data():
    if 'id' in request.args:
        id = request.args.getlist('id')

    else:
        return "Error: No id field provided. Please provide patient id"

    if 'MEG' in request.args:
        MEG = request.args.get('MEG')

    else:
        return "Error: No MEG field provided. Please provide patient MEG"


    if 'EEG' in request.args:
        EEG = request.args.get('EEG')

    else:
        return "Error: No EEG field provided. Please provide patient EEg"

    results = []

    patient_id = "{0:03}".format(int(id[0]))
    parent_dir = os.path.abspath(os.pardir)
    path_to_patient = parent_dir + f"\\data\\ICA_processed\\sub{patient_id}\\0.fif"



    print(EEG.split(","))
    # print(ast.literal_eval(EEG))
    # print(ast.literal_eval(MEG))

    # return render_template('template', patients = results)

    script = server_document(url='http://localhost:5006/bokeh_app', arguments={"eeg": "fp,p2,f4"})
    return render_template('index.html',
                           script=script,
                           title="Info Viz Example",
                           paragraph_title="Testing123")


if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)