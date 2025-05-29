import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration - hardcoded for reliability
EMAIL_SENDER = "vedanthh46@gmail.com"
EMAIL_PASSWORD = "zcfrdrpgxalygkrp"
ADMIN_EMAIL = "vedanthh46@gmail.com"

def send_email(to_email, subject, message):
    """
    Send an email using Gmail SMTP
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add message body
        msg.attach(MIMEText(message, 'html'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(0)  # Set to 1 for debugging
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        
        # Send email
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def send_registration_confirmation(user):
    """
    Send registration confirmation email to user
    """
    subject = "Welcome to Crisis Guardian - Registration Successful"
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-success {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 10px 0; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Welcome to Crisis Guardian!</h2>
            </div>
            <div class="content">
                <p>Hello {user.full_name},</p>
                <div class="alert-success">
                    <p>Your account has been successfully created with the username: <strong>{user.username}</strong></p>
                </div>
                <p>You can now log in to the Crisis Guardian system to report incidents and track their status.</p>
                <p>Thank you for registering with our crisis management system.</p>
                <a href="#" class="btn">Log In Now</a>
                <p>Best regards,<br>Crisis Guardian Team</p>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(user.email, subject, html)

def send_incident_report_notification(incident, reporter, notes=None):
    """
    Send incident report notification to user, admin, and rescue team
    """
    # Email to reporter
    subject = f"Incident Report Confirmation - #{incident.id}"
    
    notes_html = ""
    if notes:
        notes_html = f"<p><strong>Notes:</strong> {notes}</p>"
        
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-info {{ background-color: #e7f3fe; border-left: 4px solid #0066cc; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Incident Report Confirmation</h2>
            </div>
            <div class="content">
                <p>Hello {reporter.full_name},</p>
                <div class="alert-info">
                    <p>Your incident report has been successfully submitted with ID: <strong>#{incident.id}</strong></p>
                </div>
                
                <table>
                    <tr>
                        <th>Title</th>
                        <td>{incident.title}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>{incident.incident_type.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <th>Priority</th>
                        <td>{incident.priority.title()}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>{incident.status.replace('_', ' ').title()}</td>
                    </tr>
                </table>
                
                {notes_html}
                
                <p>You can track the status of your incident by logging into your account.</p>
                <p>Thank you for using Crisis Guardian.</p>
                <p>Best regards,<br>Crisis Guardian Team</p>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(reporter.email, subject, html)
    
    # Email to admin
    admin_subject = f"New Incident Reported - #{incident.id}"
    admin_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>New Incident Report</h2>
            </div>
            <div class="content">
                <div class="alert-warning">
                    <p>A new incident has been reported:</p>
                </div>
                
                <table>
                    <tr>
                        <th>ID</th>
                        <td>#{incident.id}</td>
                    </tr>
                    <tr>
                        <th>Title</th>
                        <td>{incident.title}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>{incident.incident_type.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <th>Priority</th>
                        <td>{incident.priority.title()}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>{incident.status.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <th>Reported By</th>
                        <td>{reporter.full_name} ({reporter.email})</td>
                    </tr>
                </table>
                
                {notes_html}
                
                <p>Please log in to the admin dashboard to review and assign this incident.</p>
                <a href="#" class="btn">Review Incident</a>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(ADMIN_EMAIL, admin_subject, admin_html)

def send_incident_assignment_notification(incident, team):
    """
    Send incident assignment notification to rescue team
    """
    subject = f"New Incident Assignment - #{incident.id}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>New Incident Assignment</h2>
            </div>
            <div class="content">
                <p>Hello {team.full_name},</p>
                <div class="alert-warning">
                    <p>You have been assigned to a new incident:</p>
                </div>
                
                <table>
                    <tr>
                        <th>ID</th>
                        <td>#{incident.id}</td>
                    </tr>
                    <tr>
                        <th>Title</th>
                        <td>{incident.title}</td>
                    </tr>
                    <tr>
                        <th>Type</th>
                        <td>{incident.incident_type.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <th>Priority</th>
                        <td>{incident.priority.title()}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>{incident.status.replace('_', ' ').title()}</td>
                    </tr>
                </table>
                
                <p>Please log in to your dashboard to view the details and take appropriate action.</p>
                <a href="#" class="btn">View Incident Details</a>
                <p>Best regards,<br>Crisis Guardian Team</p>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(team.email, subject, html)

def send_status_update_notification(incident, old_status, new_status, reporter, updater):
    """
    Send status update notification to user and admin
    """
    # Email to reporter
    subject = f"Incident Status Update - #{incident.id}"
    
    # Set status color based on new status
    status_style = "color: #0066cc;" # Default blue
    if new_status == 'resolved':
        status_style = "color: #28a745;" # Green
    elif new_status == 'rejected':
        status_style = "color: #dc3545;" # Red
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-info {{ background-color: #e7f3fe; border-left: 4px solid #0066cc; padding: 10px; margin: 10px 0; }}
            .alert-danger {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
            .status-rejected {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Incident Status Update</h2>
            </div>
            <div class="content">
                <p>Hello {reporter.full_name},</p>
                
                {('<div class="alert-danger"><p>Your incident report has been rejected. This may be due to insufficient information or it has been identified as a false report.</p></div>' if new_status == 'rejected' else '<div class="alert-info"><p>The status of your incident report has been updated:</p></div>')}
                
                <table>
                    <tr>
                        <th>ID</th>
                        <td>#{incident.id}</td>
                    </tr>
                    <tr>
                        <th>Title</th>
                        <td>{incident.title}</td>
                    </tr>
                    <tr>
                        <th>Status Change</th>
                        <td>{old_status.replace('_', ' ').title()} → <span style="{status_style}">{new_status.replace('_', ' ').title()}</span></td>
                    </tr>
                </table>
                
                <p>You can log in to your account to view the latest updates.</p>
                <a href="#" class="btn">View Incident Details</a>
                <p>Thank you for using Crisis Guardian.</p>
                <p>Best regards,<br>Crisis Guardian Team</p>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(reporter.email, subject, html)
    
    # Email to admin
    admin_subject = f"Incident Status Updated - #{incident.id}"
    admin_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; }}
            .alert-info {{ background-color: #e7f3fe; border-left: 4px solid #0066cc; padding: 10px; margin: 10px 0; }}
            .alert-danger {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .btn {{ display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
            .status-rejected {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Incident Status Update</h2>
            </div>
            <div class="content">
                {('<div class="alert-danger"><p>An incident has been rejected:</p></div>' if new_status == 'rejected' else '<div class="alert-info"><p>An incident status has been updated:</p></div>')}
                
                <table>
                    <tr>
                        <th>ID</th>
                        <td>#{incident.id}</td>
                    </tr>
                    <tr>
                        <th>Title</th>
                        <td>{incident.title}</td>
                    </tr>
                    <tr>
                        <th>Status Change</th>
                        <td>{old_status.replace('_', ' ').title()} → <span style="{status_style}">{new_status.replace('_', ' ').title()}</span></td>
                    </tr>
                    <tr>
                        <th>Updated By</th>
                        <td>{updater.full_name} ({updater.role})</td>
                    </tr>
                </table>
                
                <a href="#" class="btn">View Incident Details</a>
            </div>
            <div class="footer">
                <p>© 2025 Crisis Guardian. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(ADMIN_EMAIL, admin_subject, admin_html)