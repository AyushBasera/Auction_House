from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User,Listing,Comment,Bid


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    closed_listings = Listing.objects.filter(is_active=False)
    won_auctions=[]
    for listing in closed_listings:
        highest_bid = listing.bids.order_by("-amount").first()
        if highest_bid and highest_bid.user==request.user:
            won_auctions.append(listing)
    return render(request, "auctions/index.html",{
        "listings":active_listings,
        "won_listings":won_auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        title=request.POST.get("title")
        description=request.POST.get("description")
        starting_bid=request.POST.get("starting_bid")
        image_url=request.POST.get("image_url")
        category=request.POST.get("category")

        listing=Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            category=category,
            created_by=request.user
        )
        listing.save()
        return HttpResponseRedirect(reverse(index))
    
    return render(request,"auctions/create.html")

def listing(request,listing_id):
    listing=get_object_or_404(Listing,pk=listing_id)
    user = request.user
    in_watchlist=user.is_authenticated and listing in user.watchlist.all()
    highest_bid=listing.bids.order_by("-amount").first()
    is_creator=listing.created_by == user
    winner=highest_bid.user if highest_bid else None
    is_winner=winner==user
    comments=listing.comments.all().order_by("-created_at")

    message=None
    message_type=None
    #handling post requests for bid,watchlist_toggle,close auction,comment
    if request.method=='POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if 'place_bid' in request.POST:
            bid_amount=request.POST.get("bid")
            bid_amount=float(bid_amount)
            current_price=listing.current_price
            try:
                if bid_amount<=current_price:
                    message="Amount of the bid must be higher then current Price "
                    message_type="error"
                    # messages.error(request,"Amount of the bid must be higher then current Price ")
                    # return HttpResponseRedirect(reverse("listing",args=[listing.id]))
                else:
                    bid=Bid(user=user,listing=listing,amount=bid_amount)
                    bid.save()
                    message="Bid saved successfully"
                    message_type="success"
                    # messages.success(request,"Bid saved successfully")
                    # return HttpResponseRedirect(reverse("listing",args=[listing.id]))
            except:
                message="Invalid Bid"
                message_type="error"
                # return HttpResponseRedirect(reverse("listing",args=[listing.id]))
        elif 'watchlist_toggle' in request.POST:
            if in_watchlist:
                user.watchlist.remove(listing)
                message="Item removed from the watchList"
                message_type="info"
            else:
                user.watchlist.add(listing)
                message="Item added to the watchlist"
                message_type="success"
            in_watchlist=not in_watchlist
            # return HttpResponseRedirect(reverse("listing",args=[listing.id]))
        elif 'close_auction' in request.POST:
            listing.is_active=False
            listing.save()
            message="Auction closed Successfully"
            message_type="success"
            # return HttpResponseRedirect(reverse("listing",args=[listing.id]))
        elif 'comment_submit' in request.POST:
            content=request.POST.get("comment")
            if content:
                comment=Comment(user=user,listing=listing,content=content)
                comment.save()
                message="Comment saved Successfully"
                message_type="success"
            # return HttpResponseRedirect(reverse("listing",args=[listing.id]))



    return render(request,"auctions/listing.html",{
        "listing":listing,
        "in_watchlist":in_watchlist,
        "highest_bid":highest_bid,
        "is_creator":is_creator,
        "winner":winner if not listing.is_active else None,
        "is_winner":is_winner,
        "comments":comments,
        "message":message,
        "message_type":message_type
    })

def watchlist(request,user_id):
    all_listings=request.user.watchlist.all()
    return render(request,"auctions/watchlist.html",{
        "all_listings":all_listings
    })

def categories(request):
    active_listings = Listing.objects.filter(is_active=True)
    all_categories=[]
    for listing in active_listings:
        curr_category=listing.category
        if curr_category and curr_category not in all_categories:
            all_categories.append(curr_category)
    
    return render(request,"auctions/categories.html",{
        "all_categories":all_categories
    })

def category(request,category_name):
    active_listings = Listing.objects.filter(is_active=True)
    listing_of_this_category=[]
    for listing in active_listings:
        if listing.category==category_name:
            listing_of_this_category.append(listing)

    return render(request,"auctions/category.html",{
        "listings":listing_of_this_category,
        "category":category_name
    })