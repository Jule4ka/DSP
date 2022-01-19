import random as rand

from flask import Flask, render_template, request, url_for, flash, redirect, session, Response
import pandas as pd
from flask_navigation import Navigation
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField
import os
import uuid
from sqlalchemy import create_engine
import math

app = Flask(__name__, static_url_path='')
nav = Navigation(app)

# code for connection
# MySQL Hostname
app.config['MYSQL_HOST'] = 'localhost'
# MySQL username
app.config['MYSQL_USER'] = 'root'
# MySQL password here in my case password is null so i left empty
app.config['MYSQL_PASSWORD'] = 'root'
# Database name In my case database name is projectreporting
app.config['MYSQL_DB'] = 'dummy_db'

mysql = MySQL(app)

# Define dict for new projects
projects = {'AssetName': [], 'StartDate': [], 'Maintainer': [],
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


@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    project_list = ''
    project_id = ''
    project_names = None
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # executing query
        cursor.execute("select assetname, project_id from projects where %s = user_id", (session['email'],))
        project_names = cursor.fetchall()
        project_id = request.args.get("project_id")

    finally:
        # creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # executing query
        cursor.execute("select * from components where status = 'Published'")
        # fetching all records from database
        data = cursor.fetchall()
        if request.method == "POST":
            if request.form['action'] == 'Delete All Selected':  # check whether form comes from delete
                msg = ''
                for getid in request.form.getlist('mycheckbox'):
                    cursor.execute("delete from components where component_id= %s", [getid])
                    mysql.connection.commit()
                    msg = 'Successfully deleted'
                if (not msg): msg = "There is nothing to delete"
                return redirect(url_for('marketplace'))

        # returning back to projectlist.html with all records from MySQL which are stored in variable data
        return render_template("marketplace.html", data=data, project_names=project_names, project_id=project_id)


@app.route('/component_page.html', methods=['GET', 'POST'])
def component_page():
    record_id = request.args.get("record_id")

    # Fetch component specific data
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from components WHERE component_id=%s", [record_id])
    component_data = cursor.fetchall()

    # Fetch user data
    cursor.execute("select * from accounts WHERE email=(select owner_email from components WHERE component_id=%s)",
                   [record_id])
    user_data = cursor.fetchall()

    # Fetch similar components
    cursor.execute("select * from components where category=%s and component_id<>%s",
                   [component_data[0]['category'], record_id])
    similar_components_data = cursor.fetchall()
    return render_template("component_page.html", component_data=component_data,
                           similar_components_data=similar_components_data,
                           user_data=user_data
                           , record_id=record_id)


@app.route('/assets_overview', methods=['GET', 'POST'])
def assets_overview():
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from asset_overview")
    # fetching all records from database
    data = cursor.fetchall()

    # returning back to projectlist.html with all records from MySQL which are stored in variable data
    return render_template("assets_overview.html", data=data)


@app.route('/my_assets', methods=['GET', 'POST'])
def my_assets():
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # collecting all the assets that the user has
    if session.get('loggedin') == True:
        cursor.execute("select * from asset_overview where %s = user_id", (session['email'],))
        asset_data = cursor.fetchall()
    else:
        render_template('login.html')
        return redirect(url_for('login'))

    if request.method == 'POST':  # check to see if all data is filled in
        if request.form['action'] == 'submit':  # check whether post is coming from insert
            try:
                # create unique id for the asset
                UserId = session['email']
                AssetId = uuid.uuid1()
                AssetName = request.form['AssetName']
                AssetType = request.form['AssetType']
                Maintanencestate = request.form['maintainancestate']
                BuildYear = str(request.form['Builddate'])
                DestructionYear = str(request.form['Destructiondate'])
                Maintainer = request.form['Maintainer']
                Owner = session['companyname']
                Width = request.form['Width']
                Length = request.form['Length']
                Location = str(request.form['address'] + request.form['city'])
                ConstructionType = request.form['ConstructionType']
                Status = 'Existing'
                if Maintanencestate == '5. Poor':
                    Alert = 'Yes'
                else:
                    Alert = 'No'
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

                sql = "INSERT INTO asset_overview (Assetnumber, AssetName, AssetType, ConstructionType,	" \
                      "Maintainance_State,	Buildyear, " \
                      "Maintainer, Owner, Status, Width, Length, Area, Location, Passage_road_width, " \
                      "Passage_road_height, Passage_sail_width, Passage_sail_height, " \
                      "Technical_lifespan_expires, OBJECT_GUID, Area_1, Connection_Type, Neighborhood, City, RD_X, " \
                      "RD_Y, Length_1, Area_2, " \
                      "circumference, user_id, Alert) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, " \
                      "NULL, %s, NULL, NULL, NULL, " \
                      "NULL, %s, NULL, NULL, NULL, NULL, %s, NULL, NULL, NULL, NULL, NULL, %s, %s)"
                val = (
                    AssetId, AssetName, AssetType, ConstructionType, Maintanencestate, BuildYear, Maintainer, Owner,
                    Status, Width, Length, Location, DestructionYear, UserId)

                print(val)
                cursor.execute(sql, val)
                mysql.connection.commit()
                print('Succesfull')
                msg = "Asset succesfully added"
                return redirect(url_for('my_assets'))
            except:
                msg = 'an error occurred'
                print('failed')

    # reindex the dataframe and get the right information
    cursor.execute("select * from asset_overview")
    categories = cursor.fetchall()
    asset_cat = pd.DataFrame(categories)
    dataset = asset_cat.reindex(columns=asset_cat.columns.tolist() + ['Open_Asset'])
    construction_type = dataset['ConstructionType'].unique()
    asset_type = dataset['AssetType'].unique()
    maintainance_type = dataset['Maintainance_State'].unique()

    return render_template("my_assets.html",
                           asset_data=asset_data,
                           construction_type=construction_type,
                           asset_type=asset_type,
                           maintainance_type=maintainance_type)


@app.route('/add_component', methods=['GET', 'POST'])
def add_component():
    msg = ''
    # check to see if user is logged in otherwise, redirect user to the login page
    if session.get('loggedin') == True:
        msg = 'add a component'
    else:
        msg = 'You need to be logged in to add components'
        render_template('login.html')
        return redirect(url_for('login'))

    record_id = ''

    if request.method == 'GET':
        record_id = request.args.get("record_id")

    if request.method == 'POST':  # check to see if all data is filled in
        if request.form['asset_id'] == 'None':
            record_id = None
            Status = 'Published'
        else:
            record_id = request.form['asset_id']
            Status = 'Not Published'

        ComponentID = uuid.uuid1()
        ComponentMaterial = request.form['ComponentMaterial']
        Category = request.form['Category']
        Weight = request.form['ComponentWeight']
        Condition = request.form['ComponentCondition']
        Availability = request.form['Availability']
        Owner = session['companyname']
        Owner_email = session['email']
        AvailabilityDate = request.form['AvailabilityDate']
        Location = request.form['Location']
        Price = request.form['Price']
        Description = request.form['comment']
        AssetId = record_id

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
        if AssetId is None:
            sql = "INSERT INTO components (component_id, asset_id, material, category, weight, component_condition, " \
                  "availability, availability_date, component_owner, owner_email, " \
                  "location, price, component_description, status) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (
                ComponentID, ComponentMaterial, Category, Weight, Condition, Availability, AvailabilityDate, Owner,
                Owner_email, Location, Price, Description, Status)

        else:
            sql = "INSERT INTO components (component_id, asset_id, material, category, weight, component_condition, availability, " \
                  "availability_date, component_owner, owner_email, " \
                  "location, price, component_description, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (
                ComponentID, AssetId, ComponentMaterial, Category, Weight, Condition, Availability, AvailabilityDate,
                Owner, Owner_email, Location, Price, Description, Status)

        cursor.execute(sql, val)
        mysql.connection.commit()

        print('Succesfull')
        flash("Component succesfully added")
        if AssetId is None:
            return redirect(url_for('marketplace'))
        else:
            return redirect(url_for('asset_components', record_id=AssetId, user_id=Owner_email))

    return render_template("add_component.html", title="Add Component", asset_id=record_id)


