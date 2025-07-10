import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    try:
        query = gql('{ hello }')
        result = client.execute(query)
        if 'hello' in result:
            message = f"{timestamp} CRM is alive (GraphQL OK: {result['hello']})\n"
        else:
            message = f"{timestamp} CRM is alive (GraphQL RESPONSE ERROR)\n"
    except Exception:
        message = f"{timestamp} CRM is alive (GraphQL TIMEOUT)\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)


def update_low_stock():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = "/tmp/low_stock_updates_log.txt"

    mutation = '''
    mutation {
        updateLowStockProducts {
            message
            updatedProducts {
                name
                stock
            }
        }
    }
    '''

    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            timeout=10
        )
        if response.ok:
            data = response.json().get('data', {}).get('updateLowStockProducts', {})
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} - {data.get('message')}\n")
                for product in data.get('updatedProducts', []):
                    log_file.write(f"→ {product['name']} stock: {product['stock']}\n")
        else:
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} - GraphQL ERROR {response.status_code}: {response.text}\n")
    except Exception as e:
        with open(log_path, 'a') as log_file:
            log_file.write(f"{timestamp} - Exception occurred: {str(e)}\n")

'''
    Add and Run the Cron Job
    Register the cron job with Django:
    python manage.py crontab add
    Confirm it's working:
    python manage.py crontab show
'''
