from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
  path('', views.product_list, name='product-list'),
  path('<slug:category_slug>/', views.product_list, name='product-list-by-category'),
  path('<int:pk>/<slug:slug>/', views.product_detail, name='product-detail'),
]