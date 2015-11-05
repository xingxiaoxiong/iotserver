from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
import time, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from database_setup import Base, Farm, Greenhouse, Node, Temperature, Humidity

# imports for generating session
from flask import session as login_session
import random, string


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

@app.route('/')
@app.route('/farms/')
def farms():
    farms = session.query(Farm).all()
    print farms
    return render_template('farm/farms.html', farms = farms)
    
@app.route('/farm/<int:farm_id>/')
@app.route('/farm/<int:farm_id>/greenhouses/')
def greenhouses(farm_id):
    greenhouses = session.query(Greenhouse).filter_by(farm_id = farm_id).all()
    print greenhouses
    return render_template('greenhouse/greenhouses.html', greenhouses = greenhouses, farm_id = farm_id)
    
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
    greenhouse = session.query(Greenhouse).filter_by(id = greenhouse_id).one()
    return render_template('node/nodes.html', nodes = nodes, greenhouse_id = greenhouse_id, greenhouse = greenhouse)
    
@app.route('/greenhouse/<int:greenhouse_id>/new/', methods=['GET', 'POST'])
def newNode(greenhouse_id):
    if request.method == 'POST':
        newNode = Node(name = request.form['name'], greenhouse_id = greenhouse_id)
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
            
@app.route('/greenhouse/<int:greenhouse_id>/node/<int:node_id>/', methods=['GET', 'POST'])
def showNode(node_id, greenhouse_id):
    if request.method == 'POST':
        pass
    else:
        return render_template('node/showNode.html', node_id = node_id, greenhouse_id = greenhouse_id)
            
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
