from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title="Info Viz Example", paragraph_title="Testing123")


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


@app.route('/patient/EEG_MEG', methods=['GET'])
def get_patient_data():
    if 'id' in request.args:
        id = request.args['id']

    else:
        return "Error: No id field provided. Please provide patient id"

    if 'EEG' in request.args:
        EEG_channels = request.args.getlist('EEG')

    else:
        return "Error: No EEG field provided. Please provide patient EEG channel numbers"

    if 'MEG' in request.args:
        MEG_channels = request.args.getlist('MEG')

    else:
        return "Error: No MEG field provided. Please provide patient MEG channel numbers"

    patient_id = "{0:03}".format(int(id))
    path_to_patient = f"..\\data\\ICA_processed\\sub{patient_id}"



    """
    call the correct channels, return template with those channels that are shown
    """

    results = []


    # return render_template('template', patients = results)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)