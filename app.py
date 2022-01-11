from flask import Flask, render_template, request, url_for, flash, redirect, session
import pandas as pd
from flask_navigation import Navigation
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf import FlaskForm
from wtforms import FileField
import os

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
nav = Navigation(app)

#code for connection
#MySQL Hostname
app.config['MYSQL_HOST'] = 'localhost'
#MySQL username
app.config['MYSQL_USER'] = 'root'
#MySQL password here in my case password is null so i left empty
app.config['MYSQL_PASSWORD'] = 'DSPB1'
#Database name In my case database name is projectreporting
app.config['MYSQL_DB'] = 'dummy_db'

mysql = MySQL(app)


# Define dict for new projects
projects = {'AssetName': [], 'StartDate':[], 'Maintainer': [],
            'Owner': [], 'Width': [], 'Length': [],
            'Area': [], 'Location': []}

# initializing navigation
nav.Bar('top', [
    nav.Item('Assets Overview', 'assets_overview'),
    nav.Item('Components Overview', 'components_overview'),
    nav.Item('Marketplace', 'marketplace')
])


@app.route('/', methods=['GET', 'POST'])
def navpage():
    return render_template("navpage.html", title="Home Page")

@app.route('/marketplace', methods=['GET','POST'])
def marketplace():
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from dummy_data_marketplace")
    # fetching all records from database
    data = cursor.fetchall()

    for dict_row in data:
        for key, value in dict_row.items():
            print(type(value))
    # returning back to projectlist.html with all records from MySQL which are stored in variable data
    return render_template("marketplace.html", data=data)


@app.route('/assets_overview', methods=['GET', 'POST'])
def assets_overview():
    dataset = pd.read_excel("data/Gemeente Almere bruggen paspoort gegevens.xlsx")
    dataset = dataset.reindex(columns=dataset.columns.tolist() + ['Open_Asset'])
    # rename column titles
    dataset.columns = [c.replace(' ', '_') for c in dataset.columns]
    dataset_to_display = dataset[
        ["Assetnumber", "AssetName", "AssetType", "Maintainance_State", "Buildyear", "Maintainer",
         "Owner", "Status", "Location", "City", "Open_Asset"]]
    # link_column is the column that I want to add a button to
    return render_template("assets_overview.html", column_names=dataset_to_display.columns.values,
                           row_data=list(dataset_to_display.values.tolist()),
                           link_column="Open_Asset", zip=zip, title="Assets Overview")
    # return render_template('assets_overview.html', data=dataset_to_display.to_html(), title="Assets Overview")
    # return render_template('assets_overview.html', data=dataset.to_dict()) #transform to dictionary


@app.route('/asset-components', methods=['GET', 'POST'])
def asset_components():
    #table
    record_id=int(request.args['record_id'])
    if request.method == 'GET':
        components_dataset = pd.read_excel("data/Gemeente Almere bruggen components dummy.xlsx")
        components_dataset = components_dataset.loc[components_dataset['Assetnumber'] == record_id]
        #image
        img1 = os.path.join(app.config['UPLOAD_FOLDER'])
        #uploadbutton
        form = MyForm()
        if form.validate_on_submit():
            filename = images.save(form.image.data)
            return f'Filename: {filename}'
        return render_template("asset_components.html", column_names=components_dataset.columns.values,
                               row_data=list(components_dataset.values.tolist()),
                               zip=zip, title="Asset Components", user_image = img1, form = form)

@app.route('/register')
def register():
    return render_template('register.html', title="Register")


@app.route('/login')
def login():
    return render_template('login.html', title="Login")

@app.route('/scheduling-overview', methods=['GET', 'POST'])
def scheduling_overview():  # Provide forms for input
    if request.method == 'POST':
        AssetName = request.form['AssetName']
        StartDate = request.form['start_date']
        Maintainer = request.form['Maintainer']
        Owner = request.form['Owner']
        Width = request.form['Width']
        Length = request.form['Length']
        Area = request.form['Area']
        Location = request.form['Location']

        if not AssetName:  # Error message if fields are not filled out
            flash('Asset name is required!')
        elif not StartDate:
            flash('Start date is required!')
        else:  # Add input to project dict
            projects['AssetName'].append(AssetName)
            projects['StartDate'].append(StartDate)
            projects['Maintainer'].append(Maintainer)
            projects['Owner'].append(Owner)
            projects['Width'].append(Width)
            projects['Length'].append(Length)
            projects['Area'].append(Area)
            projects['Location'].append(Location)
            with open('planned_projects.txt', 'a') as f:  # Add input to txt file. This is supposed to be used in the app
                print(projects, file=f)

            return redirect(url_for('scheduling_overview'))

    projects_df = pd.DataFrame.from_dict(projects)  # Transfrom project dict to DataFrame (this is now used in the App)

    #with open('planned_projects.txt', 'r')

    return render_template("scheduling_overview.html",
                           projects=projects,
                           projects_df=projects_df,
                           tables=[projects_df.to_html(classes='data', header="true")])

## IMPORT image
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

class MyForm(FlaskForm):
    image = FileField('image')

# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
