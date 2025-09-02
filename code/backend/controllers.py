
from flask import Flask, render_template,request,redirect,url_for,flash,session,jsonify
from flask import current_app as app  
from backend.models import *
from datetime import date ,datetime


@app.route("/") 
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        uname = request.form.get("uname")
        pwd = request.form.get("pwd")

        usr = Cust_info.query.filter_by(uname=uname, pwd=pwd).first()
        if usr:
            session['user_id'] = usr.id
            session['username'] = usr.uname  

            if usr.role == 0:
                return redirect(url_for("admin_dashboard"))
            elif usr.role == 1:
                return redirect(url_for("user_dashboard", username=usr.uname))

        pro_usr = Pro_info.query.filter_by(uname=uname, pwd=pwd).first()
        if pro_usr:
    
            if pro_usr.status == 'blocked':
                flash("Your account has been blocked by the admin.", "danger")
                return redirect(url_for("user_login"))
            
        
            if pro_usr.role == 2 and pro_usr.status == 'pending':
                flash("You have not been approved by the admin yet.", "danger")
                return redirect(url_for("user_login"))

    
            if pro_usr.role == 2 and pro_usr.status == 'approved':
                session['user_id'] = pro_usr.id
                session['username'] = pro_usr.uname
                return redirect(url_for("professional_dashboard", username=pro_usr.uname))        
        flash("Invalid Credentials!!", "danger")
        return render_template("login.html")

    return render_template("login.html")

        
@app.route("/customer_signup",methods=["GET","POST"]) 
def user_signup():
    if request.method=="POST":     
        uname=request.form.get("uname")
        email=request.form.get("email")
        pwd=request.form.get("pwd")
        add=request.form.get("add")
        pin=request.form.get("pin")

        usr=Cust_info.query.filter_by(uname=uname).first()     
        if not usr:
            new_user=Cust_info(uname=uname,pwd=pwd,email=email,add=add,pin=pin)
            db.session.add(new_user)
            db.session.commit()
            return render_template("login.html")      
        else:
            flash("Username Already Exists","danger")
            return render_template("customer_signup.html")   
   
    return render_template("customer_signup.html")   


@app.route("/professional_signup",methods=["GET","POST"])
def pro_signup():
    if request.method=="POST":      
        uname=request.form.get("uname")
        email=request.form.get("email")
        pwd=request.form.get("pwd")
        service_type=request.form.get("service_type")
        exp=request.form.get("exp")
        add=request.form.get("add")
        pin=request.form.get("pin")

        usr=Pro_info.query.filter_by(uname=uname).first()     
        if not usr: 
            new_user=Pro_info(uname=uname,email=email,pwd=pwd,service_type=service_type,exp=exp,add=add,pin=pin)
            db.session.add(new_user)
            db.session.commit()
            pro_in = fetch_pro()
            return render_template("login.html")
        else:
            flash("Username Already Exists!!", "danger")
            return render_template("professional_signup.html")   
    
    return render_template("professional_signup.html")  


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("user_login")) 



def fetch_services():
    services=Service.query.all()
    service_in = {}
    for service in services:
        service_in[service.id]= (service.name, service.price, service.time_required,service.description)
    return(service_in)


def fetch_pro():
    pro=Pro_info.query.all()
    pro_in = {}
    for p in pro:
        pro_in[p.id]= (p.uname, p.service_type,p.exp,p.email,p.add,p.pin)
    return(pro_in)   


def fetch_service_requests(user_id):
    service_requests = Service_request.query.filter_by(user_id=user_id).all()
    requests = {}
    for req in service_requests:
        requests[req.id] = {"service_name": req.service.name, "professional_name": req.pro_info.uname, "professional_email": req.pro_info.email, "status": req.status, "date_of_request": req.date_of_request}
    return(requests)
 


