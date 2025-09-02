from flask import Flask, render_template
from backend.models import *       #model file is getting linked

def init_app():
    proj=Flask(__name__)   #object of flask
    proj.debug=True    
    proj.secret_key = '123' 
      # Direct access app by outer modules like db,authentication(to make sure user is not able to sensitive info but we can
    proj.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///proj.sqlite3"
    #proj.config["SQLALCHEMY_POOL_SIZE"]=100
    proj.app_context().push() #direct access to app

    db.init_app(proj) #object.method(<parameter>)
    print("Finally Backend")
    return proj


app=init_app()   # app is called by init app 
from backend.controllers import *

if __name__=="__main__":
    app.run()

