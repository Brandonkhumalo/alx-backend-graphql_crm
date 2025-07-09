from celery import shared_task
import requests
import datetime

@shared_task
def generate_crm_report():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = "/tmp/crm_report_log.txt"

    query = '''
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    '''

    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': query},
            timeout=10
        )
        if response.ok:
            data = response.json().get('data', {})
            report_line = (
                f"{timestamp} - Report: {data.get('totalCustomers')} customers, "
                f"{data.get('totalOrders')} orders, "
                f"{data.get('totalRevenue')} revenue\n"
            )
        else:
            report_line = f"{timestamp} - ERROR {response.status_code}: {response.text}\n"
    except Exception as e:
        report_line = f"{timestamp} - Exception: {str(e)}\n"

    with open(log_path, "a") as f:
        f.write(report_line)