@app.route('/admin_dashboard')
def admin_dashboard():
    username = session.get('username')
    query = request.args.get('query', '').strip()
    search_by = request.args.get('search_by', '')

    search_results = []

    new_pro = Pro_info.query.filter_by(status='pending').all()
    approved_professionals = Pro_info.query.filter_by(status='approved').all()
    blocked_professionals = Pro_info.query.filter_by(status='blocked').all()
    services = Service.query.all()


    if query and search_by:
        if search_by == 'service_name':
            search_results = Service.query.filter(Service.name.ilike(f"%{query}%")).all()
        elif search_by == 'pro_name':
            search_results = Pro_info.query.filter(
                Pro_info.uname.ilike(f"%{query}%"),
                Pro_info.status == 'approved'
            ).all()
            print("Professional Search Query:", query)
            print("Professional Search Results:", search_results)

     

    customers = Cust_info.query.all() 

    service_requests = db.session.query(
        Service_request.id.label('request_id'),
        Cust_info.uname.label('customer_name'),
        Pro_info.uname.label('professional_name'),
        Service.name.label('service_name'),
        Service_request.date_of_request,
        Service_request.rating,
        Service_request.status
    ).join(Cust_info, Service_request.user_id == Cust_info.id) \
     .outerjoin(Pro_info, Service_request.pro_id == Pro_info.id) \
     .outerjoin(Service, Service_request.service_id == Service.id) \
     .all()

    ser = {s.id: [s.name, s.price, s.time_required, s.description] for s in services}

    return render_template(
        'admin_dashboard.html',
        new_pro=new_pro,
        approved_professionals=approved_professionals,
        users=ser,
        customers=customers,
        username=username,
        blocked_professionals=blocked_professionals,
        service_requests=service_requests,
        search_results=search_results,
        search_by=search_by,
        search_query=query)


@app.route("/service_summary_data", methods=['GET'])
def service_summary_data():

    status_counts = db.session.query(
        Service_request.status, db.func.count(Service_request.id)
    ).group_by(Service_request.status).all()

    rating_counts = db.session.query(
        Service_request.rating, db.func.count(Service_request.id)
    ).group_by(Service_request.rating).all()

    status_data = {status: count for status, count in status_counts}
    rating_data = {rating: count for rating, count in rating_counts if rating is not None}

    return jsonify({'status_data': status_data, 'rating_data': rating_data})



@app.route("/add_service", methods=["GET", "POST"])
def add_service():
    if request.method == "POST":  
        name = request.form.get("name")
        price = request.form.get("price")
        time_required = request.form.get("time_required")
        description = request.form.get("description")
        
        ext_ser = Service.query.filter_by(name=name).first() 
        if ext_ser:
            user_summary = fetch_services()
            flash("Service Already Exists!!", "error")
            return render_template("admin_dashboard.html", users=user_summary)         
        new_ser = Service(name=name, price=price, time_required=time_required, description=description)
        db.session.add(new_ser)
        db.session.commit()
        
        user_summary = fetch_services()
        flash("Service Added Successfully!!", "success")
        return render_template("admin_dashboard.html", users=user_summary) 
    
    return redirect(url_for('admin_dashboard'))


@app.route("/edit_service/<int:id>", methods=["POST"])
def edit_service(id):
    service = Service.query.get(id)

    if service:

        service_name = request.form.get("service_name", service.name)
        price = request.form.get("price", service.price)
        time_required = request.form.get("time_required", service.time_required)
        description = request.form.get("description", service.description)

        existing_service = Service.query.filter_by(name=service_name).first()
        if existing_service and existing_service.id != id:
            flash("Service name already exists. Please choose a different name.", "error")
            return redirect(url_for("edit_service", id=id)) 
        
        service.name = service_name
        service.price = price
        service.time_required = time_required
        service.description = description
        
        db.session.commit()
        flash("Service updated successfully!", "success")
    else:
        flash("Service not found.", "error")

    return redirect(url_for("admin_dashboard"))


