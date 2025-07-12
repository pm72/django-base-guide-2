from django.shortcuts import get_object_or_404, render

from .models import Category, Product
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    category = None

    if category_slug:
      category = get_object_or_404(Category, slug=category_slug)
      products = products.filter(category=category)
    
    # სორტირება
    sort = request.GET.get('sort')

    if sort in ('name', '-name', 'price', '-price'):
      products = products.order_by(sort)

    context = {
      'categories': categories,
      'products': products,
      'category': category,
      'current_sort': sort,
    }

    return render(request, 'main/products/list.html', context)


def product_detail(request, pk, slug):
  product = get_object_or_404(Product, pk=pk, slug=slug, available=True)
  related_products = Product.objects.filter(category=product.category, available=True).exclude(pk=product.pk)[:4]

  cart_product_form = CartAddProductForm()

  context = {
    'product': product,
    'related_products': related_products,
    'cart_product_form': cart_product_form,
  }

  return render(request, 'main/products/detail.html', context)