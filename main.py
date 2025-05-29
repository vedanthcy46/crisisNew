# Monkey patch for safe_str_cmp
import hmac
import sys

# Add the safe_str_cmp function to werkzeug.security
import werkzeug.security
if not hasattr(werkzeug.security, 'safe_str_cmp'):
    werkzeug.security.safe_str_cmp = lambda a, b: hmac.compare_digest(a, b)

from app import app

if __name__ == '__main__':
    app.run(debug=True)