from App import app, db, bcrypt, login_manager
from flask import request, jsonify
from pymongo import MongoClient
import smtplib
import os
import uuid
# import imaplib
import email
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file


# ================================================= Auth ================================================

UPLOAD_FOLDER = '/var/www/html/Resume_Builder'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
collection = db['your_collection_name']

# Directory to store files
file_directory = '/var/www/html/Resume_Files/'

def save_file(file, uid):
    filename = str(uuid.uuid4())  # Generate a unique filename using UUID
    file_path = os.path.join(file_directory, uid, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    return f'http://127.0.0.1/Resume_Files/{uid}/{filename}'

@app.route('/submitResume', methods=['POST'])
def submit_resume():
    try:
        data = request.json  # Parse JSON data

        # Extracting common information
        uid = data.get('uid')
        file_urls = {}

        # Handle candidate file
        candidate_file = request.files.get('candidate')
        if candidate_file:
            file_urls['candidate'] = save_file(candidate_file, uid)

        # Handle passport file
        passport_file = request.files.get('passport')
        if passport_file:
            file_urls['passport'] = save_file(passport_file, uid)

        # Handle German language files
        for entry in data.get('german', []):
            for module in ['listening_module', 'speaking_module', 'reading_module', 'writing_module']:
                file = entry.get(module)
                if file:
                    entry[module] = save_file(file, uid)

        # Handle Post Graduate, Under Graduate, Twelfth, Eleventh, Tenth, and First to Ninth files
        for category in ['post_graduate', 'under_graduate', 'twelweth', 'eleventh', 'tenth', 'first_to_ninth']:
            for entry in data.get(category, []):
                marksheet_file = entry.get('marksheet')
                if marksheet_file:
                    entry['marksheet'] = save_file(marksheet_file, uid)

        # Handle Blank Year files
        for entry in data.get('blank_year', []):
            reason_file = entry.get('reason_file')
            if reason_file:
                entry['reason_file'] = save_file(reason_file, uid)

        # Handle Language files
        signature_file = data['declaration']['signature_img']
        if signature_file:
            data['declaration']['signature_img'] = save_file(signature_file, uid)

        # Handle Internship files
        for entry in data.get('internship', []):
            internship_certificate_file = entry.get('internship_certificate')
            if internship_certificate_file:
                entry['internship_certificate'] = save_file(internship_certificate_file, uid)

        # Handle Work Experience files
        for entry in data.get('work_experience', []):
            work_experience_certificate_file = entry.get('work_experience_certificate')
            if work_experience_certificate_file:
                entry['work_experience_certificate'] = save_file(work_experience_certificate_file, uid)

        # Handle Declaration signature file
        declaration_signature_file = data['declaration']['signature_img']
        if declaration_signature_file:
            data['declaration']['signature_img'] = save_file(declaration_signature_file, uid)

        # Handle Motivation Letter signature file
        motivation_letter_signature_file = data['motivation_letter']['signature_img']
        if motivation_letter_signature_file:
            data['motivation_letter']['signature_img'] = save_file(motivation_letter_signature_file, uid)

        # Save the modified data to MongoDB
        collection.insert_one(data)

        return jsonify({'message': 'Data stored successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500