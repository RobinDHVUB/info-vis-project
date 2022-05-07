import os

from flask import Flask, render_template, request, jsonify

from bokeh.client import pull_session
from bokeh.embed import server_document
import mne
import json
import ast

app = Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    # pull a new session from a running Bokeh server

    # generate a script to load the customized session
    # script = server_document(url='http://localhost:5006/bokeh_app', arguments={"eeg":"fp,p2,f4"})

    return render_template(
        "index.html",
        # script=script,
        title="A multi-subject, multi-modal human neuroimaging dataset",
        title_url="https://www.nature.com/articles/sdata20151"
    )


@app.route("/data", methods=["POST"])
def show_data():
    data = request.json
    script = server_document(
        url="http://localhost:5006/app", arguments={"id": data["subject"],
                                                    "EEG": json.dumps(data["eeg"]),
                                                    "MEG": json.dumps(data["meg"])}
        #arguments={"id": 1, "EEG": "EEG001", "MEG": "MEG0111"}
    )
    return render_template(
        "bokeh-wrapper.html",
        script=script,
    )


if __name__ == "__main__":
    #from data.parse import parse_meg_coords, parse_meg_names

    #print(parse_meg_names())
    #print(parse_meg_coords())
    app.run(debug=True, host="0.0.0.0", port=5000)