@app.route("/delete_service/<int:id>", methods=["POST"])
def delete_service(id):
    ser = Service.query.get(id)
    if ser:
        db.session.delete(ser)
        db.session.commit()
        flash("Service deleted successfully!","success")
    else:
        flash("Service not found!","error")
    return redirect(url_for("admin_dashboard"))   


@app.route("/approve_professional/<int:id>", methods=["GET","POST"])
def approve_professional(id):
    pro = Pro_info.query.get(id)
    pro.status = 'approved' 
    db.session.commit()
    
    flash(f'Professional {pro.uname} has been approved!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route("/delete_professional/<int:id>", methods=["POST"])
def delete_professional(id):
    pro = Pro_info.query.get(id)
    if pro:
        db.session.delete(pro)
        db.session.commit()
        flash("Professional deleted successfully!","success")
    else:
        flash("Professional not found!","error")
    return redirect(url_for("admin_dashboard"))    


@app.route("/block_professional/<int:id>", methods=["POST"])
def block_professional(id):
    pro = Pro_info.query.get(id)
    if pro:
        pro.status = 'blocked'
        db.session.commit()
        flash(f'Professional {pro.uname} has been blocked.', 'warning')
    return redirect(url_for('admin_dashboard'))


@app.route("/unblock_professional/<int:id>", methods=["POST"])
def unblock_professional(id):
    pro = Pro_info.query.get(id)
    if pro:
        pro.status = 'approved'
        db.session.commit()
        flash(f'Professional {pro.uname} has been unblocked.', 'success')
    return redirect(url_for('admin_dashboard'))    


@app.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    user_id = session.get("user_id")
    if not user_id:
        flash("User not logged in.", "error")
        return redirect(url_for("user_login"))

    user = Cust_info.query.get(user_id)
    username = session.get('username')
    services = Service.query.all()  

    query = request.args.get('query', '').strip()
    search_results = []

    if query:
        search_results = Service.query.filter(Service.name.ilike(f"%{query}%")).all()

    requested_services = db.session.query(
        Service_request.id.label('req_id'),
        Service.name.label('service_name'),
        Service_request.date_of_request
    ).join(Service, Service_request.service_id == Service.id)\
     .filter(Service_request.user_id == user_id, Service_request.status == "requested").all()

    service_history = db.session.query(
        Service_request.id.label('req_id'),
        Service.name.label('service_name'),
        Service.description.label('service_description'),
        Pro_info.id.label('professional_id'),
        Pro_info.uname.label('professional_name'),
        Pro_info.email.label('professional_email'),
        Service_request.date_of_request,
        Service_request.status
    ).join(Service, Service_request.service_id == Service.id)\
     .join(Pro_info, Service_request.pro_id == Pro_info.id)\
     .filter(Service_request.user_id == user_id, Service_request.status.in_(["accepted", "closed"])).all()

    return render_template('user_dashboard.html',services=services,user=user,username=user.uname,service_history=service_history,requested_services=requested_services,search_results=search_results,search_query=query)


@app.route('/status_summary', methods=['GET'])
def status_summary():
    user_id = session.get('user_id') 

    service_history = db.session.query(
        Service_request.id.label('req_id'),
        Service.name.label('service_name'),
        Service.description.label('service_description'),
        Pro_info.id.label('professional_id'),
        Pro_info.uname.label('professional_name'),
        Pro_info.email.label('professional_email'),
        Service_request.date_of_request,
        Service_request.status
    ).join(Service, Service_request.service_id == Service.id)\
     .join(Pro_info, Service_request.pro_id == Pro_info.id)\
     .filter(Service_request.user_id == user_id, Service_request.status.in_(["accepted", "closed"])).all()

    requested = sum(1 for req in service_history if req.status == "accepted")
    closed = sum(1 for req in service_history if req.status == "closed")

    closed_services_summary = {}
    for req in service_history:
        if req.status == "closed":
            closed_services_summary[req.service_name] = closed_services_summary.get(req.service_name, 0) + 1

    return jsonify({
        "requested": requested,
        "closed": closed,
        "closed_services_summary": closed_services_summary
    })
    

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    user = Cust_info.query.get(user_id)
    if user:
        user.uname = request.form.get('uname')
        user.email = request.form.get('email')
        user.add = request.form.get('address')
        user.pin = request.form.get('pincode')
        db.session.commit()
    return redirect(url_for('user_dashboard'))


@app.route('/book_service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("User not logged in.", "error")
        return redirect(url_for("user_login"))

    service = Service.query.get(service_id)
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("user_dashboard"))

    professional = Pro_info.query.filter_by(service_type=service.name, status='approved').first()
    if not professional:
        flash("No professional available for this service.", "error")
        return redirect(url_for("user_dashboard"))

    new_request = Service_request(
        service_id=service_id,
        user_id=user_id,
        pro_id=None,
        date_of_request=date.today(),
        status="requested"
    )
    db.session.add(new_request)
    db.session.commit()
    flash("Service request sent successfully!", "success")

    return redirect(url_for('user_dashboard'))  


@app.route('/cancel_service_request/<int:request_id>', methods=['POST'])
def cancel_service_request(request_id):
    service_request = Service_request.query.get(request_id)
    
    user_id = session.get("user_id")
    if not service_request or service_request.user_id != user_id:
        flash("Request not found .", "error")
        return redirect(url_for('user_dashboard'))
    
    db.session.delete(service_request)
    db.session.commit()
    flash("Service request canceled successfully.", "success")
    
    return redirect(url_for('user_dashboard'))


@app.route('/close_request/<int:request_id>', methods=['POST'])
def close_request(request_id):
    rating = request.form.get('service_rating')
    remarks = request.form.get('remarks')

    service_request = Service_request.query.get(request_id)
    if service_request:
        service_request.status = "closed" 
        service_request.rating = rating
        service_request.remarks = remarks
        db.session.commit()
        flash("Service request closed successfully!", "success")
    else:
        flash("Service request not found.", "error")

    return redirect(url_for('user_dashboard'))
 


@app.route('/edit_request/<int:request_id>', methods=["GET", "POST"])
def edit_request(request_id):
    date_of_request = request.form.get('date_of_request')

    service_request = Service_request.query.get(request_id)
    if not service_request:
        flash("Request not found.", "error")
        return redirect(url_for('user_dashboard'))

    if date_of_request:
        try:
            service_request.date_of_request = datetime.strptime(date_of_request, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for('user_dashboard'))
    else:
        flash("Please provide a valid date of request.", "error")
        return redirect(url_for('user_dashboard'))

    db.session.commit()
    flash("Request updated successfully!", "success")
    return redirect(url_for('user_dashboard'))

    

@app.route("/professional_dashboard", methods=["GET"])
def professional_dashboard():
    user_id = session.get("user_id")
    username = session.get("username")    

    if not user_id:
        flash("You are not logged in.", "error")
        return redirect(url_for("user_login"))
    
    pro = Pro_info.query.get(user_id)
    if not pro:
        flash("Professional details not found.", "danger")
        return redirect(url_for("user_login"))

    customer_requests = db.session.query(
        Service_request.id.label('request_id'),
        Cust_info.uname.label('customer_name'),
        Cust_info.email.label('customer_email'),
        Cust_info.add.label('customer_address'),
        Cust_info.pin.label('customer_pincode'),
        Service.name.label('service_name')
    ).join(Cust_info, Service_request.user_id == Cust_info.id)\
     .join(Service, Service_request.service_id == Service.id)\
     .filter(Service_request.pro_id.is_(None), Service_request.status == 'requested', Service.name == pro.service_type ).all()

    closed_services = db.session.query(
        Service_request.id.label('req_id'),
        Cust_info.uname.label('customer_name'),
        Cust_info.email.label('customer_email'),
        Cust_info.add.label('customer_address'),
        Cust_info.pin.label('customer_pincode'),
        Service_request.date_of_request,
        Service_request.rating,
        Service_request.remarks
    ).join(Cust_info, Service_request.user_id == Cust_info.id)\
     .filter(Service_request.pro_id == user_id, Service_request.status == "closed").all()

    search_filter = request.args.get("search_filter")
    search_query = request.args.get("search_query")
    search_results = None

    if search_filter and search_query:
        search_results = db.session.query(
        Service_request.id.label('req_id'),
        Cust_info.uname.label('customer_name'),
        Cust_info.email.label('customer_email'),
        Cust_info.add.label('customer_address'),
        Cust_info.pin.label('customer_pincode'),
        Service_request.date_of_request,
        Service_request.rating,
        Service_request.remarks
    ).join(Cust_info, Service_request.user_id == Cust_info.id)\
    .filter(Service_request.pro_id == user_id, Service_request.status == "closed")

        if search_filter == "date_of_request":
            search_results = search_results.filter(Service_request.date_of_request == search_query)
        elif search_filter == "customer_address":
            search_results = search_results.filter(Cust_info.add.ilike(f"%{search_query}%"))
        elif search_filter == "customer_pincode":
            search_results = search_results.filter(Cust_info.pin.ilike(f"%{search_query}%"))

        search_results = search_results.all()
    else:
        search_results = []  

    return render_template("professional_dashboard.html", 
                           customer_requests=customer_requests,
                           username=pro.uname,
                           pro=pro,
                           closed_services=closed_services,
                           search_results=search_results,
                           search_query=search_query)



@app.route('/pro_ratings_summary', methods=['GET'])
def pro_ratings_summary():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    ratings_query = db.session.query(
        Service_request.rating, 
        db.func.count(Service_request.rating)
    ).filter(Service_request.status == 'closed', Service_request.pro_id == user_id)\
     .group_by(Service_request.rating).all()

    ratings_summary = {str(rating): count for rating, count in ratings_query}

    status_query = db.session.query(
        Service_request.status, 
        db.func.count(Service_request.id)
    ).filter(Service_request.pro_id == user_id)\
     .group_by(Service_request.status).all()

    status_counts = {status: count for status, count in status_query}
    accepted_count = status_counts.get('accepted', 0)
    closed_count = status_counts.get('closed', 0)

    return jsonify({
        "ratings": ratings_summary,
        "status_counts": { "accepted": accepted_count, "closed": closed_count }})


@app.route('/accept_request/<int:request_id>', methods=["POST", "GET"])
def accept_request(request_id):
    service_request = Service_request.query.get(request_id)
    professional_id = session.get("user_id") 
    
    if service_request and professional_id:
        service_request.status = "accepted" 
        service_request.pro_id = professional_id 
        db.session.commit()
        flash("Service request accepted!", "success")
    else:
        flash("Request not found or Professional not logged in.", "error")
    return redirect(url_for('professional_dashboard'))   


@app.route('/reject_request/<int:request_id>', methods=["POST"])
def reject_request(request_id):
    service_request = Service_request.query.get(request_id)
    
    if service_request:
        service_request.status = "rejected"  
        service_request.pro_id = None 
        db.session.commit()
        flash("Service request rejected!", "danger")
    else:
        flash("Request not found.", "error")
    
    return redirect(url_for('professional_dashboard'))



@app.route('/update_professional_profile', methods=["GET","POST"])
def update_professional_profile():
    username = session.get('username')  

    if not username:
        flash("You must be logged in to update your profile.", "error")
        return redirect(url_for('user_login'))     
    professional = Pro_info.query.filter_by(uname=username).first()
    
    if professional:
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        
        professional.uname = name
        professional.email = email
        professional.add = address
        professional.pin = pincode
        
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
    else:
        flash("Professional not found.", "error")
    
    return redirect(url_for('professional_dashboard'))




