import os
from flask import url_for, current_app
from flask_login import current_user
from PIL import Image
import smtplib
from email.mime.text import MIMEText

def save_picture(form_picture):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = current_user.username + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    # form_picture.save(picture_path)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def send_mail(subject, message, sender, password, recipient):
  try:
    # Body of E-mail
    email_body = MIMEText(message)
    # Subject of E-mail
    email_body['Subject'] = subject
    # Sender E-mail Id
    email_body['From'] = sender
    # Receiver E-mail Id
    email_body['To'] = recipient
    # SMTP Server
    server = smtplib.SMTP_SSL('smtppro.zoho.in', 465)
    # SMTP Server Login Credentials
    server.login(sender, password)
    # Gives Send Mail Request to SMTP Server
    server.sendmail(sender, recipient, email_body.as_string())
    # Quit or Logout from SMTP Server
    server.quit()
    print("email sent successfully")
  except:
    print("failed to send email")

def send_reset_email(user):
    token = user.get_reset_token()
    subject = "Reset Password Link"
    message = f'''To reset your password, visit the following
link: {url_for('user.reset_token', token=token, _external=True)}
If you did not make this request, then simply ignore this email and no changes will be made.
'''
    sender=os.environ.get('EMAIL_USER')
    password=os.environ.get('EMAIL_PASSWORD')
    print("sender of email => ", sender)
    send_mail(subject, message, sender, password, user.email)
    print("https://booklists.pythonanywhere.com" + url_for('user.reset_token', token=token))


