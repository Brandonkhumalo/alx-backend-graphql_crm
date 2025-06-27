import re
import graphene
from django.utils.timezone import now
from django.db import transaction
from graphene import Mutation, Field, List, String, Int, Decimal as GrapheneDecimal, ID
from .models import Customer, Product, Order
from .types import CustomerType, ProductType, OrderType
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

def is_valid_phone(phone):
    return re.match(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$", phone or "")

class CreateCustomer(Mutation):
    class Arguments:
        name = String(required=True)
        email = String(required=True)
        phone = String()

    customer = Field(CustomerType)
    message = String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        if phone and not is_valid_phone(phone):
            raise Exception("Invalid phone format.")
        customer = Customer(name=name, email=email, phone=phone or "")
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(Mutation):
    class CustomerInput(graphene.InputObjectType):
        name = String(required=True)
        email = String(required=True)
        phone = String()

    class Arguments:
        input = List(CustomerInput)

    customers = List(CustomerType)
    errors = List(String)

    def mutate(self, info, input):
        customers = []
        errors = []

        for index, data in enumerate(input):
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Email '{data.email}' already exists.")
                if data.phone and not is_valid_phone(data.phone):
                    raise Exception(f"Invalid phone format: {data.phone}")
                customer = Customer(name=data.name, email=data.email, phone=data.phone or "")
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(f"Entry {index + 1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(Mutation):
    class Arguments:
        name = String(required=True)
        price = GrapheneDecimal(required=True)
        stock = Int(required=False, default_value=0)

    product = Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be a positive number.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(Mutation):
    class Arguments:
        customer_id = ID(required=True)
        product_ids = List(ID, required=True)
        order_date = String(required=False)

    order = Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("At least one product must be selected.")

        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise Exception("One or more product IDs are invalid.")

        total = sum(p.price for p in products)

        order = Order(customer=customer, total_amount=total)
        if order_date:
            order.order_date = order_date
        order.save()
        order.products.set(products)

        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)