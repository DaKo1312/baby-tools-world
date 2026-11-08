from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list, name="products"),
    path("category/<slug:category_slug>/", views.product_list, name="products_by_category"),
    path("category/<slug:category_slug>/<int:pk>/", views.product_detail, name="product_detail"),
]
