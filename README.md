# mad1_household
# Household Services Application

**Modern Application Development I Project**

The Household Services Application is a multi-user web platform for managing and providing home services. The system supports three roles — **Admin**, **Service Professional**, and **Customer** — enabling service management, booking, and tracking in a structured and efficient manner.

---

## Features

### Admin
- Predefined superuser with full access (no registration required)
- Manage all users (customers and service professionals)
- Approve service professionals after verification of profile documents
- Block/unblock users based on fraudulent activity or poor reviews
- Create, update, and delete available services with base prices

### Service Professional
- Register and login to the platform
- View assigned service requests from customers
- Accept or reject service requests
- Close service requests after completion
- Profiles visible based on customer reviews

### Customer
- Register and login to the platform
- Search for services by name, location, or pin code
- Create, edit, and close service requests
- Post reviews/remarks on completed services

---

## Technology Stack

- **Backend:** Flask
- **Frontend:** Jinja2 templates + Bootstrap
- **Database:** SQLite

---

## Core Functionalities

1. **Authentication**
   - Role-based login/register forms for Admin, Service Professional, and Customer
   - Separate dashboards for each role

2. **Admin Dashboard**
   - Monitor all users and approve/block service professionals or customers
   - Create, update, and delete services
   - Manage service requests and monitor service completion

3. **Service Management**
   - CRUD operations on services (name, price, time required, description)

4. **Service Requests**
   - Customers can create, edit, and close service requests
   - Professionals can accept/reject and close service requests

5. **Search Functionality**
   - Customers can search services by name, location, or pin code
   - Admin can search professionals for monitoring purposes

6. **Optional/Recommended Functionalities**
   - API endpoints for user, service, and request management
   - Frontend and backend form validation
   - Charts and dashboards using libraries like Chart.js
   - Responsive frontend design
   - Optional dummy payment portal or extra features

---

## Database Schema (Simplified)

**User**
- `id`, `name`, `role`, `email`, `password`, `date_created`

**Service**
- `id`, `name`, `base_price`, `time_required`, `description`

**Service Professional**
- `id`, `name`, `service_type`, `experience`, `description`

**Service Request**
- `id`, `service_id`, `customer_id`, `professional_id`, `date_of_request`, `date_of_completion`, `service_status`, `remarks`

---

## Installation and Setup

1. Clone the repository:  
   ```
   git clone https://github.com/your-username/household.git
   cd household
Set up a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
Initialize the database programmatically:


python create_db.py  # Example file to create tables
Run the application:

flask run

Notes
Admin account is predefined and cannot be registered via the app.

Wireframes are for guidance; frontend design may vary.

Database must be created programmatically; manual creation is not allowed.
