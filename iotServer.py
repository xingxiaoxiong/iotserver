from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
import time, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from database_setup import Base, Farm, Greenhouse, Node, Temperature, Humidity, Watering

# imports for generating session
from flask import session as login_session
import random, string

from watering import levelToTime, computeWateringStatus

import httplib2
import json
from flask import make_response
import requests

import arrow

app = Flask(__name__)

engine = create_engine('mysql+pymysql://root:worldofiot@localhost')
engine.execute("USE IoT")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

APPLICATION_NAME = "SensorCloud"

def JSONResponse(message, code):
    response = make_response(json.dumps(message, code))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/farms/')
def farms():
    farms = session.query(Farm).all()
    #print farms
    return render_template('farm/farms.html', farms = farms)
    
@app.route('/farm/<int:farm_id>/')
@app.route('/farm/<int:farm_id>/greenhouses/')
def greenhouses(farm_id):
    greenhouses = session.query(Greenhouse).filter_by(farm_id = farm_id).all()
    waterLevel = []
    waterTime = []
    waterStatus = []
    
    for greenhouse in greenhouses:
        try:
            if datetime.datetime.today().hour >= 18:
                record = session.query(Watering). \
                        filter(Watering.greenhouse_id == greenhouse.id). \
                        filter(Watering.date == datetime.date.today() - datetime.timedelta(days = 1)).first()
            else:
                record = session.query(Watering). \
                        filter(Watering.greenhouse_id == greenhouse.id). \
                        filter(Watering.date == datetime.date.today() - datetime.timedelta(days = 2)).first()
                        
            level = record.time
        except:
            level = "-"

        try:
            if datetime.datetime.today().hour >= 18:
                todayRecord = session.query(Watering). \
                        filter(Watering.greenhouse_id == greenhouse.id). \
                        filter(Watering.date == datetime.date.today()).first()
            else:
                todayRecord = session.query(Watering). \
                        filter(Watering.greenhouse_id == greenhouse.id). \
                        filter(Watering.date == datetime.date.today() - datetime.timedelta(days = 1)).first()
            todayLevel = todayRecord.time
        except:
            todayLevel = "-"
        
        # waterLevel.append(level)
        waterTime.append(levelToTime(level))
        waterStatus.append(computeWateringStatus(todayLevel, datetime.datetime.now()))
        
    info = zip(greenhouses, waterStatus, waterTime)  
    print info

    return render_template('greenhouse/greenhouses.html', 
                            info = info, 
                            farm_id = farm_id)
    
@app.route('/farm/<int:farm_id>/new/', methods=['GET', 'POST'])
def newGreenhouse(farm_id):
    if request.method == 'POST':
        newGreenhouse = Greenhouse(name = request.form['name'], farm_id = farm_id)
        session.add(newGreenhouse)
        session.commit()
        return redirect(url_for('greenhouses', farm_id = farm_id))
    else:
        return render_template('greenhouse/newGreenhouse.html', farm_id = farm_id)
        
@app.route('/farm/<int:farm_id>/<int:greenhouse_id>/edit/',
           methods=['GET', 'POST'])
