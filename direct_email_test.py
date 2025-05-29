import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
EMAIL_SENDER = "vedanthh46@gmail.com"
EMAIL_PASSWORD = "zcfrdrpgxalygkrp"
TO_EMAIL = "vedanthh46@gmail.com"

# Create message
msg = MIMEMultipart()
msg['From'] = EMAIL_SENDER
msg['To'] = TO_EMAIL
msg['Subject'] = "Direct Test Email"

# Simple HTML content
html = """
<html>
<body>
    <h2 style="color: #0066cc;">Test Email</h2>
    <p>This is a direct test email to verify SMTP functionality.</p>
    <p>If you receive this, the email system is working correctly.</p>
</body>
</html>
"""

msg.attach(MIMEText(html, 'html'))

try:
    # Connect directly to Gmail SMTP
    print("Connecting to SMTP server...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)  # Show debug output
    server.ehlo()
    print("Starting TLS...")
    server.starttls()
    server.ehlo()
    print("Logging in...")
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    
    # Send email
    print("Sending email...")
    server.sendmail(EMAIL_SENDER, TO_EMAIL, msg.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {str(e)}")