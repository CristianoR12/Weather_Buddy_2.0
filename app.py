from flask import Flask, render_template, redirect, request, jsonify
from flask_caching import Cache
from flask_bootstrap import Bootstrap
import mysql.connector
import requests
import json

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

bootstrap = Bootstrap(app)

#Database implementation
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Psw_123456#!",
  database="weather"
)

#Database implementation
#Database table management => Checks if there is a preexistent table  
db = mydb.cursor()
db.execute("DROP TABLE IF EXISTS forecast")
db.execute("CREATE TABLE forecast (id INT AUTO_INCREMENT PRIMARY KEY, city TEXT NOT NULL, temperature TEXT NOT NULL, description TEXT NOT NULL, icon TEXT NOT NULL)") 

#Index route
@app.route('/')
def index():
    return render_template("home.html")

#Route to manage the data received from user e.g., city name
@app.route('/register', methods=['GET'])
def register():
    c_name = request.args.get("c_name")
    city_name=str(c_name)  
    API_KEY = '9564059a8dcacce6e2ac0bcf2a543290'
    
    #Get the JSON from API
    req = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city_name+'&appid='+API_KEY+'&units=metric')
    data = json.loads(req.content) 

    #City name not recognized
    if data.get('cod') != 200:
        return render_template("error.html", message="Sorry. We couldn't find the specified city.")
   
    #JSON data filtering
    city=data['name']
    temperature=int(data['main']['temp'])
    description=data['weather'][0]['description']
    icon=data['weather'][0]['icon']

    #Data picked from JSON sent to the database
    sql = "INSERT INTO forecast (city, temperature, description, icon) VALUES (%s, %s, %s, %s)"
    val = (city, temperature, description, icon)
    db.execute(sql,val)
    mydb.commit()
    
    return redirect('/req')   

#Route to manage the data from database to be exhibited
@app.route('/req', methods=['GET'])
def test():    

    db.execute("SELECT * FROM forecast WHERE id = 1")
    myList = [dict(id0=row1[0],city0=row1[1],temperature0=row1[2], description0=row1[3], icon0=row1[4]) for row1 in db.fetchall()]
    
    db.execute("SELECT * FROM forecast WHERE id = 2")
    myList2 = [dict(id1=row2[0],city1=row2[1],temperature1=row2[2], description1=row2[3], icon1=row2[4]) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 3")
    myList3 = [dict(id2=row2[0],city2=row2[1],temperature2=row2[2], description2=row2[3], icon2=row2[4]) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 4")
    myList4 = [dict(id3=row2[0],city3=row2[1],temperature3=row2[2], description3=row2[3], icon3=row2[4] ) for row2 in db.fetchall()]

    db.execute("SELECT * FROM forecast WHERE id = 5")
    myList5 = [dict(id4=row2[0],city4=row2[1],temperature4=row2[2], description4=row2[3], icon4=row2[4]) for row2 in db.fetchall()]
    
    if not (myList2):
        myList2 = [
        {   
            'id1': 0, 
            'city1': '', 
            'temperature1': '', 
            'description1': '',
            'icon1': ''
        }
        ]    
    if not (myList3):
        myList3 = [
        {   
            'id2': 0, 
            'city2': '', 
            'temperature2': '', 
            'description2': '',
            'icon2': ''
        }
        ]
    if not (myList4):
        myList4 = [
        {   
            'id3': 0, 
            'city3': '', 
            'temperature3': '', 
            'description3': '',
            'icon3': ''
        }
        ]
    if not (myList5):
        myList5 = [
        {   
            'id4': 0, 
            'city4': '', 
            'temperature4': '', 
            'description4': '',
            'icon4': ''
        }
        ]
    myList_Total =  myList + myList2 + myList3 + myList4 + myList5 
    print(myList_Total)
   
    return render_template("req.html", arguments=myList_Total)

#Route to get the cache data for the specified city_name
@app.route("/weather/<city_name>", methods=['GET'])
@cache.cached(timeout=300)#cache must live for 300s or 5min
def get_city_name(city_name):
    c_name=str(city_name)    
    API_KEY = '9564059a8dcacce6e2ac0bcf2a543290'    
    db.execute(f"SELECT * FROM forecast WHERE city = '{city_name}'")    
    info = db.fetchall()
    test=info           
    
    #If the city is not yet registered in the database, retrieve data from the API      
    if not test:  
        req = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+c_name+'&appid='+API_KEY+'&units=metric')
        data = json.loads(req.content)

        info = {
            "city":str(data['name']),
            "temperature":str(data['main']['temp']),
            "description":str(data['weather'][0]['description']), 
        }

    return jsonify({'result (Obs.: If there is just one result, it is because the database has no record of the requested city, and the information displayed comes from the API': info })
   
#Route to get all the cached cities, up to the latest 'n' entries or max_number 
@app.route("/weather", methods=['GET'])
@cache.cached(timeout=300)#cache must live for 300s or 5min
def max_number():
    max_number = int(request.args.get("max"))       
    db.execute(f"SELECT * FROM forecast WHERE id <= {max_number}")
    info = db.fetchall()

    return jsonify({'result': info })

