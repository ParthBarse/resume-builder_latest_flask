from App import app, db, bcrypt, login_manager
from flask import request, jsonify
import smtplib
import os
# import imaplib
import email
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_file


# ================================================= Auth ================================================

UPLOAD_FOLDER = '/var/www/html/Renoadmin'
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