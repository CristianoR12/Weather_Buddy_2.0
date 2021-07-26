from flask import Flask, render_template, redirect, request, jsonify
from flask_bootstrap import Bootstrap
import mysql.connector
import requests
import json

app = Flask(__name__)

bootstrap = Bootstrap(app)

#Database implementation
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Psw_123456#!",
  database="weather",
  auth_plugin='mysql_native_password'
  
)

#Database table management => Checks if there is a preexistent table  
db = mydb.cursor()
db.execute("DROP TABLE IF EXISTS forecast")
db.execute("CREATE TABLE forecast (id INT AUTO_INCREMENT PRIMARY KEY, city TEXT NOT NULL, temperature TEXT NOT NULL, description TEXT NOT NULL)") 

#Index route
@app.route('/')
def index():
    return render_template("home.html")

#Route to manage the data received from user e.g., city name
@app.route('/register', methods=['GET'])
def register():
    c_name = request.args.get("c_name")
    city_name=str(c_name)  
    
    #Get the JSON from API
    req = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city_name+'&appid=9564059a8dcacce6e2ac0bcf2a543290&units=metric')
    data = json.loads(req.content) 

    #City name not recognized
    if data.get('cod') != 200:
        return render_template("error.html", message="Sorry. We couldn't find the specified city.")
   
    #JSON data filtering
    city=data['name']
    temperature=int(data['main']['temp'])
    description=data['weather'][0]['description']

    #Data picked from JSON sent to the database
    sql = "INSERT INTO forecast (city, temperature, description) VALUES (%s, %s, %s)"
    val = (city, temperature, description)
    db.execute(sql,val)
    mydb.commit()
    
    return redirect('/req')   

#Route to manage the data from database to be exhibited
@app.route('/req', methods=['GET'])
def test():    

    db.execute("SELECT * FROM forecast WHERE id = 1")
    myList = [dict(id0=row1[0],city0=row1[1],temperature0=row1[2], description0=row1[3]) for row1 in db.fetchall()]
    
    db.execute("SELECT * FROM forecast WHERE id = 2")
    myList2 = [dict(id1=row2[0],city1=row2[1],temperature1=row2[2], description1=row2[3]) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 3")
    myList3 = [dict(id2=row2[0],city2=row2[1],temperature2=row2[2], description2=row2[3]) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 4")
    myList4 = [dict(id3=row2[0],city3=row2[1],temperature3=row2[2], description3=row2[3]) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 5")
    myList5 = [dict(id4=row2[0],city4=row2[1],temperature4=row2[2], description4=row2[3]) for row2 in db.fetchall()]
    
    if not (myList2):
        myList2 = [
        {   
            'id1': 0, 
            'city1': '', 
            'temperature1': '', 
            'description1': ''
        }
        ]    
    if not (myList3):
        myList3 = [
        {   
            'id2': 0, 
            'city2': '', 
            'temperature2': '', 
            'description2': ''
        }
        ]
    if not (myList4):
        myList4 = [
        {   
            'id3': 0, 
            'city3': '', 
            'temperature3': '', 
            'description3': ''
        }
        ]
    if not (myList5):
        myList5 = [
        {   
            'id4': 0, 
            'city4': '', 
            'temperature4': '', 
            'description4': ''
        }
        ]

    myList_Total =  myList + myList2 + myList3 + myList4 + myList5 
    print(myList_Total)
    
    return render_template("req.html", arguments=myList_Total)

#Route to get the cache data for the specified city_name
@app.route("/weather/<city_name>", methods=['GET'])
def get_city_name(city_name):
    c_name=str(city_name)        
    db.execute(f"SELECT * FROM forecast WHERE city = '{city_name}'")    
    info = db.fetchall()
    test=info           
    
    #If the city is not yet registered in the database, retrieve data from the API      
    if not test:  
        req = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+c_name+'&appid=9564059a8dcacce6e2ac0bcf2a543290&units=metric')
        data = json.loads(req.content)

        info = {
            "city":str(data['name']),
            "temperature":str(data['main']['temp']),
            "description":str(data['weather'][0]['description']), 
        }

    return jsonify({'result (Obs.: If there is just one result, it is because the database has no record of the requested city, and the information displayed comes from the API': info })
    
#Route to get all the cached cities, up to the latest 'n' entries or max_number 
@app.route("/weather", methods=['GET'])
def max_number():
    max_number = int(request.args.get("max"))       
    db.execute(f"SELECT * FROM forecast WHERE id <= {max_number}")
    info = db.fetchall()

    return jsonify({'result': info })

