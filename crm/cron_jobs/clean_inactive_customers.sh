#!/bin/bash

# Navigate to the Django project root
cd "$(dirname "$0")/../.." || exit

# Run the customer cleanup logic
deleted_count=$(./manage.py shell <<EOF
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(last_order_date__lt=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log output with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $deleted_count" >> /tmp/customer_cleanup_log.txt