def editGreenhouse(farm_id, greenhouse_id):
    editedGreenhouse = session.query(Greenhouse).filter_by(id = greenhouse_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedGreenhouse.name = request.form['name']
        session.add(editedGreenhouse)
        session.commit()
        return redirect(url_for('greenhouses', farm_id = farm_id))
    else:
        return render_template(
            'greenhouse/editGreenhouse.html', farm_id = farm_id, 
            greenhouse_id = greenhouse_id, greenhouse = editedGreenhouse)
            
@app.route('/farm/<int:farm_id>/<int:greenhouse_id>/delete/',
           methods=['GET', 'POST'])
def deleteGreenhouse(farm_id, greenhouse_id):
    greenhouseToDelete = session.query(Greenhouse).filter_by(id = greenhouse_id).one()
    if request.method == 'POST':
        session.delete(greenhouseToDelete)
        session.commit()
        return redirect(url_for('greenhouses', farm_id = farm_id))
    else:
        return render_template('greenhouse/deleteGreenhouse.html', greenhouse = greenhouseToDelete)
        
        
@app.route('/greenhouse/<int:greenhouse_id>/')
@app.route('/greenhouse/<int:greenhouse_id>/nodes/')
def nodes(greenhouse_id):
    nodes = session.query(Node).filter_by(greenhouse_id = greenhouse_id).all()
    watering = session.query(Watering).filter_by(greenhouse_id = greenhouse_id).all();
    greenhouse = session.query(Greenhouse).filter_by(id = greenhouse_id).one()
    return render_template('node/nodes.html', nodes = nodes,
                                              greenhouse_id = greenhouse_id, 
                                              greenhouse = greenhouse, 
                                              watering = watering)
    
@app.route('/greenhouse/<int:greenhouse_id>/new/', methods=['GET', 'POST'])
def newNode(greenhouse_id):
    if request.method == 'POST':
        greenhouse = session.query(Greenhouse).filter_by(id = greenhouse_id).one()
        newNode = Node(name = request.form['name'], greenhouse_id = greenhouse_id, farm_id = greenhouse.farm_id)
        session.add(newNode)
        session.commit()
        return redirect(url_for('nodes', greenhouse_id = greenhouse_id))
    else:
        return render_template('node/newNode.html', greenhouse_id = greenhouse_id)
        
@app.route('/greenhouse/<int:greenhouse_id>/<int:node_id>/edit/',
           methods=['GET', 'POST'])
def editNode(node_id, greenhouse_id):
    editedNode = session.query(Node).filter_by(id = node_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedNode.name = request.form['name']
        session.add(editedNode)
        session.commit()
        return redirect(url_for('nodes', greenhouse_id = greenhouse_id))
    else:
        return render_template(
            'node/editNode.html', node_id = node_id, 
            greenhouse_id = greenhouse_id, node = editedNode)
            
@app.route('/greenhouse/<int:greenhouse_id>/<int:node_id>/delete/',
           methods=['GET', 'POST'])
def deleteNode(greenhouse_id, node_id):
    nodeToDelete = session.query(Node).filter_by(id = node_id).one()
    if request.method == 'POST':
        session.delete(nodeToDelete)
        session.commit()
        return redirect(url_for('nodes', greenhouse_id = greenhouse_id))
    else:
        return render_template('node/deleteNode.html', node = nodeToDelete)
        
@app.route('/upload/')
def uploadData():
    node_id = request.args.get('id','nan');
    if node_id == 'nan':
        return JSONResponse('Invalid Node ID', 400)
    else:
        try:
            node_id = int(node_id)
        except:
            return JSONResponse('Invalid Node ID', 400)
    
    api_key = request.args.get('k','nan');
    if api_key == 'nan':
        return JSONResponse('Invalid API key', 400)
    
    farm = session.query(Farm).filter_by(api_key=api_key).one()
    if farm == None:
        return JSONResponse('Invalid API key', 400)
        
    node = session.query(Node).filter_by(id=node_id).one()
    if node.farm_id != farm.id:
        return JSONResponse('Permission denied', 400)
        
    temperature = request.args.get('t','nan');
    if temperature != "nan":
        try:
            temperature = float(temperature)
        except:
            print "temperature not a number"
    if isinstance(temperature, float):
        tempData = Temperature(value=temperature, node_id=node.id)
        session.add(tempData)

    humidity = request.args.get('h','nan');
    if humidity != "nan":
        try:
            humidity = float(humidity)
        except:
            print "humidity not a number"
    if isinstance(humidity, float):
        humData = Humidity(value=humidity, node_id=node.id)
        session.add(humData)

    session.commit()
    response = make_response(json.dumps('OK', 200))
    response.headers['Content-Type'] = 'application/json'
    return response
            
@app.route('/node/<int:node_id>/', methods=['GET'])
def showNode(node_id):
    # if 'username' not in login_session or user_id != login_session['user_id']:
    #     response = make_response(
    #         json.dumps('Permission denied.', 400))
    #     response.headers['Content-Type'] = 'application/json'
    #     return response
    # user = session.query(User).filter_by(id=user_id).one();
    
    node = session.query(Node).filter_by(id=node_id).one();
    greenhouse = session.query(Greenhouse).filter_by(id=node.greenhouse_id).one();
    farm = session.query(Farm).filter_by(id=node.farm_id).one();
    
    from_date_str   = request.args.get('from', time.strftime("%Y-%m-%d 00:00"))
    to_date_str     = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    timezone        = request.args.get('timezone','Etc/UTC');
    range_h_form    = request.args.get('range_h','');
    range_h_int     = "nan"
    try: 
        range_h_int = int(range_h_form)
    except:
        print "range_h_form not a number"
    
    if not validate_date(from_date_str):
        from_date_str   = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str     = time.strftime("%Y-%m-%d %H:%M")

    from_date_obj       = datetime.datetime.strptime(from_date_str,'%Y-%m-%d %H:%M')
    to_date_obj         = datetime.datetime.strptime(to_date_str,'%Y-%m-%d %H:%M')

    if isinstance(range_h_int,int): 
        arrow_time_from = arrow.utcnow().replace(hours=-range_h_int)
        arrow_time_to   = arrow.utcnow()
        from_date_utc   = arrow_time_from.strftime("%Y-%m-%d %H:%M")    
        to_date_utc     = arrow_time_to.strftime("%Y-%m-%d %H:%M")
        from_date_str   = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
        to_date_str     = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
    else:
        #Convert datetimes to UTC so we can retrieve the appropriate records from the database
        from_date_utc   = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")   
        to_date_utc     = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

    #print from_date_str
    #print to_date_str
    tempRecords = session.query(Temperature).filter_by(node_id=node_id).filter( (Temperature.datetime >= from_date_utc.format('YYYY-MM-DD HH:mm')) & (Temperature.datetime <= to_date_utc.format('YYYY-MM-DD HH:mm'))).all()
    humRecords = session.query(Humidity).filter_by(node_id=node_id).filter( (Humidity.datetime >= from_date_utc.format('YYYY-MM-DD HH:mm')) & (Humidity.datetime <= to_date_utc.format('YYYY-MM-DD HH:mm'))).all()
    
    time_adjusted_temperatures = []
    time_adjusted_humidity = []

    for record in humRecords:
        local_timedate = arrow.get(record.datetime, 'Etc/UTC').to(timezone)
        # record.datetime = local_timedate.format('YYYY-MM-DD HH:mm:ss')
        # record.datetime = datetime.datetime.strptime(local_timedate.format('YYYY-MM-DD HH:mm:ss'),'%Y-%m-%d %H:%M:%S')
        time_adjusted_humidity.append([local_timedate.format('YYYY-MM-DD HH:mm:ss'), round(record.value,2)])

    for record in tempRecords:
        local_timedate = arrow.get(record.datetime, 'Etc/UTC').to(timezone)
        # record.datetime = local_timedate.format('YYYY-MM-DD HH:mm:ss')
        # record.datetime = datetime.datetime.strptime(local_timedate.format('YYYY-MM-DD HH:mm:ss'),'%Y-%m-%d %H:%M:%S')
        time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm:ss'), round(record.value,2)])

    return render_template('node/showNode.html', tempRecords = time_adjusted_temperatures,
                                                humRecords =  time_adjusted_humidity,
                                                node_id = str(node_id), 
                                                temp_items= len(tempRecords), 
                                                api_key="ABCDEFGHIJKLMNOP",
                                                from_date=from_date_str,
                                                to_date=to_date_str,
                                                farm = farm,
                                                greenhouse = greenhouse);
                                                

# def watering(greenhouse_id, methods=['GET', 'POST']):
#     watering = session.query(Watering).filter_by(greenhouse_id = greenhouse_id).all();
#     if request.method == 'POST':
    
            
def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    app.secret_key = 'thisIsXiaoxiong'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
