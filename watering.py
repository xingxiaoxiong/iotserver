
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

def computeWateringStatus(level, currentTime):
    if level == 1:
        return datetime.now().minute <= 3
    elif level == 2:
        return datetime.now().minute <= 6
    elif level == 3:
        return datetime.now().minute <= 9
    elif level == 4:
        return datetime.now().minute <= 12
    elif level == 5:
        if datetime.now().hour >= 18:
            delta = datetime.now() - datetime.datetime(datetime.now().year, datetime.now().month, datetime.now().day, 18, 0)
        else:
            yesterday = datetime.now() - timedelta(days=1)
            delta = datetime.now() - datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 18, 0)
        return delta.seconds % (45 * 60) < 12 * 60
    else: 
        return "-"

def levelToTime(level):
    if level == 1:
        return 72
    elif level == 2:
        return 144
    elif level == 3:
        return 216
    elif level == 4:
        return 288
    elif level == 5:
        return 384
    else: 
        return "-"

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

if __name__ == '__main__':
    greenhouses = session.query(Greenhouse).all();
    for greenhouse in greenhouses:
        nodes = session.query(Node).filter_by(greenhouse_id = greenhouse.id).all();
        cnt = 0
        humidity = 0.0
        hum = 0.0
        
        for node in nodes:
            try:
                hum = session.query(Humidity).filter(Humidity.node_id == node.id).filter(Humidity.datetime > tenMinBefore).one();
            except:
                hum = None
            if hum != None:
                humidity = humidity + hum
                cnt = cnt + 1
                
        if cnt > 0:
            humidity = humidity / cnt
        data = timeToTurnOn(humidity)
        
        water = Watering(time = data, date = date.today(), greenhouse_id = greenhouse.id)
        session.add(water)
        session.commit()
    
    
    
    
    
        