from django.urls import path,include
from django.contrib import admin

from . import views

urlpatterns = [
    path("admin",admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.create_listing,name="create"),
    path("listing/<int:listing_id>",views.listing,name="listing"),
    path("watchlist/<int:user_id>",views.watchlist,name="watchlist"),
    path("categories",views.categories,name="categories"),
    path("categories/<str:category_name>",views.category,name="category")
]
