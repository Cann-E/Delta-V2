import os
import django

# Set up Django environment (update path to match your settings file)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delta.settings')  
django.setup()

# Now import models
from delta.models import Request

# Fetch all requests that are NOT "pending"
requests_to_update = Request.objects.exclude(status="pending")

if requests_to_update.exists():
    # Update all found requests to "pending"
    count = requests_to_update.update(status="pending")
    
    print(f"🔄 {count} request(s) have been changed to Pending.")
else:
    # Handle the case where all requests are already pending
    print("✅ No requests found that need to be changed to Pending.")
