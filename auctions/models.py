from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watchlist=models.ManyToManyField('Listing',blank=True,related_name="watchlisted_by")

class Listing(models.Model):
    title=models.CharField(max_length=60)
    description=models.TextField()
    starting_bid=models.DecimalField(max_digits=10, decimal_places=2)
    image_url=models.URLField(blank=True,null=True)
    category=models.CharField(max_length=60,blank=True,null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='listings')

    def __str__(self):
        return f"{self.title}"
    @property
    def current_price(self):
        highest=self.bids.order_by('-amount').first()
        return highest.amount if highest else self.starting_bid

class Bid(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    listing=models.ForeignKey('Listing',on_delete=models.CASCADE,related_name="bids")
    amount=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.user.username} bids Rs. {self.amount} on {self.listing}"

class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    listing=models.ForeignKey('Listing',on_delete=models.CASCADE,related_name="comments")
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"comment by {self.user.username} on {self.listing}"


