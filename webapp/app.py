from flask import Flask, render_template, request, jsonify

from bokeh.client import pull_session
from bokeh.embed import server_session

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # pull a new session from a running Bokeh server
    with pull_session(url="http://localhost:5006/bokeh_app") as session:

        # generate a script to load the customized session
        script = server_session(session_id=session.id, url='http://localhost:5006/bokeh_app')

        return render_template('index.html',
                               script=script,
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



# http://localhost:5000/patient/EEG_MEG/[1,2,3]/[4,5,6]?id=0
@app.route('/patient/EEG_MEG/<EEG>/<MEG>', methods=['GET'])
def get_patient_data(EEG, MEG):
    if 'id' in request.args:
        id = request.args['id']

    else:
        return "Error: No id field provided. Please provide patient id"



    patient_id = "{0:03}".format(int(id))
    path_to_patient = f"..\\data\\ICA_processed\\sub{patient_id}"

    print(EEG)
    print(MEG)





    """
    call the correct channels, return template with those channels that are shown
    """

    results = []


    # return render_template('template', patients = results)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=5000)