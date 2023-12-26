from App import app, db, bcrypt, login_manager
from flask import request, jsonify
from pymongo import MongoClient
import smtplib
import os
import uuid
import datetime
# import imaplib
import email
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash


# ================================================= Auth ================================================

host = "20.197.17.85"

# MongoDB connection setup
client = MongoClient('mongodb+srv://resume:resume123@cluster0.fjnp4qu.mongodb.net/')
db = client['resume_project']
collection = db['resumes']

UPLOAD_FOLDER = '/var/www/html/Resume_Builder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "secretKey"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/registerStudent', methods=['POST'])
def register_student():
    try:
        data = request.get_json()

        # Get parameters from the JSON data
        students_db = db['students_db']
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        password = data.get('password')
        phn = data.get('phn')
        que = data.get('que')
        ans = data.get('ans')
        sid = str(uuid.uuid4().hex)
        admin = students_db.find_one({"email": email}, {"_id": 0})
        if admin:
            return jsonify({"success":False,"error":"email Already Exist"})

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "email and password are required."}), 400  # Bad Request

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Store admin information in the MongoDB collection
        students_db = db['students_db']
        students_db.insert_one({"fname":fname, "lname":lname, "email": email, "phn":phn, "password": hashed_password, "que":que, "ans":ans, "sid":sid})

        return jsonify({"message": " Registration Successful.","success":True, "sid":sid})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal Server Error
    
@app.route('/registerAdmin', methods=['POST'])
def register_admin():
    try:
        data = request.get_json()

        # Get parameters from the JSON data
        students_db = db['admin_db']
        fname = data.get('fname')
        lname = data.get('lname')
        email = data.get('email')
        password = data.get('password')
        phn = data.get('phn')
        aid = str(uuid.uuid4().hex)
        admin = students_db.find_one({"email": email}, {"_id": 0})
        if admin:
            return jsonify({"success":False,"error":"email Already Exist"})

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "email and password are required."}), 400  # Bad Request

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Store admin information in the MongoDB collection
        students_db = db['admin_db']
        students_db.insert_one({"fname":fname, "lname":lname, "email": email, "phn":phn, "password": hashed_password, "aid":aid})

        return jsonify({"message": "Admin added successfully.","success":True, "aid":aid})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Internal Server Error
    
import jwt
import datetime
from flask import jsonify

def create_jwt_token(sid):
    payload = {
        'sid': sid,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expiration time
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@app.route('/loginStudent', methods=['POST'])
def login_student():
    try:
        data = request.get_json()

        # Get parameters from the JSON data
        email = data.get('email')
        password = data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "email and password are required.", "success": False}), 400  # Bad Request

        # Find the admin based on email
        students_db = db["students_db"]
        student = students_db.find_one({"email": email}, {"_id": 0})

        if not student or not check_password_hash(student.get("password", ""), password):
            return jsonify({"error": "Invalid email or password.", "success": False}), 401  # Unauthorized

        # Generate JWT token
        token = create_jwt_token(student['sid']).decode('utf-8')  # Decode bytes to string

        return jsonify({"message": "Login successful.", "success": True, "sid": student['sid'], "token": token})

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500  # Internal Server Error
    
@app.route('/loginAdmin', methods=['POST'])
def login_admin():
    try:
        data = request.get_json()

        # Get parameters from the JSON data
        email = data.get('email')
        password = data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "email and password are required.", "success": False}), 400  # Bad Request

        # Find the admin based on email
        students_db = db["admin_db"]
        student = students_db.find_one({"email": email}, {"_id": 0})

        if not student or not check_password_hash(student.get("password", ""), password):
            return jsonify({"error": "Invalid email or password.", "success": False}), 401  # Unauthorized

        # Generate JWT token
        token = create_jwt_token(student['aid']).decode('utf-8')  # Decode bytes to string

        return jsonify({"message": "Login successful.", "success": True, "aid": student['aid'], "token": token})

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500  # Internal Server Error