@app.route('/asset-components', methods=['GET', 'POST'])
def asset_components():
    # table
    record_id = request.args.get("record_id")

    # Fetch bridge specific data
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    record_id = str(record_id)
    cursor.execute("select * from asset_overview WHERE Assetnumber= %s", [record_id])
    bridge_dataset = cursor.fetchall()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from components where asset_id = %s", [record_id])
    components_dataset = cursor.fetchall()

    # update alert state of asset if 80% of components are in poor state
    calculate_percentage_poor_components(components_dataset, record_id)
    # requery the database if the data was changed
    cursor.execute("select * from asset_overview WHERE Assetnumber= %s", [record_id])
    bridge_dataset = cursor.fetchall()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from components where asset_id = %s", [record_id])
    components_dataset = cursor.fetchall()


    cursor.execute("select * from asset_overview")
    categories = cursor.fetchall()
    asset_cat = pd.DataFrame(categories)
    dataset = asset_cat.reindex(columns=asset_cat.columns.tolist() + ['Open_Asset'])
    construction_type = dataset['ConstructionType'].unique()
    asset_type = dataset['AssetType'].unique()
    maintainance_type = dataset['Maintainance_State'].unique()

    if request.method == 'POST':  # check to see if all data is filled in
        if request.form['action'] == 'submit':  # check whether post is coming from insert
            try:
                # create unique id for the asset
                UserId = session['email']
                AssetId = record_id
                AssetName = request.form['AssetName']
                AssetType = request.form['AssetType']
                Maintanencestate = request.form['maintainancestate']
                BuildYear = request.form['Builddate']
                DestructionYear = request.form['Destructiondate']
                Maintainer = request.form['Maintainer']
                Owner = session['companyname']
                Width = request.form['Width']
                Length = request.form['Length']
                Location = str(request.form['address'] + request.form['city'])
                ConstructionType = request.form['ConstructionType']
                Status = 'Existing'

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

                sql = "UPDATE asset_overview SET Assetnumber = %s, AssetName = %s, AssetType = %s, ConstructionType = %s,	" \
                      "Maintainance_State = %s,	Buildyear = %s, " \
                      "Maintainer = %s, Owner = %s, Status = %s, Width = %s, Length = %s, Area = NULL, Location = %s, Passage_road_width = NULL, " \
                      "Passage_road_height = NULL, Passage_sail_width = NULL, Passage_sail_height = NULL, " \
                      "Technical_lifespan_expires = %s, OBJECT_GUID = NULL, Area_1 = NULL, Connection_Type = NULL, Neighborhood = NULL, City = NULL, RD_X = NULL, " \
                      "RD_Y = NULL, Length_1 = NULL, Area_2 = NULL, " \
                      "circumference = NULL, user_id = %s WHERE Assetnumber = %s"
                val = (
                    AssetId, AssetName, AssetType, ConstructionType, Maintanencestate, BuildYear, Maintainer, Owner,
                    Status, Width, Length, Location, DestructionYear, UserId, AssetId)

                cursor.execute(sql, val)
                mysql.connection.commit()
                print('Succesfull')
                msg = "Asset succesfully added"
                return redirect(url_for('asset_components', record_id=AssetId))
            except:
                msg = 'an error occurred'
                print('failed')

    return render_template("asset_components.html", bridge_dataset=bridge_dataset,
                           components_dataset=components_dataset,
                           title="Asset Components",
                           record_id=record_id,
                           construction_type=construction_type,
                           asset_type=asset_type,
                           maintainance_type=maintainance_type)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        try:
            kvknumber = request.form['kvknumber']
            phonenumber = request.form['phone']
            password = request.form['password']
            email = request.form['email']
            companyname = request.form['companyname']
            location = str(request.form['address'] + request.form['city'])

            # connect to database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists !'
            else:

                cursor.execute('INSERT INTO accounts VALUES (% s, % s, % s, % s, % s, % s, NULL, NULL, NULL)',
                               (kvknumber, phonenumber, password, email, companyname, location))

                mysql.connection.commit()

                msg = 'You have successfully registered !'
                render_template('login.html')
                return redirect(url_for('login'))
        except:
            msg = 'Failed to register, please try again later'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = % s AND password = % s', (email, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['email'] = account['email']
            session['companyname'] = account['companyname']
            msg = 'Logged in successfully !'
            render_template('navpage.html', msg=msg)
            return redirect(url_for('navpage'))
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('companyname', None)
    return redirect(url_for('login'))


