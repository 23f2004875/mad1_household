from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy() #instance of SQLAlchemy

class Cust_info(db.Model):
    __tablename__="cust_info"
    id=db.Column(db.Integer,primary_key=True)
    uname=db.Column(db.String,unique=True,nullable=False)
    email=db.Column(db.String,nullable=False)
    pwd=db.Column(db.String,nullable=False)
    add=db.Column(db.String,nullable=False)
    pin=db.Column(db.Integer,nullable=False)
    role=db.Column(db.Integer,default=1)

class Pro_info(db.Model):
    __tablename__="pro_info"
    id=db.Column(db.Integer,primary_key=True)
    uname=db.Column(db.String,unique=True,nullable=False)
    email=db.Column(db.String,nullable=False)
    pwd=db.Column(db.String,nullable=False)
    service_type=db.Column(db.String,nullable=False)
    exp=db.Column(db.String,nullable=False)
    add=db.Column(db.String,nullable=False)
    pin=db.Column(db.Integer,nullable=False)
    role=db.Column(db.Integer,default=2)
    status = db.Column(db.String, default='pending') 

class Service(db.Model):
    __tablename__="service"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    price=db.Column(db.Integer,nullable=False)
    time_required=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String,nullable=False)

class Service_request(db.Model):
    __tablename__="service_request"
    id=db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer,db.ForeignKey('service.id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('cust_info.id'),nullable=False,)
    pro_id=db.Column(db.Integer,db.ForeignKey('pro_info.id'),nullable=True,)
    
    date_of_request=db.Column(db.Date,nullable=False)
    status=db.Column(db.String,nullable=False)
    rating=db.Column(db.String,nullable=True)
    remarks=db.Column(db.String,nullable=True)
   
    cust_info=db.relationship("Cust_info",backref="service_request")
    pro_info=db.relationship("Pro_info",backref="service_request")
    service=db.relationship("Service",backref="service_request")

 