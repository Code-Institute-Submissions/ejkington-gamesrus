from django.db import models
import uuid
from django.db.models import Sum
from django.conf import settings
from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=30, null=False, editable=False)
    full_name = models.CharField(max_length=40, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    country = models.CharField(max_length=50, null=False, blank=False)
    postcode = models.CharField(max_length=10, null=False, blank=False)
    town_or_city = models.CharField(max_length=50, null=False, blank=False)
    street_adress1 = models.CharField(max_length=50, null=False, blank=False)
    street_adress2 = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=15, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, null=False, default=0)

    def _generate_order_number(self):
        """ generate random unique order number """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kvargs):
        """ Overides the defaul save method """
        if not self.order_number:
            self.order_number = self._generate_order_number()
            super().save(*args, **kwargs)
            
    def __str__(self):
        return self.order_number

    def update_total(self):
        """ update grand total each time a line item is added taking delivery cost in considiration """
        self.order_total = self.lineitems.aggregate(sum('lineitem_total'))['lineitem_total__sum']
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.deliver_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kvargs):
        """ Overides the defaul save method to update order total """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'