@app.route('/project-overview', methods=['GET', 'POST'])
def project_overview():  # Provide forms for input
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # collecting all the projects that the user has
    if session.get('loggedin') == True:

        cursor.execute("select * from projects where %s = user_id", (session['email'],))
        project_data = cursor.fetchall()
    else:
        render_template('login.html')
        return redirect(url_for('login'))

    if request.method == 'POST':  # check to see if all data is filled in
        if request.form['action'] == 'submit':  # check whether post is coming from insert
            try:
                # create unique id for the asset
                UserId = session['email']
                ProjectId = uuid.uuid1()
                AssetName = request.form['AssetName']
                AssetType = request.form['AssetType']
                StartDate = request.form['start_date']
                EndDate = request.form['end_date']
                Maintainer = request.form['Maintainer']
                Owner = session['companyname']
                Width = request.form['Width']
                Length = request.form['Length']
                Location = str(request.form['address'] + request.form['city'])
                ConstructionType = request.form['ConstructionType']

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

                sql = "INSERT INTO projects (user_id, project_id, assetname, assettype, startdate, enddate, maintainer, owner, width, length, location, constructiontype) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (
                    UserId, ProjectId, AssetName, AssetType, StartDate, EndDate, Maintainer, Owner, Width, Length,
                    Location,
                    ConstructionType)

                cursor.execute(sql, val)
                mysql.connection.commit()

                print('Succesfull')
                msg = "Project succesfully added"
                return redirect(url_for('project_overview'))
            except:
                msg = 'an error occurred'


        elif request.form['action'] == 'Show Details':  # check whether post is coming from 'show details'
            return render_template("project_components.html")

    # Get possible construction and asset types from Asset database and convert it to a dataframe
    cursor.execute("select * from asset_overview")
    asset_data = pd.DataFrame(cursor.fetchall())

    # reindex the dataframe and get the right information
    dataset = asset_data.reindex(columns=asset_data.columns.tolist() + ['Open_Asset'])
    construction_type = dataset['ConstructionType'].unique()
    asset_type = dataset['AssetType'].unique()

    return render_template("project_overview.html",
                           projects_df=project_data,
                           construction_type=construction_type,
                           asset_type=asset_type)