# Endpoint for requesting password reset (for admin)
@app.route("/sendApprove", methods=["GET"])
def sendApprove():
    try:
        mailToSend = request.args.get('email')
        # Send the password reset link via email
        sender_email = "partbarse92@gmail.com"
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login("partbarse92@gmail.com", "xdfrjwaxctwqpzyg")

        message_text = f"Hello, Your Resume is now Approved by Admin"
        message = MIMEText(message_text)
        message["Subject"] = "Request Approved Successfully"
        message["From"] = sender_email
        message["To"] = mailToSend

        smtp_server.sendmail(sender_email, mailToSend, message.as_string())
        smtp_server.quit()

        return jsonify({'success': True, 'msg': 'Mail Send'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500
    



# Endpoint for requesting password reset (for admin)
@app.route("/sendApproveNew", methods=["GET"])
def sendApprove_New():
    try:
        sid = request.args.get('sid')
        students_db = db["students_db"]
        student_data = collection.find_one({"sid":sid}, {"_id":0})
        mailToSend = student_data['personal']['email']
        # Send the password reset link via email
        sender_email = "partbarse92@gmail.com"
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login("partbarse92@gmail.com", "xdfrjwaxctwqpzyg")

        message_text = f"Hello, Your Resume is now Approved by Admin"
        message = MIMEText(message_text)
        message["Subject"] = "Request Approved Successfully"
        message["From"] = sender_email
        message["To"] = mailToSend

        smtp_server.sendmail(sender_email, mailToSend, message.as_string())
        smtp_server.quit()

        data = {
            "isApproved":"Approved"
        }
        new_values = {"$set": data}
        collection.update_one({"sid":sid}, new_values)

        return jsonify({'success': True, 'msg': 'Mail Send'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500
    





@app.route("/sendDisapprove", methods=["GET"])
def sendDisapprove():
    try:
        mailToSend = request.args.get('email')
        comment = request.args.get('comment')
        # Send the password reset link via email
        sender_email = "partbarse92@gmail.com"
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login("partbarse92@gmail.com", "xdfrjwaxctwqpzyg")

        message_text = f"Hello, Your Resume is Rejected by Admin \n\n Please Review below comments and resubmit the form - \n {comment}"
        message = MIMEText(message_text)
        message["Subject"] = "Request Approved Rejected"
        message["From"] = sender_email
        message["To"] = mailToSend

        smtp_server.sendmail(sender_email, mailToSend, message.as_string())
        smtp_server.quit()

        return jsonify({'success': True, 'msg': 'Mail Send'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500
    



    

@app.route("/sendDisapproveNew", methods=["GET"])
def sendDisapproveNew():
    try:
        sid = request.args.get('sid')
        comment = request.args.get('comment')
        students_db = db["students_db"]
        student_data = collection.find_one({"sid":sid}, {"_id":0})
        mailToSend = student_data['personal']['email']
        # Send the password reset link via email
        sender_email = "partbarse92@gmail.com"
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login("partbarse92@gmail.com", "xdfrjwaxctwqpzyg")

        message_text = f"Hello, Your Resume is Rejected by Admin \n\n Please Review below comments and resubmit the form - \n {comment}"
        message = MIMEText(message_text)
        message["Subject"] = "Request Approved Rejected"
        message["From"] = sender_email
        message["To"] = mailToSend

        smtp_server.sendmail(sender_email, mailToSend, message.as_string())
        smtp_server.quit()

        data = {
            "isApproved":"Disapproved"
        }
        new_values = {"$set": data}
        collection.update_one({"sid":sid}, new_values)

        return jsonify({'success': True, 'msg': 'Mail Send'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500


    
# MongoDB connection setup
client = MongoClient('mongodb+srv://resume:resume123@cluster0.fjnp4qu.mongodb.net/')
db = client['resume_project']
collection = db['resumes']

# Directory to store files
file_directory = '/var/www/html/Resume_Files/'

def save_file(file, uid):
    try:
        # Get the file extension from the original filename
        original_filename = file.filename
        _, file_extension = os.path.splitext(original_filename)

        # Generate a unique filename using UUID and append the original file extension
        filename = str(uuid.uuid4()) + file_extension

        file_path = os.path.join(file_directory, uid, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        return f'http://{host}/Resume_Files/{uid}/{filename}'
    except Exception as e:
        raise e

@app.route('/submitResume', methods=['POST'])
def submit_resume():
    try:
        data = request.get_json()  # Use get_json() instead of request.json

        # Check if data is a valid dictionary
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid JSON format. Expected a dictionary.',"success":False}), 400

        # Extracting common information
        sid = data.get('sid')
        if sid is None:
            return jsonify({'error': 'Missing "sid" parameter in the request data.',"success":False}), 400

        # Save the modified data to MongoDB
        collection.insert_one(data)

        return jsonify({'message': 'Data stored successfully.',"success":True}), 200

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500

@app.route('/editStudentResume', methods=['PUT'])
def edit_student_resume():
    try:
        data = request.get_json()

        # # Check if data is a valid dictionary
        # if not isinstance(data, dict):
        #     return jsonify({'error': 'Invalid JSON format. Expected a dictionary.', "success": False}), 400

        # Extracting common information
        sid = data.get('sid')
        if sid is None:
            return jsonify({'error': 'Missing "sid" parameter in the request data.', "success": False}), 400

        # Update the student's resume data in MongoDB
        result = collection.update_one({'sid': sid}, {'$set': data})

        # Check if the update was successful
        if result.modified_count > 0:
            return jsonify({'message': 'Data updated successfully.', "success": True}), 200
        else:
            return jsonify({'error': 'No document found for the provided sid.', "success": False}), 404

    except Exception as e:
        return jsonify({'error': str(e), "success": False}), 500

@app.route('/getAllStudentsResume', methods=['GET'])
def get_all_students_resume():
    try:
        # Retrieve all students' resumes from MongoDB
        all_resumes = list(collection.find({}, {'_id': 0}))
        return jsonify({'resumes': all_resumes, "success":True}), 200

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500
    
@app.route('/getStudent', methods=['GET'])
def get_student_resume():
    try:
        sid = request.args.get("sid")
        # Retrieve all students' resumes from MongoDB
        resume = collection.find_one({"sid":sid}, {'_id': 0})
        return jsonify({'resume': resume,"success":True}), 200

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500
    

@app.route('/deleteResume', methods=['GET'])
def delete_students_resume():
    try:
        sid = request.args.get("sid")
        collection.delete_one({"sid":sid})
        return jsonify({"msg":"Deleted Successfully","success":True}), 200

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500


@app.route('/getStudentLoginInfo', methods=['GET'])
def getStudentLoginInfo():
    try:
        students_db = db["students_db"]
        # Extracting common information
        sid = request.args.get('sid')

        data = students_db.find_one({"sid": sid}, {"_id": 0})
        if data:
            return jsonify({'message': 'Success',"data":data,"success":True}), 200
        else:
            return jsonify({"message":"No Student fount with this sid","success":False})

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500

file_directory = '/var/www/html/Resume_Files/'
    
@app.route('/uploadFile', methods=['POST'])
def upload_file():
    try:
        # Check if 'file' and 'sid' parameters are present in the form data
        if 'file' not in request.files or 'sid' not in request.form:
            return jsonify({'error': 'Missing parameters: file or sid.',"success":False}), 400

        uploaded_file = request.files['file']
        sid = request.form['sid']

        # Check if the file is an allowed type (e.g., image or pdf)
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
        if (
            '.' in uploaded_file.filename
            and uploaded_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions
        ):
            return jsonify({'error': 'Invalid file type. Only allowed: png, jpg, jpeg, gif, pdf.',"success":False}), 400

        # Save the file and get the URL
        file_url = save_file(uploaded_file, sid)

        return jsonify({'message': 'File stored successfully.', 'file_url': file_url,"success":True}), 200

    except Exception as e:
        return jsonify({'error': str(e),"success":False}), 500
    
# Directory to store files
file_directory = '/var/www/html/Resume_Files/'

def delete_file(sid, filename):
    try:
        file_path = os.path.join(file_directory, sid, filename)

        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False
    except Exception as e:
        raise e

@app.route('/deleteFile', methods=['POST'])
def delete_file_api():
    try:
        data = request.json
        # Check if 'sid' and 'url' parameters are present in the form data
        if 'sid' not in data or 'url' not in data:
            return jsonify({'error': 'Missing parameters: sid or url.', "success": False}), 400

        sid = data['sid']
        url = data['url']

        # Extract filename from the file URL
        filename = url.split('/')[-1]

        # Delete the file and check the result
        success = delete_file(sid, filename)

        if success:
            return jsonify({'message': 'File deleted successfully.', "success": True}), 200
        else:
            return jsonify({'error': 'File not found or unable to delete.', "success": False}), 404

    except Exception as e:
        return jsonify({'error': str(e), "success": False}), 500
    
# Endpoint for requesting password reset (for admin)
@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    try:
        from datetime import datetime, timedelta

        user_db = db["students_db"]
        # Get email from request
        email = request.form.get('email')

        # Check if the provided email exists in the database
        user_data = user_db.find_one({"email": email})

        if not user_data:
            return jsonify({'success': False, 'msg': 'Email not found'}), 404

        # Generate a random password reset token and update it in the user's document in the database
        reset_token = jwt.encode({
            'sid': user_data["sid"],
            'exp': datetime.utcnow() + timedelta(hours=1)  # Token expiration time (1 hour)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        user_db.update_one({"email": email}, {"$set": {"reset_token": reset_token}})

        # Send the password reset link via email
        sender_email = "partbarse92@gmail.com"
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login("partbarse92@gmail.com", "xdfrjwaxctwqpzyg")

        reset_link = f"http://localhost:8090/forgotpassword?email={email}&reset_token={reset_token}"
        message_text = f"Hi,\n\nYou have requested a password reset for your admin account.\n\nPlease click on the following link to reset your password:\n\n{reset_link}\n\nIf you didn't request this reset, please ignore this email.\n\nBest regards,\nThe Admin Team"
        message = MIMEText(message_text)
        message["Subject"] = "Password Reset Request"
        message["From"] = sender_email
        message["To"] = email

        smtp_server.sendmail(sender_email, email, message.as_string())
        smtp_server.quit()

        return jsonify({'success': True, 'msg': 'Password reset link sent to your email'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500


# Endpoint for handling password reset (for admin)
@app.route("/reset_password", methods=["POST"])
def reset_password():
    try:
        user_db = db["students_db"]
        # Get form data from request
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        reset_token = request.form.get('reset_token')

        # Check if the provided email exists in the database
        user_data = user_db.find_one({"email": email})

        if not user_data:
            return jsonify({'success': False, 'msg': 'Email not found'}), 404

        # Verify the reset token
        try:
            jwt.decode(reset_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'msg': 'Reset token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'success': False, 'msg': 'Invalid reset token', "reason": str(e)}), 401

        # If token is valid, update the user's password in the database
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user_db.update_one({"email": email}, {"$set": {"pass": hashed_password, "reset_token": None}})

        return jsonify({'success': True, 'msg': 'Password reset successful'}), 200

    except Exception as e:
        return jsonify({'success': False, 'msg': 'Something Went Wrong.', 'reason': str(e)}), 500