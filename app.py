from flask import Flask,session,redirect,url_for,render_template,request,flash,jsonify,make_response
import sqlite3
import datetime
from collections import Counter
import os
import base64
import csv

app = Flask(__name__)
app.secret_key = "secretKey"

UPLOAD_FOLDER = 'static/students'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def exactDate(lst):
    date_str = lst.split(' ', 1)[0]
    return datetime.datetime.strptime(date_str, '%Y/%m/%d')

@app.route("/getData", methods=['GET'])
def loadData_dashboard(flag = True):
    global eventsDate
    personalDetails = []
    email = session.get('email')
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM studentCredential WHERE mailID = (?);",(email,))
    temp = cursor.fetchone()
    personalDetails.append(temp[1]+" "+temp[2])
    personalDetails.append(temp[0])
    personalDetails.append(temp[3])
    personalDetails.append(temp[4])
    personalDetails.append(temp[5])
    personalDetails.append(temp[6])
    personalDetails.append(temp[10])
    personalDetails.append(temp[11])
    cursor.execute("SELECT eventDate FROM studentActivities WHERE email=(?);",(email,))
    result = Counter(sorted(cursor.fetchall()))
    dates = ','.join([str(item) for item in result.keys()])
    count = ','.join([str(item) for item in result.values()])
    cursor.execute("SELECT specificEvent,eventDate,eventName FROM studentActivities WHERE email=(?);",(email,))
    result = list(cursor.fetchall())
    result = list(map(list,result))
    for i in range(len(result)):
        result[i][0]+=(" : " + result[i][2])
    
    events = [str(item[0]) for item in result]
    eDate = [str(item[1]) for item in result]
    eventsDate1 = [item+" - "+key for key,item in list(zip(events,eDate))]
    eventsDate = eventsDate1
    eventsDate = sorted(eventsDate,key=exactDate,reverse=True)
    
    cursor.execute(f"SELECT image FROM studentCredential WHERE mailID LIKE '{email}%'")
    image_data = cursor.fetchone()[0]
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    connection.close()
    if flag:
        return jsonify({'dates':dates,'count':count,'eventsDate':eventsDate,'imageData':image_base64,'personalDetails':personalDetails})
    else:
        return eventsDate

@app.route('/')
def home():
    email = session.get('email')
    if email:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST','GET'])    
def login():
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        stmt = "SELECT mailID,password FROM studentCredential WHERE mailID=(?) AND password=(?);"
        cursor.execute(stmt,(email,password))
        if cursor.fetchone() != None:
            
            connection.close()
            session['email'] = email
            #dates, count, eventsDate, imageData = loadData_dashboard()
            return redirect(url_for('dashboard'))
        else:
            
            flash("Invalid credential",category="error")
            connection.close()
            return render_template('login.html')
    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        rollNumber = request.form['rollnumber']
        fname = request.form['fname']
        lname = request.form['lname']
        batch = request.form['batch']
        dept = request.form['dept']
        section = request.form['section']
        phoneNumber = request.form['phoneNumber']
        password = request.form['password']
        dob = request.form['dob']
        dob = dob.replace('-','/')
        address = request.form['address']
        
        flag = True
        if 'image' not in request.files:
            flash("Upload image",category="error")
            flag = False
        else:
            file = request.files['image']
            if file.filename == '':
                flash("No file selected", category="error")
                flag = False
                
            if file and allowed_file(file.filename):
                extension = file.filename.split('.')[-1]
                blob_data = file.read()
            else:
                flash("Invalid type",category="error")
                flag = False
        
        if flag == False:
            return redirect(url_for('register'))

        connection = sqlite3.connect("studentDB.db")
        cursor = connection.cursor()
        try:
            stmt = "INSERT INTO studentCredential VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);"
            cursor.execute(stmt,(rollNumber,fname,lname,email,batch,dept,section,phoneNumber,password,rollNumber+extension,blob_data,dob,address))
            connection.commit()
            session['email'] = email
            connection.close()
            return redirect(url_for('dashboard'))
        except Exception as e:
            
            flash("Error in adding record",category="error")
            return redirect(url_for('login'))
    return render_template('register.html',popUp=False)

