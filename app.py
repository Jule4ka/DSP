from flask import Flask, render_template, request
import pandas as pd
from flask_navigation import Navigation

app = Flask("__name__")
nav = Navigation(app)

# initializing navigation
nav.Bar('top', [
    nav.Item('Assets Overview', 'assets_overview'),
    nav.Item('Asset Components', 'asset_components')
])


@app.route('/')
def navpage():
    return render_template("navpage.html", title="Home Page")


@app.route('/assets_overview', methods=['GET', 'POST'])
def assets_overview():
    dataset = pd.read_excel("data/Gemeente Almere bruggen paspoort gegevens.xlsx")
    return render_template('assets_overview.html', data=dataset.to_html(), title="Assets Overview")
    # return render_template('assets_overview.html', data=dataset.to_dict()) #transform to dictionary


@app.route('/asset-components', methods=['GET', 'POST'])
def asset_components():
    return render_template("asset_components.html", title="Asset Components")


@app.route('/register')
def register():
    return render_template('register.html', title="Register")


@app.route('/login')
def login():
    return render_template('login.html', title="Login")


# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
