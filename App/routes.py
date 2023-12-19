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

        return jsonify({"message": "Admin added successfully.","success":True, "sid":sid})

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
            return jsonify({'error': 'Invalid JSON format. Expected a dictionary.'}), 400

        # Extracting common information
        sid = data.get('sid')
        if sid is None:
            return jsonify({'error': 'Missing "sid" parameter in the request data.'}), 400

        file_urls = {}

        # Handle candidate file
        candidate_file = request.files.get('candidate')
        if candidate_file:
            file_urls['candidate'] = save_file(candidate_file, sid)

        # Handle passport file
        passport_file = request.files.get('passport')
        if passport_file:
            file_urls['passport'] = save_file(passport_file, sid)

        # Handle German language files
        if data.get('german'):
            for entry in data.get('german', []):
                for module in ['listening_module', 'speaking_module', 'reading_module', 'writing_module']:
                    file = entry.get(module)
                    if file:
                        entry[module] = save_file(file, sid)

        # Handle Post Graduate, Under Graduate, Twelfth, Eleventh, Tenth, and First to Ninth files
        for category in ['post_graduate', 'under_graduate', 'twelweth', 'eleventh', 'tenth', 'first_to_ninth']:
            for entry in data.get(category, []):
                if entry :
                    marksheet_file = entry.get('marksheet')
                    if marksheet_file:
                        entry['marksheet'] = save_file(marksheet_file, sid)

        # Handle Blank Year files
        for entry in data.get('blank_year', []):
            if entry:
                reason_file = entry.get('reason_file')
                if reason_file:
                    entry['reason_file'] = save_file(reason_file, sid)

        # Handle Language files
        signature_file = data['declaration']['signature_img']
        if signature_file:
            data['declaration']['signature_img'] = save_file(signature_file, sid)

        # Handle Internship files
        for entry in data.get('internship', []):
            if entry:
                internship_certificate_file = entry.get('internship_certificate')
                if internship_certificate_file:
                    entry['internship_certificate'] = save_file(internship_certificate_file, sid)

        # Handle Work Experience files
        if data.get('work_experience'):
            for entry in data.get('work_experience', []):
                work_experience_certificate_file = entry.get('work_experience_certificate')
                if work_experience_certificate_file:
                    entry['work_experience_certificate'] = save_file(work_experience_certificate_file, sid)

        # Handle Declaration signature file
        declaration_signature_file = data['declaration']['signature_img']
        if declaration_signature_file:
            data['declaration']['signature_img'] = save_file(declaration_signature_file, sid)

        # Handle Motivation Letter signature file
        motivation_letter_signature_file = data['motivation_letter']['signature_img']
        if motivation_letter_signature_file:
            data['motivation_letter']['signature_img'] = save_file(motivation_letter_signature_file, sid)

        # Save the modified data to MongoDB
        collection.insert_one(data)

        return jsonify({'message': 'Data stored successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getAllStudentsResume', methods=['GET'])
def get_all_students_resume():
    try:
        # Retrieve all students' resumes from MongoDB
        all_resumes = list(collection.find({}, {'_id': 0}))
        return jsonify({'resumes': all_resumes}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/getStudentLoginInfo', methods=['GET'])
def getStudentLoginInfo():
    try:
        students_db = db["students_db"]
        # Extracting common information
        sid = request.args.get('sid')

        data = students_db.find_one({"sid": sid}, {"_id": 0})
        if data:
            return jsonify({'message': 'Success',"data":data}), 200
        else:
            return jsonify({"message":"No Student fount with this sid"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500