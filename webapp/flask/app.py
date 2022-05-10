import os

from flask import Flask, Blueprint, render_template, request, jsonify

from bokeh.client import pull_session
from bokeh.embed import server_document
import mne
import json
import ast

app = Flask(__name__)

# add a blueprint to have access to the processed data folder as a static resource
blueprint = Blueprint('data', __name__, static_url_path='/static/subject-data', static_folder='data/processed')
app.register_blueprint(blueprint)

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    # render the main page for subject selection
    return render_template(
        "index.html",
        title="A multi-subject, multi-modal human neuroimaging dataset",
        title_url="https://www.nature.com/articles/sdata20151"
    )


@app.route("/data-analysis", methods=["POST"])
def data_analysis():
    # this route is expected to be accessed via AJAX

    # get the JSON from the AJAX call and use it to serve a Bokeh document based on the request's data
    data = request.json
    script = server_document(
        url="http://localhost:5006/app", arguments={"id": data["subject"],
                                                    "EEG": json.dumps(data["eeg"]),
                                                    "MEG": json.dumps(data["meg"])}
    )

    # render the Bokeh document and embed it in the given wrapper template
    return render_template(
        "bokeh-wrapper.html",
        script=script,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
