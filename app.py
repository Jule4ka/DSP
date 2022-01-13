from flask import Flask, render_template, request, url_for, flash, redirect, session, Response
import pandas as pd
from flask_navigation import Navigation
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_navigation.item import Item
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField
import os
import uuid

app = Flask(__name__, static_url_path='')
nav = Navigation(app)

# code for connection
# MySQL Hostname
app.config['MYSQL_HOST'] = 'localhost'
# MySQL username
app.config['MYSQL_USER'] = 'root'
# MySQL password here in my case password is null so i left empty
app.config['MYSQL_PASSWORD'] = 'DSPB1'
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
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from components")
    # fetching all records from database
    data = cursor.fetchall()
    if request.method == "POST":
        if request.form['action'] == 'Delete All Selected': #check whether form comes from delete
            msg = ''
            for getid in request.form.getlist('mycheckbox'):
                cursor.execute("delete from components where component_id= %s", [getid])
                mysql.connection.commit()
                cursor.execute("select * from components")
                data = cursor.fetchall()
                msg = 'Successfully deleted'
            if (not msg): msg = "There is nothing to delete"
            return render_template("marketplace.html", msg=msg, data=data)

    # returning back to projectlist.html with all records from MySQL which are stored in variable data
    return render_template("marketplace.html", data=data)


@app.route('/component_page.html', methods=['GET', 'POST'])
def component_page():
    record_id = request.args.get("record_id")

    # Fetch component specific data
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from components WHERE component_id=%s", [record_id])
    component_data = cursor.fetchall()

    # Fetch user data
    cursor.execute("select * from accounts WHERE email=(select owner_email from components WHERE component_id=%s)", [record_id])
    user_data = cursor.fetchall()

    # Fetch similar components
    cursor.execute("select * from components where category=%s and component_id<>%s", [component_data[0]['category'], record_id])
    similar_components_data = cursor.fetchall()
    return render_template("component_page.html",   component_data=component_data,
                                                    similar_components_data=similar_components_data,
                                                    user_data=user_data)


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
                BuildYear = request.form['Builddate']
                DestructionYear = request.form['Destructiondate']
                Maintainer = request.form['Maintainer']
                Owner = session['companyname']
                Width = request.form['Width']
                Length = request.form['Length']
                Location = str(request.form['address'] + request.form['city'])
                ConstructionType = request.form['ConstructionType']

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # creating variable for connection

                sql = "INSERT INTO asset_overview (Assetnumber, AssetName, AssetType, ConstructionType,	Maintainance_State,	Buildyear, Maintainer, Owner, Status, Width, Length, Area, Location, Passage_road-width, Passage_road-height, Passage_sail-width, Passage_sail-height, Technical_lifespan_expires, OBJECT_GUID, Area_1, Connection_Type, Neighborhood, City, RD-X, RD-Y, Length_1, Area_2, circumference, user_id, Destructionyear) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, NULL, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %s, %s)"
                val = (AssetId,	AssetName,	AssetType,	ConstructionType,	Maintanencestate,	BuildYear,	Maintainer,	Owner,	Width,	Length,	Location, UserId,	DestructionYear)

                print(val)
                cursor.execute(sql, val)
                mysql.connection.commit()

                print('Succesfull')
                msg = "Asset succesfully added"
                return redirect(url_for('my_assets'))
            except:
                msg = 'an error occurred'
                print('failed')

        if request.form['action'] == 'Delete All Selected':  # check whether post is coming from delete
            msg = ''
            for getid in request.form.getlist('mycheckbox'):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("delete from asset_overview where assetid = %s", [getid])
                mysql.connection.commit()
                cursor.execute("select * from asset_overview where %s = userid", (session['email'],))
                asset_data = cursor.fetchall()
                msg = 'Successfully deleted'
            if (not msg): msg = "There is nothing to delete"
            return render_template("my_assets.html", msg=msg, asset_df=asset_data)
        elif request.form['action'] == 'Show Details':  # check whether post is coming from 'show details'
            return render_template("component_page.html")


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
    if request.method == 'POST':  # check to see if all data is filled in
        try:
            # create unique id for the asset
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

            sql = "INSERT INTO components (component_id, material, category, weight, component_condition, availability, availability_date, component_owner, owner_email, " \
                  "location, price, component_description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (ComponentID, ComponentMaterial, Category, Weight, Condition, Availability, AvailabilityDate, Owner, Owner_email, Location, Price,Description)

            cursor.execute(sql, val)
            mysql.connection.commit()

            print('Succesfull')
            flash("Project succesfully added")
            return (redirect(url_for('marketplace.html')))
        except:
            flash('an error occured')

    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from components")
    return render_template("add_component.html", title="Add Component")


@app.route('/asset-components', methods=['GET', 'POST'])
def asset_components():
    # table
    if request.method == 'POST':
        record_id = int(request.form['asset_id'])
        components_dataset = pd.read_excel("data/Gemeente Almere bruggen components dummy.xlsx")
        components_dataset = components_dataset.loc[components_dataset['Assetnumber'] == record_id]

        # Fetch bridge specific data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        record_id = str(record_id)
        cursor.execute("select * from asset_overview WHERE Assetnumber= %s", [record_id])
        bridge_dataset = cursor.fetchall()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from dummy_data_marketplace")
        data = cursor.fetchall()

        return render_template("asset_components.html", column_names=components_dataset.columns.values,
                               row_data=list(components_dataset.values.tolist()), bridge_dataset=bridge_dataset,
                               zip=zip, title="Asset Components",
                               # , user_image=img1, form=form
                               record_id=record_id)


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
                UserId, ProjectId, AssetName, AssetType, StartDate, EndDate, Maintainer, Owner, Width, Length, Location,
                ConstructionType)

                cursor.execute(sql, val)
                mysql.connection.commit()

                print('Succesfull')
                msg = "Project succesfully added"
                return redirect(url_for('project_overview'))
            except:
                msg = 'an error occurred'

        elif request.form['action'] == 'Delete All Selected':  # check whether post is coming from delete
            msg = ''
            for getid in request.form.getlist('mycheckbox'):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("delete from projects where project_id= %s", [getid])
                mysql.connection.commit()
                cursor.execute("select * from projects where %s = user_id", (session['email'],))
                project_data = cursor.fetchall()
                msg = 'Successfully deleted'
            if (not msg): msg = "There is nothing to delete"

            return render_template("project_overview.html", msg=msg, projects_df=project_data)
        elif request.form['action'] == 'Show Details':  #check whether post is coming from 'show details'
            return render_template("component_page.html")

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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],bridgeimgname))
        flash("Success! Profile photo uploaded successfully.", 'success')
    return render_template("upload.html")

# run the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
