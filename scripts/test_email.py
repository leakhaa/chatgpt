import os
import sys

# Add the parent directory to sys.path (this allows imports to work)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.email_handler_part2 import send_email

# Test
send_email("leakhaganesh@gmail.com", "Test Subject", "This is a test email body.")