## IMPORT image
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)


class MyForm(FlaskForm):
    image = FileField('image')


# Upload Image
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        asset_id = request.args.get('record_id')
        file = request.files['file']
        bridgeimgname = 'asset_id=' + str(asset_id) + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], bridgeimgname))
        flash("Success! Profile photo uploaded successfully.", 'success')
        return redirect(url_for("asset_components", record_id=asset_id))
    return render_template("upload.html")


@app.route('/project_components', methods=['GET', 'POST'])
def project_components():
    project_id = str(request.args.get('project_id'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    project_id = str(project_id)
    cursor.execute("select DISTINCT * from project_components WHERE ProjectId= %s", [project_id])
    data = cursor.fetchall()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from projects WHERE project_id= %s", [project_id])
    project_data = cursor.fetchall()

    cursor.execute("select * from asset_overview")
    categories = cursor.fetchall()
    asset_cat = pd.DataFrame(categories)
    dataset = asset_cat.reindex(columns=asset_cat.columns.tolist() + ['Open_Asset'])
    construction_type = dataset['ConstructionType'].unique()
    asset_type = dataset['AssetType'].unique()
    maintainance_type = dataset['Maintainance_State'].unique()

    if request.method == 'POST':  # check to see if all data is filled in
        if request.form['action'] == 'submit':  # check whether post is coming from insert
            try:
                # create unique id for the asset
                UserId = session['email']
                ProjectId = str(request.args.get('project_id'))
                AssetName = request.form['AssetName']
                AssetType = request.form['AssetType']
                StartDate = request.form['start_date']
                EndDate = request.form['end_date']
                Maintainer = request.form['Maintainer']
                Owner = session['companyname']
                Width = request.form['Width']
                Length = request.form['Length']
                Location = str(request.form['address'] + request.form['city'])
                ConstructionType = request.form['ConstructionType']

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

                sql = "UPDATE projects SET user_id = %s, project_id = %s, assetname = %s, assettype = %s, " \
                      "startdate = %s, enddate = %s, maintainer = %s, owner = %s, width = %s, length = %s, " \
                      "location = %s, constructiontype = %s WHERE project_id = %s"
                val = (
                    UserId, ProjectId, AssetName, AssetType, StartDate, EndDate, Maintainer, Owner, Width, Length,
                    Location,
                    ConstructionType, ProjectId)

                cursor.execute(sql, val)
                mysql.connection.commit()
                print('Succesfull')
                msg = "Project succesfully added"
                return redirect(url_for('project_components', project_id=ProjectId))
            except:
                msg = 'an error occurred'

    return render_template("project_components.html",
                           data=data,
                           title="Project Components",
                           project_id=project_id,
                           project_data=project_data,
                           construction_type=construction_type,
                           asset_type=asset_type,
                           maintainance_type=maintainance_type)


# Upload Data
UPLOAD_FOLDER_DATA = './data/uploads'
app.config['UPLOAD_FOLDER_DATA'] = UPLOAD_FOLDER_DATA
UPLOAD_DATA_FILENAME = "Asset_source_data.xlsx"
app.config['UPLOAD_DATA_FILENAME'] = UPLOAD_DATA_FILENAME
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/upload_data', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST' and 'data_file' in request.files:
        # uploading the file
        file = request.files['data_file']
        location = os.path.join(app.config['UPLOAD_FOLDER_DATA'], app.config['UPLOAD_DATA_FILENAME'])
        file.save(location)
        flash("Success! File is uploaded", 'success')

        # populating the table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                               .format(user=app.config['MYSQL_USER'],
                                       pw=app.config['MYSQL_PASSWORD'],
                                       db=app.config['MYSQL_DB']))

        assets_dataset = pd.read_excel(location)
        assets_dataset.columns = [c.replace(' ', '_') for c in assets_dataset.columns]
        assets_dataset.columns = [c.replace('-', '_') for c in assets_dataset.columns]
        assets_dataset.columns = [c.replace('.', '_') for c in assets_dataset.columns]

        assets_dataset = assets_dataset.reindex(columns=assets_dataset.columns.tolist() + ['user_id'])
        assets_dataset = assets_dataset.reindex(columns=assets_dataset.columns.tolist() + ['alert'])

        assets_dataset['user_id'] = session['email']
        assets_dataset['alert'] = assets_dataset.apply(lambda row: label_alert(row), axis=1)
        if session['email'] != 'gemeente@almere.nl':
            assets_dataset['Assetnumber'] = [uuid.uuid1() for _ in range(len(assets_dataset.index))]

        assets_dataset.to_sql('asset_overview', engine, if_exists='append', index=False)
        return redirect(url_for('my_assets'))
    return render_template("upload_data.html")


