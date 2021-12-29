from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
from flask_navigation import Navigation

app = Flask("__name__")
nav = Navigation(app)
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
    dataset = dataset.reindex(columns=dataset.columns.tolist() + ['Open_Asset'])
    # rename column titles
    dataset.columns = [c.replace(' ', '_') for c in dataset.columns]
    dataset_to_display = dataset[["Assetnumber", "AssetName", "AssetType", "Maintainance_State", "Buildyear", "Maintainer",
                                  "Owner", "Status", "Location", "City", "Open_Asset"]]
    # link_column is the column that I want to add a button to
    return render_template("assets_overview.html", column_names=dataset_to_display.columns.values,
                           row_data=list(dataset_to_display.values.tolist()),
                           link_column="Open_Asset", zip=zip)

    #return render_template('assets_overview.html', data=dataset_to_display.to_html(), title="Assets Overview")
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


# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