@app.route("/dashboard")
def dashboard():
    email = session.get('email')
    if not email:
        return redirect(url_for('login'))
    
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT eventDate FROM studentActivities WHERE email=(?);",(email,))
    result = Counter(sorted(cursor.fetchall(),key=lambda x: x[0].split('/')[1]))
    dates = list(result.keys())
    count = list(result.values())
    eventsDate = loadData_dashboard(False)
    connection.close()
    return render_template('dashboard.html',labels=dates,values=count, eventsDate=eventsDate)

@app.route("/logout")
def logout():
    session.pop('email',None)
    flash("Logged out successfully",category="success")
    return redirect(url_for('login'))

@app.route("/upgrade")
def upgrade():
    if not session.get('email'):
        return redirect(url_for('login'))

    return render_template('upgradeProgree.html')

@app.route("/changePassword", methods=['GET','POST'])
def changePassword():
    if not session.get('email'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        currentPass = request.form['current_password']
        newPass = request.form['new_password']
        confirmNewPass = request.form['confirm_new_password']

        email = session.get('email')
        connection = sqlite3.connect("studentDB.db")
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM studentCredential WHERE mailID=(?)",(email,))
        password = cursor.fetchone()[0]
        
        if password != currentPass:
            flash("Invalid password",category="error")
        elif newPass != confirmNewPass:
            flash("Password does not matches",category="error")
        else:
            cursor.execute("UPDATE studentCredential SET password=(?) WHERE mailID=(?);",(email,newPass))
            connection.commit()
            flash("Password changed successfully",category="success")
            cursor.execute("SELECT eventDate FROM studentActivities WHERE email=(?);",(email,))
            result = Counter(sorted(cursor.fetchall(),key=lambda x: x[0].split('/')[1]))
            dates = list(result.keys())
            count = list(result.values())
            connection.close()
            _,_,eventsDate,imageData = loadData_dashboard()
            return render_template('dashboard.html',labels=dates,values=count,eventsDate=eventsDate,imageData=imageData)

    
    return render_template('changePassword.html')

@app.route('/editProfile')
def editProfile():
    if not session.get('email'):
        return redirect(url_for('login'))

    return render_template('editProfile.html')

@app.route('/searchData', methods=['GET','POST'])
def searchData():
    if not session.get('email'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        fromDate = request.form['fromDate']
        toDate = request.form['toDate']
        particulars = request.form['particulars']
        location = request.form['location']
        specificEvent = request.form['specificEvent']
        
        fromDate = fromDate.replace('-','/')
        
        toDate = toDate.replace('-','/')
        
        email = session.get('email')
        connection = sqlite3.connect("studentDB.db")
        cursor = connection.cursor()
        cursor.execute("SELECT eventDate,specificEvent,eventName,collegeName,location,price,additionalInfo,id FROM studentActivities WHERE email = (?) AND eventDate BETWEEN (?) AND (?);",(email,fromDate,toDate))
        result = cursor.fetchall()
        result = list(map(list,result))
        for i in range(len(result)):
            result[i][2] += (" ("+result[i][6]+")")
            del result[i][6]
        columns = ['date', 'eventSpec', 'eventName', 'location', 'venue', 'prize', 'id']
        formatted_data = [dict(zip(columns, row)) for row in result]
        connection.close()
    return jsonify({"details":formatted_data})

    
@app.route("/addRecords", methods=['GET','POST'])
def addRecords():
    if not session.get('email'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        specificEvent = request.form['specificEvent']
        eventName = request.form['eventName']
        eventDate = request.form['eventDate']
        eventDate = eventDate.replace("-",'/')
        location = request.form['location']
        collegeName = request.form['collegeName']
        prize = request.form['prize']
        cashPrize = request.form['cashPrize']
        additionalInfo = request.form['additional-info']
        
        flag = True
        if 'certificate' not in request.files:
            flash("Upload image",category="error")
            flag = False
        else:
            file = request.files['certificate']
            if file.filename == '':
                flash("No file selected", category="error")
                flag = False
                
            if file and allowed_file(file.filename):
                extension = file.filename.split('.')[-1]
                blob_data = file.read()
            else:
                flash("Invalid type",category="error")
                flag = False
        
        if flag == False:
            
            return redirect(url_for('addRecords'))
        
        connection = sqlite3.connect("studentDB.db")
        cursor = connection.cursor()
        try:
            email = session.get('email')
            cursor.execute("SELECT rollNumber FROM studentCredential WHERE mailID=(?);",(email,))
            rollNumber = cursor.fetchone()[0]
            
            stmt = "INSERT INTO studentActivities (email,specificEvent,eventName,eventDate,location,collegeName,price,cashPrize,additionalInfo,fileName,certificate) VALUES(?,?,?,?,?,?,?,?,?,?,?);"
            cursor.execute(stmt,(email,specificEvent,eventName,eventDate,location,collegeName,prize,cashPrize,additionalInfo,(rollNumber+"_"+eventName+"."+extension),blob_data))
            connection.commit()
            connection.close()
            
            return redirect(url_for('upgrade'))
        except Exception as e:
            
           
            flash("Error in adding record",category="error")
            return redirect(url_for('addRecords'))
        
        
        
        
    return render_template('addRecords.html')

@app.route('/downloadCertificate/<id>', methods=['GET','POST'])
def downloadCertificate(id):
    if not session.get('email'):
        return redirect(url_for('login'))
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    try:
        email = session.get('email')
        cursor.execute("SELECT certificate FROM studentActivities WHERE email=(?) AND id=(?);",(email,id))
        imageBlob = cursor.fetchone()
        
        cursor.execute("SELECT fileName FROM studentActivities WHERE email=(?) AND id=(?);",(email,id))
        extension = cursor.fetchone()[0]
        extension = extension.split('.')[-1]
        response = make_response(imageBlob[0])
        response.headers.set('Content-Type', f"image/{extension}")
        response.headers.set('Content-Disposition', 'attachment', filename=f"Certificate.{extension}")
        connection.close()
        return response
            
    except Exception as e:
        
        flash("Error in retrieving data from database")
        return redirect(url_for('upgrade'))

@app.route("/certificationCourse")
def certificationCourse():
    if not session.get('email'):
        return redirect(url_for('login'))
    return render_template('certificationCourses.html')

length = 0
csvData = None

@app.route('/searchCourses', methods=['POST'])
def search():
    global csvData
    if not session.get('email'):
        return redirect(url_for('login'))
    global length
    platform = request.form.get('platform')
    certificationType = request.form.get('certificationType')
    particulars = request.form.get('particulars')
    freePaid = request.form.get('freePaid')
    year = request.form.get('year')
    section = request.form.get('section')
    semester = request.form.get('semester')
    courseType = request.form.get('courseType')
    duration = request.form.get('duration')
    fromDate = request.form.get('fromDate')
    fromDate = fromDate.replace('-','/')
    toDate = request.form.get('toDate')
    toDate = toDate.replace('-','/')

   
    
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    stmt = "SELECT s1.name, s1.year, s1.platform, s1.courseType||' - '||s1.particulars, s1.duration, s1.id, s2.rollNumber FROM studentCertification s1 JOIN studentCredential s2 on s1.email = s2.mailID WHERE "
    
    lst = {
    'platform': platform,
    'certificationType': certificationType,
    'rollNumber': particulars,
    'freePaid': freePaid,
    'year': year,
    'section': section,
    'semester': semester,
    'courseType': courseType,
    'duration': duration,
    'fromDate': fromDate,
    'toDate': toDate
    }
    
    flag = False
    for i in lst:
        if(lst[i]!=None and lst[i]!=""):
            if(i=='freePaid' and lst[i]=='Both'):
                stmt+=("(freePaid = 'Free' OR freePaid = 'Paid') AND ")
                flag = True
            else:
                stmt+=(f"{i} = '{lst[i]}' AND ")
                flag = True   
    if flag == False:
        stmt = stmt.replace("WHERE","")
    if flag:
        stmt = stmt[:len(stmt)-4]
    cursor.execute(stmt)
    result = cursor.fetchall()
    csvData = result
    length = len(result)
    connection.close()
    return jsonify({'details':result})

@app.route('/certificateUpload', methods=['GET','POST'])
def certificateUpload():
    if not session.get('email'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        platform = request.form.get('platform')
        certificationType = request.form.get('certificationType')
        particulars = request.form.get('particulars')
        freePaid = request.form.get('freePaid')
        mode = request.form.get('mode')
        year = request.form.get('year')
        section = request.form.get('section')
        semester = request.form.get('semester')
        courseType = request.form.get('courseType')
        duration = request.form.get('duration')
        fromDate = request.form.get('fromDate')
        fromDate = fromDate.replace('-','/')
        toDate = request.form.get('toDate')
        toDate = toDate.replace('-','/')
        
        flag = True
        if 'certificate' not in request.files:
            flash("Upload image",category="error")
            flag = False
        else:
            file = request.files['certificate']
            if file.filename == '':
                flash("No file selected", category="error")
                flag = False
                
            if file and allowed_file(file.filename):
                extension = file.filename.split('.')[-1]
                blob_data = file.read()
            else:
                flash("Invalid type",category="error")
                flag = False
        
        if flag == False:
            
            return redirect(url_for('certificateUpload'))
        
        connection = sqlite3.connect("studentDB.db")
        cursor = connection.cursor()
        try:
            email = session.get('email')
            cursor.execute("SELECT firstName||' '||lastName as name FROM studentCredential WHERE mailID=(?);",(email,))
            name = cursor.fetchone()[0]
            
            cursor.execute("""INSERT INTO studentCertification (
        email, name, platform, certificationType, particulars, 
        freePaid, mode, year, section, semester, 
        courseType, duration, fromDate, toDate, fileName, certificate
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",(email,name,platform,certificationType,particulars,freePaid,mode,year,section,semester,courseType,duration,fromDate,toDate,(name+" "+certificationType+"."+extension),blob_data)) 
            connection.commit()
            connection.close()
            
            return redirect(url_for('certificationCourse'))
        except Exception as e:
            
            
            flash("Error in adding record",category="error")
            return redirect(url_for('certificateUpload'))
        
    
    return render_template('certificateUpload.html')


@app.route('/download/<id>', methods=['GET','POST'])
def download(id):
    if not session.get('email'):
        return redirect(url_for('login'))
    connection = sqlite3.connect("studentDB.db")
    cursor = connection.cursor()
    try:
        email = session.get('email')
        cursor.execute("SELECT certificate FROM studentCertification WHERE id=(?);",(id,))
        imageBlob = cursor.fetchone()
        
        cursor.execute("SELECT fileName FROM studentCertification WHERE id=(?);",(id,))
        extension = cursor.fetchone()[0]
        extension = extension.split('.')[-1]
        response = make_response(imageBlob[0])
        response.headers.set('Content-Type', f"image/{extension}")
        response.headers.set('Content-Disposition', 'attachment', filename=f"Certificate.{extension}")
        connection.close()
        return response
            
    except Exception as e:
        print(e)
        flash("Error in retrieving data from database")
        return redirect(url_for('certificationCourse'))
    
@app.route('/downloadExcel')
def downloadExcel():
    global csvData
    csvData = list(map(list,csvData))
    for i in range(len(csvData)):
        csvData[i] = csvData[i][len(csvData[i])-2:]+csvData[i][:len(csvData[i])-2]
    print(csvData)
    with open("certificationDetails.csv",'w') as fileObj:
        writer = csv.writer(fileObj)
        writer.writerows(csvData)
    return redirect(url_for("certificationCourse"))
    


@app.route('/getPaginationData', methods=['POST'])
def get_pagination_data():
    if not session.get('email'):
        return redirect(url_for('login'))
    current_page = 1
    items_per_page = 25
    total_items = length

    
    response_data = {
        'current_page': current_page,
        'items_per_page': items_per_page,
        'total_items': total_items
    }
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)