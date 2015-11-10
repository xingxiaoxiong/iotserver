
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Farm, Greenhouse, Node, Temperature, Humidity, Watering

from datetime import datetime, timedelta, date

engine = create_engine('mysql+pymysql://root:worldofiot@localhost')
engine.execute("USE IoT")
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

tenMinBefore = datetime.today() - timedelta(minutes = 10)

def timeToTurnOn(humidity):
    if humidity > 95.0:
        return 1
    elif humidity > 80.0:
        return 2
    elif humidity > 65:
        return 3
    elif humidity > 50:
        return 4
    else:
        return 5

greenhouses = session.query(Greenhouse).all();
for greenhouse in greenhouses:
    nodes = session.query(Node).filter_by(greenhouse_id = greenhouse.id).all();
    cnt = 0
    humidity = 0.0
    
    for node in nodes:
        hum = session.query(Humidity).filter_by(node_id = node.id, datetime >= tenMinBefore).one();
        if hum != None:
            humidity = humidity + hum
            cnt = cnt + 1
            
    humidity = humidity / cnt
    data = timeToTurnOn(humidity)
    
    water = Watering(time = data, date = date.today(), greenhouse_id = greenhouse.id)
    session.add(water)
    session.commit()
    
    
    
    
    
        