import re
import graphene
from django.utils.timezone import now
from django.db import transaction
from graphene import Mutation, Field
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from django.db.models import Sum
from .models import Customer, Product, Order
from .types import CustomerType, ProductType, OrderType
from .filters import CustomerFilter, ProductFilter, OrderFilter


def is_valid_phone(phone):
    return re.match(r"^(\+?\d{10,15}|\d{3}-\d{3}-\d{4})$", phone or "")


# Define CustomerInput outside mutation for better IDE support
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists.")
        if phone and not is_valid_phone(phone):
            raise Exception("Invalid phone format.")
        customer = Customer(name=name, email=email, phone=phone or "")
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

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


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be a positive number.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.String(required=False)

    order = graphene.Field(OrderType)

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
            order.order_date = order_date  # Consider parsing if needed
        order.save()
        order.products.set(products)

        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)
        return UpdateLowStockProducts(
            updated_products=updated_products,
            message=f"{len(updated_products)} product(s) restocked successfully."
        )


class Query(graphene.ObjectType):
    total_customers = graphene.Int()
    total_orders = graphene.Int()
    total_revenue = graphene.Float()

    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_total_customers(root, info):
        return Customer.objects.count()

    def resolve_total_orders(root, info):
        return Order.objects.count()

    def resolve_total_revenue(root, info):
        return Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0.0


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
