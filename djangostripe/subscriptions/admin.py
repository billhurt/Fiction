from django.contrib import admin
from subscriptions.models import StripeCustomer, Post

# Register your models here.

admin.site.register(StripeCustomer)
admin.site.register(Post)