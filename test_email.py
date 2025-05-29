from email_utils import send_email

# Test email with simple UI
subject = "Test Email with Simple UI"
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .header { background-color: #0066cc; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; margin-bottom: 20px; }
        .footer { background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; margin-top: 20px; }
        .content { padding: 0 15px; }
        .btn { display: inline-block; background-color: #0066cc; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 3px; }
        .alert-info { background-color: #e7f3fe; border-left: 4px solid #0066cc; }
        .alert-success { background-color: #d4edda; border-left: 4px solid #28a745; }
        .alert-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Crisis Guardian Test</h2>
        </div>
        <div class="content">
            <p>Hello there,</p>

            <div class="alert alert-info">
                <p>This is a test email with the new UI template.</p>
            </div>

            <table>
                <tr>
                    <th>Item</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Test Item 1</td>
                    <td>Value 1</td>
                </tr>
                <tr>
                    <td>Test Item 2</td>
                    <td>Value 2</td>
                </tr>
            </table>

            <p>This is a <a href="#" class="btn">Test Button</a></p>

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

result = send_email("vedanthh46@gmail.com", subject, html_content)
print(f"Email sent: {result}")