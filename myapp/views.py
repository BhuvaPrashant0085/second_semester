from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Sample student data
students = {
    "230007002": {"name": "Prashant", "marks": 90, "email": "prashantbhuva085@gmail.com"},
    "230007001": {"name": "Rehan", "marks": 85, "email": "rehanramodiya666@gmail.com"}
}

def index(request):
    return render(request, 'index.html')


def send_email(request):
    if request.method == 'POST':
        enrollment_number = request.POST.get('enrollmentNumber')
        email = request.POST.get('email')

        # Debugging: Print the received values
        print(f"Received Enrollment Number: {enrollment_number}")
        print(f"Received Email: {email}")

        # If enrollment number is provided, check if it exists
        if enrollment_number:
            if enrollment_number in students:
                student = students[enrollment_number]
            else:
                return render(request, 'index.html', {'error': "Invalid Enrollment Number"})
        elif email:
            student = None
            for student_id, student_info in students.items():
                if student_info['email'] == email:
                    student = student_info
                    break
            if student is None:
                return render(request, 'index.html', {'error': "Invalid Email"})
        else:
            return render(request, 'index.html', {'error': "Please enter an enrollment number or email"})

        # Store student data in session
        request.session['student'] = student
        request.session['email'] = email

        # Generate random OTP
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        print(f"Generated OTP: {otp}")

        # Send email
        sender_email = "prashantbhuva085@gmail.com"
        receiver_email = email
        password = os.getenv('SMTP_PASSWORD')
        print("SMTP_PASSWORD:", os.getenv('SMTP_PASSWORD')) # Use environment variable

        if not password:
            return HttpResponse("SMTP password not set correctly. Please check your environment variable.")

        if not email:
            return render(request, 'index.html', {'error': "Email is required."})

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Your OTP for Verification"
        body = f"Your OTP is: {otp}"
        message.attach(MIMEText(body, "plain"))

        try:    
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            return render(request, 'verify_otp.html', {'email': email})
        except Exception as e:
            return HttpResponse(f"Failed to send email: {e}")

    return redirect('index')  # fallback



def verify_otp(request):
    email = request.session.get('email')
    student = request.session.get('student')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if int(entered_otp) == request.session.get('otp'):
            return render(request, 'student.html', {'email': email, 'student': student})
        else:
            return render(request, 'verify_otp.html', {'email': email, 'error': "Invalid OTP"})

    return render(request, 'verify_otp.html', {'email': email})
