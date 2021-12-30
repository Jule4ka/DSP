from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
from flask_navigation import Navigation
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask("__name__")
nav = Navigation(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/pre-registration'
db = SQLAlchemy(app)
projects = [{}
            ]

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

@app.route('/scheduling-overview', methods=['GET', 'POST'])
def scheduling_overview():
    if request.method == 'POST':
        AssetName = request.form['AssetName']
        StartDate = request.form['start_date']

        if not AssetName:
            flash('Asset name is required!')
        elif not StartDate:
            flash('Start date is required!')
        else:
            projects.append({'AssetName': AssetName, 'StartDate': StartDate})
            return redirect(url_for('scheduling_overview'))

    return render_template("scheduling_overview.html")
    projects = projects

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)


# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
