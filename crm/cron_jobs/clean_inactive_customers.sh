#!/usr/bin/env bash

# This script deletes customers who have been inactive for over a year.
# It navigates to the Django root directory and runs cleanup using a Django shell command.

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Move to the Django project root (assumed two levels up)
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
cd "$PROJECT_ROOT" || exit 1

# Check current working directory
cwd=$(pwd)

# Use conditionals to ensure we're in the right directory before running the command
if [[ -f "manage.py" ]]; then
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

    # Log the output
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: \$deleted_count from \$cwd" >> /tmp/customer_cleanup_log.txt
else
    echo "Error: manage.py not found in \$cwd"
    exit 1
fi
