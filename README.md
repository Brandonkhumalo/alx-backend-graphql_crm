# 🛒 Django GraphQL CRM

A simple **Customer Relationship Management (CRM) system** built with **Django** and **GraphQL**.  
This project manages **Customers, Products, and Orders** with GraphQL queries & mutations, and includes features like:

- Customer management (single & bulk creation)
- Product management (with stock updates & validation)
- Order creation & revenue tracking
- Low-stock product auto-restocking
- Scheduled scripts for CRM health checks and order reminders

---

## 📌 Features

### Customers
- Create single or multiple customers via GraphQL mutations
- Validates unique emails and phone number formats
- Query customers with filters

### Products
- Add products with name, price, and stock
- Validate stock and price values
- Auto-restock products when stock < 10

### Orders
- Place orders for a customer with multiple products
- Automatically calculate total amount
- Track order history and revenue

### Analytics
- Get **total customers, total orders, and total revenue**
- Query all entities with filtering support

### Automation Scripts
- **Heartbeat logger**: checks if GraphQL API is alive and logs status  
- **Low stock updater**: automatically restocks products when stock is low  
- **Order reminders**: logs recent orders from the last 7 days  

---

## ⚙️ Tech Stack

- **Backend**: Django + Graphene-Django (GraphQL)
- **Database**: SQLite (default) / PostgreSQL (recommended)
- **GraphQL Client**: gql (Python GraphQL client)
- **Task Scheduling**: Custom scripts (Celery)
