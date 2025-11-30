from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostSitemap

sitemaps = {
    'posts': PostSitemap,
}

urlpatterns = [
    path('', views.home, name='subscriptions-home'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('success/', views.success),
    path('cancel/', views.cancel),
    path('webhooks/stripe/', views.stripe_webhook, name="stripe-webhook"),
    path('billing-portal/', views.billing_portal, name="billing_portal"),
    path('about/', TemplateView.as_view(template_name="subscriptions/about.html"), name='about'),
    path('posts/', views.PostsView.as_view(), name='posts'),
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path('<slug:slug>/', views.post_detail, name="post_detail"),
]