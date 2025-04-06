import os
import django

# Set up Django environment (update path to match your settings file)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delta.settings')  
django.setup()

# Now import models and utilities
from delta.models import Request
from delta.pdf_utils import generate_pdf_for_request

# Fetch the first request with a status of "pending"
req = Request.objects.filter(status="pending").first()

if req:
    # Update the request status to "approved"
    req.status = "approved"
    req.save()

    # Generate a PDF for the approved request
    pdf_path = generate_pdf_for_request(req)
    print(f"✅ PDF Generated: {pdf_path}")
else:
    # Handle the case where no pending requests are found
    print("❌ No pending requests found!")