@app.route('/delete_row', methods=['GET', 'POST'])
def delete_row():
    project_id = request.args.get("project_id")
    project_component_id = request.args.get("project_component_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("delete from project_components where ProjectComponentId= %s", [project_component_id])
    mysql.connection.commit()
    return redirect(url_for('project_components', project_id=project_id))


@app.route('/push_to_project', methods=['GET', 'POST'])
def push_to_project():
    # assign column
    ProjectId = request.form['project']
    component_id = request.args.get("component_id")
    ProjectComponentId = str(ProjectId + component_id)
    category = request.args.get("category")
    material = request.args.get("material")
    weight = request.args.get("weight")
    component_condition = request.args.get("component_condition")
    availability = request.args.get("availability")
    availability_date = request.args.get("availability_date")
    component_owner = request.args.get("component_owner")
    location = request.args.get("location")
    price = request.args.get("price")
    component_description = request.args.get("component_description")
    owner_email = request.args.get("owner_email")
    user_id = session['email']
    asset_id = request.args.get("asset_id")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

    sql = "INSERT INTO project_components (ProjectId, ProjectComponentId, component_id, category, material,	" \
          "weight,	component_condition, " \
          "availability, availability_date, component_owner, location, price, component_description, owner_email, " \
          " user_id, asset_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
          " %s, %s, %s, %s, %s , %s)"
    val = (ProjectId, ProjectComponentId, component_id, category, material,
           weight, component_condition,
           availability, availability_date, component_owner, location, price, component_description, owner_email,
           user_id, asset_id)

    print(val)
    cursor.execute(sql, val)
    mysql.connection.commit()
    return redirect(url_for('marketplace', project_id=ProjectId))


@app.route('/upload_project_foto', methods=['GET', 'POST'])
def upload_project_foto():
    if request.method == 'POST' and 'file' in request.files:
        project_id = request.args.get('project_id')
        file = request.files['file']
        bridgeimgname = 'project_id=' + str(project_id) + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], bridgeimgname))
        flash("Success! Profile photo uploaded successfully.", 'success')
        return redirect(url_for("project_components", project_id=project_id))
    return render_template("upload_project_foto.html")


