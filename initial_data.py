from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Farm, Greenhouse, Node, Temperature, Humidity

engine = create_engine('mysql+pymysql://root:worldofiot@localhost')
engine.execute("USE IoT")
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#Create farms

farm1 = Farm(name = "Xiaoxiong's farm", api_key = "ABCDABCDABCDABCD", email="xingxiaoxiong@gmail.com")
session.add(farm1)
session.commit()

farm2 = Farm(name = "Terence's farm", api_key = "AAAAAAAAAAAAAAAA", email="terencechia82@gmail.com")
session.add(farm2)
session.commit()

farm3 = Farm(name = "Josh's farm", api_key = "BBBBBBBBBBBBBBBB", email="chiachen.su@gmail.com")
session.add(farm3)
session.commit()



greenhouse1 = Greenhouse(name = "green1", farm_id = farm1.id)
session.add(greenhouse1)
session.commit()

node1 = Node(name = "node1", farm_id = farm1.id, greenhouse_id = greenhouse1.id)
session.add(node1)
session.commit()


