import stripe
import time
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from functools import wraps
from .models import Post

from subscriptions.models import StripeCustomer

# Create your views here.

def home(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    subscription = None
    product = None
    has_access = False

    if not request.user.is_authenticated:
        return render(request, "subscriptions/home.html", {
            "subscription": None,
            "product": None,
            "has_access": False,
        })

    try:
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        subscription = stripe.Subscription.retrieve(
            stripe_customer.stripeSubscriptionId
        )

        if subscription.plan:
            product = stripe.Product.retrieve(subscription.plan.product)

        current_timestamp = int(time.time())
        if subscription.status == "active":
            has_access = True
        elif (
            subscription.status == "canceled"
            and subscription.current_period_end > current_timestamp
        ):
            has_access = True

    except StripeCustomer.DoesNotExist:
        pass
    except Exception as e:
        print("Stripe error:", e)

    return render(request, "subscriptions/home.html", {
        "subscription": subscription,
        "product": product,
        "has_access": has_access,
    })



@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@login_required
@csrf_exempt
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    domain_url = 'http://localhost:8000/'

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id,
            success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + 'cancel/',
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{'price': settings.STRIPE_PRICE_ID, 'quantity': 1}],
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def success(request):
    return render(request, 'subscriptions/success.html')


@login_required
def cancel(request):
    return render(request, 'subscriptions/cancel.html')


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if sig_header is None:
        return HttpResponse(status=400)

    # Verify the event
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return HttpResponse(status=400)

    # Handle checkout completion
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # User who paid
        client_reference_id = session.get("client_reference_id")

        # Stripe customer ID
        customer_id = session.get("customer")

        # Subscription ID — NEW SAFE METHOD
        subscription_id = (
            session.get("subscription")
            or session.get("latest_invoice", {}).get("subscription")
        )

        print("Webhook session:", session)
        print("Subscription ID found:", subscription_id)

        # Protect against missing data
        if not (client_reference_id and customer_id and subscription_id):
            print("Missing required data. Webhook aborted.")
            return HttpResponse(status=200)

        # Create StripeCustomer record
        user = User.objects.get(id=client_reference_id)
        StripeCustomer.objects.update_or_create(
            user=user,
            defaults={
                "stripeCustomerId": customer_id,
                "stripeSubscriptionId": subscription_id,
            }
        )
        print(f"{user.username} subscribed successfully.")

    return HttpResponse(status=200)



@login_required
def billing_portal(request):
    stripe_customer = StripeCustomer.objects.get(user=request.user)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    customer_id = stripe_customer.stripeCustomerId

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=request.build_absolute_uri("/")
    )
    return redirect(session.url)


class PostsView(generic.ListView):
    model = Post
    template_name = "subscriptions/posts.html"
    context_object_name = "latest_blog_posts"
    paginate_by = 10

    def get_queryset(self):
        """Return the last fifty blog posts."""
        return Post.objects.order_by("-created_at")
    

def chunk_text(text, size=2000):
    return [text[i:i+size] for i in range(0, len(text), size)]


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)

    subscription = None

    try:
        stripe_customer = StripeCustomer.objects.get(user=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
    except Exception:
        subscription = None

    chunks = chunk_text(post.content, 4000)
    paginator = Paginator(chunks, 1)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "subscriptions/post_detail.html", {
        "post": post,
        "page_obj": page_obj,
        "subscription": subscription,
    })

