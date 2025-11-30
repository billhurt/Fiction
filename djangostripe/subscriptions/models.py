from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.

class StripeCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
    

class Post(models.Model):
    """Model representing a blog post."""
    # one to many
    title = models.CharField(max_length=100, help_text="Enter a title for your blog post.")
    slug = models.SlugField(max_length=200, unique=True)
    sub_title = models.CharField(max_length=100, blank=True, help_text="Enter a sub-title for your blog post.")
    content = models.TextField(max_length=100000, help_text="Enter the content of your blog post here.", unique=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="The time at which your post was created.")
    updated_at = models.DateTimeField(auto_now_add=True, help_text="The last time your blog post was updated.")

    class Meta:
        ordering = ['updated_at']

    def __str__(self):
        """Return a string for the Post object"""
        return self.title

    def get_absolute_url(self):
        """Returns a URL to access the detail record for this particular post."""
        return reverse("blog:post_detail", args=[str(self.slug)])