@app.route('/upload_component_foto', methods=['GET', 'POST'])
def upload_component_foto():
    if request.method == 'POST' and 'file' in request.files:
        record_id = request.args.get('record_id')
        file = request.files['file']
        bridgeimgname = 'component_id=' + str(record_id) + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], bridgeimgname))
        flash("Success! Profile photo uploaded successfully.", 'success')
        return redirect(url_for("component_page", record_id=record_id))
    return render_template("upload_component_foto.html")


@app.route('/publish_to_marketplace', methods=['GET', 'POST'])
def remove_publish_to_marketplace():
    ComponentId = request.args.get("component_id")
    AssetId = request.args.get("record_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
    cursor.execute("SELECT status FROM components where component_id = %s ", [ComponentId])
    publish_status = cursor.fetchone().get('status')
    print(AssetId)
    if publish_status == 'Not Published':
        cursor.execute("UPDATE components set status = 'Published' where component_id = %s ", [ComponentId])
        user_id = session['email']
        mysql.connection.commit()
        print('succefull publishing')
        if AssetId != None:
            return redirect(url_for('asset_components', record_id=AssetId))
        else:
            return redirect(url_for('my_components'))
    if publish_status == 'Published':
        cursor.execute("UPDATE components set status = 'Not Published' where component_id = %s ", [ComponentId])
        user_id = session['email']
        mysql.connection.commit()
        print('succesfull deletion')
        if AssetId != None:
            return redirect(url_for('asset_components', record_id=AssetId))
        else:
            return redirect(url_for('my_components'))
    return redirect(url_for('my_components'))


@app.route('/asset_delete', methods=['GET', 'POST'])
def asset_delete():
    AssetId = request.args.get("asset_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
    cursor.execute("delete from asset_overview where Assetnumber = %s ", [AssetId])
    mysql.connection.commit()
    return redirect(url_for('my_assets'))


@app.route('/project_delete', methods=['GET', 'POST'])
def project_delete():
    ProjectId = request.args.get("project_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
    cursor.execute("delete from projects where project_id = %s ", [ProjectId])
    mysql.connection.commit()
    return redirect(url_for('project_overview'))


@app.route('/my_components', methods=['GET', 'POST'])
def my_components():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from components where %s = owner_email", (session['email'],))
    components_data = cursor.fetchall()

    if request.method == 'POST':  # check to see if all data is filled in
        try:
            Status = 'Not Published'
            ComponentID = uuid.uuid1()
            ComponentMaterial = request.form['ComponentMaterial']
            Category = request.form['Category']
            Weight = request.form['ComponentWeight']
            Condition = request.form['ComponentCondition']
            Availability = request.form['Availability']
            Owner = session['companyname']
            Owner_email = session['email']
            AvailabilityDate = request.form['AvailabilityDate']
            Location = request.form['Location']
            Price = request.form['Price']
            Description = request.form['comment']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

            sql = "INSERT INTO components (component_id, asset_id, material, category, weight, component_condition, " \
                  "availability, availability_date, component_owner, owner_email, " \
                  "location, price, component_description, status) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (
                ComponentID, ComponentMaterial, Category, Weight, Condition, Availability, AvailabilityDate, Owner,
                Owner_email, Location, Price, Description, Status)

            cursor.execute(sql, val)
            mysql.connection.commit()

            print('Succesfull')

            # collect the data again so the new component is added
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select * from components where %s = owner_email", (session['email'],))
            components_data = cursor.fetchall()

            return render_template('my_components.html', components_data=components_data)
        except:
            print('failed')

    return render_template('my_components.html', components_data=components_data)


@app.route('/component_delete', methods=['GET', 'POST'])
def component_delete():
    ComponentId = request.args.get("component_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
    cursor.execute("select asset_id from components where component_id = %s", [ComponentId])
    AssetId = cursor.fetchall()[0]['asset_id']
    cursor.execute("delete from components where component_id = %s ", [ComponentId])
    mysql.connection.commit()

    if AssetId != None:
        cursor.execute("select * from components where asset_id = %s", [AssetId])
        components_dataset = cursor.fetchall()
        if components_dataset:
            calculate_percentage_poor_components(components_dataset=components_dataset, record_id=AssetId)


    return redirect(url_for('my_components'))


@app.route('/remove_from_asset', methods=['GET', 'POST'])
def remove_from_asset():
    ComponentId = request.args.get("component_id")
    AssetId = request.args.get("record_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection
    cursor.execute("UPDATE components set asset_id = NULL where component_id = %s ", [ComponentId])
    mysql.connection.commit()
    cursor.execute("select * from components where asset_id = %s", [AssetId])
    components_dataset = cursor.fetchall()
    calculate_percentage_poor_components(components_dataset=components_dataset, record_id=AssetId)
    return redirect(url_for('asset_components', record_id=AssetId))



def roundup(x,y):
    return int(math.ceil(x / y)) * y

# Upload Components Data
UPLOAD_COMP_DATA_FILENAME = "Components_dummy_data.xlsx"
app.config['UPLOAD_COMP_DATA_FILENAME'] = UPLOAD_COMP_DATA_FILENAME
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/upload_components_data', methods=['GET', 'POST'])
def upload_components_data():
    if request.method == 'POST' and 'data_file' in request.files:
        # uploading the file
        file = request.files['data_file']
        location = os.path.join(app.config['UPLOAD_FOLDER_DATA'], app.config['UPLOAD_COMP_DATA_FILENAME'])
        file.save(location)
        flash("Success! File is uploaded", 'success')

        # populating the table
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                               .format(user=app.config['MYSQL_USER'],
                                       pw=app.config['MYSQL_PASSWORD'],
                                       db=app.config['MYSQL_DB']))

        # read excel + multiply data * 5 to populate the dataframe
        comp_dummy_dataset = pd.read_excel(location)
        df2 = comp_dummy_dataset.copy()
        df3 = comp_dummy_dataset.copy()
        df4 = comp_dummy_dataset.copy()
        df5 = comp_dummy_dataset.copy()
        comp_dummy_dataset = comp_dummy_dataset.append([df2, df3, df4, df5], ignore_index=True)

        comp_dummy_dataset = comp_dummy_dataset.reindex(columns=comp_dummy_dataset.columns.tolist()
                                                            + ['component_id'] + ['asset_id']
                                                            + ['status'] + ['availability'] + ['availability_date']
                                                            + ['component_owner'] + ['owner_email'] + ['location'])

        comp_dummy_dataset['component_id'] = [uuid.uuid1() for _ in range(len(comp_dummy_dataset.index))]
        comp_dummy_dataset['status'] = 'Not Published'
        comp_dummy_dataset['availability'] = 'In Asset'
        comp_dummy_dataset['owner_email'] = session['email']

        # adding random weight and price (optional)
        comp_dummy_dataset['weight'] = [roundup(rand.randint(100, 9999), 100) for _ in range(len(comp_dummy_dataset.index))]
        comp_dummy_dataset['price'] = [roundup(rand.randint(10, 999), 10) for _ in range(len(comp_dummy_dataset.index))]

        # assign randomly to assets
        query = 'select Assetnumber from asset_overview where user_id=%s'
        assets_dataset = pd.read_sql(query, con=engine, params=(session['email'],))
        assets_dataset = assets_dataset.head(25)    # take only first 25 rows for assets

        # randomly assign asset number
        for i, row in comp_dummy_dataset.iterrows():
            # one way to randomize
            # sample_asset = assets_dataset.sample()
            # comp_dummy_dataset.at[i, 'asset_id'] = sample_asset.iat[0, 0]

            # another way to randomize
            chosen_idx = rand.randint(0, 24)
            sample_asset = assets_dataset.iloc[chosen_idx]
            # update the asset_id
            comp_dummy_dataset.at[i, 'asset_id'] = sample_asset[0]

        # populate the components table
        comp_dummy_dataset.to_sql('components', engine, if_exists='append', index=False)
        return redirect(url_for('my_components'))
    return render_template("upload_comp_data.html")


def label_alert (row):
    if row['Maintainance_State'] == '5. Poor':
        return 'Yes'
    return 'No'

def calculate_percentage_poor_components(components_dataset, record_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    overall_weight = 0
    weight_poor = 0
    if components_dataset:
        for i in components_dataset:
            overall_weight = overall_weight + float(i['weight'])
            if i['component_condition'] == '5. Poor':
                weight_poor = weight_poor + float(i['weight'])
        percentage_poor = weight_poor/overall_weight*100
        if percentage_poor >= 80:
            cursor.execute("update asset_overview set alert = 'Yes' where  Assetnumber = %s", [record_id])
        else:
            cursor.execute("update asset_overview set alert = 'No' where  Assetnumber = %s", [record_id])
        mysql.connection.commit()


# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
