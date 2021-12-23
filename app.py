from flask import Flask, render_template, request
import pandas as pd
from flask_navigation import Navigation

app = Flask("__name__")


@app.route('/', methods=['GET', 'POST'])
def assets_overview():
    return render_template("start.html")


@app.route('/assets-overview', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        dataset = pd.read_excel("data/Gemeente Almere bruggen paspoort gegevens.xlsx")
        return render_template('assets-overview.html', data=dataset.to_html())
        #return render_template('assets-overview.html', data=dataset.to_dict())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
