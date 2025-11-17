from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='subscriptions-home'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.success),
    path('cancel/', views.cancel),
    path('webhook/', views.stripe_webhook),
    path("billing-portal/", views.billing_portal, name="billing_portal"),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about'),
    path('posts/', views.PostsView.as_view(), name='posts'),
]