#!/usr/bin/env python3

import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# GraphQL query
query = gql("""
query GetRecentOrders {
  orders(orderDate_Gte: "%s") {
    edges {
      node {
        id
        customer {
          email
        }
      }
    }
  }
}
""" % (datetime.datetime.now() - datetime.timedelta(days=7)).date().isoformat())

# Set up GraphQL client
transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql',
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Execute query
try:
    result = client.execute(query)
    for edge in result["orders"]["edges"]:
        order = edge["node"]
        logging.info(f"Order ID: {order['id']} - Customer Email: {order['customer']['email']}")
    print("Order reminders processed!")
except Exception as e:
    logging.error(f"Error while processing reminders: {e}")
    print("Failed to process order reminders.")
