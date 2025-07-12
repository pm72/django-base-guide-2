from django.shortcuts import redirect, render, get_object_or_404

from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from django.views.decorators.http import require_POST


# ===== VIEW 1: კალათაში დამატება =====
@require_POST
def cart_add(request, product_id):
    '''
    პროდუქტის კალათში დამატება.
    
    :param
    -- request: HTTP მოთხოვნა,
    -- product_id: პროდუქტის ID

    მუშაობს მხოლოდ POST მეთოდით.
    GET, PUT, DELETE მეთოდები არ მუშაობს (შეცდომა 405 -- Method Not Allowed).
    '''

    # კალათის ობიექტის შექმნა, რომელიც იღებს HTTP მოთხოვნას
    cart = Cart(request)

    # პროდუქტის ID-ით პროდუქტის ობიექტის მიღება
    product = get_object_or_404(Product, id=product_id)
    
    # CartAddProductForm-ის შექმნა, რომელიც იღებს POST მონაცემებს
    form = CartAddProductForm(request.POST)

    if form.is_valid():
      cd = form.cleaned_data  # ვალიდური მონაცემები: {'quantity': 1, 'override': False}

      # კალათში პროდუქტის დამატება
      cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])
    
    # კალათის გვერდზე გადამისამართება
    return redirect('cart:cart-detail')     # cart-detail შესაქმნელია


# ===== VIEW 2: კალათიდან წაშლა =====
@require_POST
def cart_remove(request, product_id):
    '''
    პროდუქტის კალათიდან წაშლა.
    
    :param
    -- request: HTTP მოთხოვნა,
    -- product_id: პროდუქტის ID

    მუშაობს მხოლოდ POST მეთოდით.
    GET, PUT, DELETE მეთოდები არ მუშაობს (შეცდომა 405 -- Method Not Allowed).
    '''

    # კალათის ობიექტის შექმნა, რომელიც იღებს HTTP მოთხოვნას
    cart = Cart(request)

    # პროდუქტის ID-ით პროდუქტის ობიექტის მიღება
    product = get_object_or_404(Product, id=product_id)

    # კალათიდან პროდუქტის წაშლა
    cart.remove(product)
    
    # კალათის გვერდზე გადამისამართება
    return redirect('cart:cart-detail')   # cart-detail შესაქმნელია


# ===== VIEW 3: კალათის დეტალები =====
def cart_detail(request):
    '''
    კალათის დეტალების ჩვენება.
    
    :param request: HTTP მოთხოვნა GET მეთოდით.
    '''

    # კალათის ობიექტის შექმნა, რომელიც იღებს HTTP მოთხოვნას
    cart = Cart(request)

    for item in cart:
      item['update_quantity_form'] = CartAddProductForm(initial={
        'quantity': item['quantity'],
        'override': True,
      })
    
    context = {
      'cart': cart,
    }

    return render(request, 'cart/cart_detail.html', context)