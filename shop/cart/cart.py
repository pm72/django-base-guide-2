from django.conf import settings
from main.models import Product
from decimal import Decimal


class Cart:
  def __init__(self, request):
    '''
    კალათის ინიციალიზაცია, რომელიც იღებს HTTP მოთხოვნას.
    '''

    # სესიის მიღება request ობიექტიდან
    # request.session – სესიის ობიექტი, რომელიც შეიცავს მომხმარებლის კალათის მონაცემებს
    self.session = request.session

    # კალათის მონაცემების მიღება სესიიდან
    # settings.CART_SESSION_ID – კალათის კლასი სესიაში (მაგ.: 'cart')
    cart = self.session.get(settings.CART_SESSION_ID)

    # თუ კალათა არ არსებობს, შექმენით ცარიელი კალათა
    if not cart:
      cart = self.session[settings.CART_SESSION_ID] = {}
    
    self.cart = cart
  

  def add(self, product, quantity=1, override_quantity=False):
    '''
    პროდუქტის კალათში დამატება ან რაოდენობის შეცვლა.
    '''

    # product_id სტრიქონი: JSON serializable ფორმატში
    product_id = str(product.id)

    if product_id not in self.cart: 
      # პროდუქტი კალათში არ არსებობს, დაამატეთ ის
      self.cart[product_id] = {
        'quantity': 0,
        'price': str(product.price),
      }
    
    if override_quantity:
      # თუ override_quantity True-ია, შეცვალეთ რაოდენობა
      self.cart[product_id]['quantity'] = quantity
    else:
      # თუ override_quantity False-ია, დაამატეთ რაოდენობა
      self.cart[product_id]['quantity'] += quantity
    
    # კალათის მონაცემების განახლება / შენახვა სესიაში
    self.save()


  def remove(self, product):
    '''
    პროდუქტის კალათიდან წაშლა.
    '''
    
    product_id = str(product.id)
    if product_id in self.cart:
      del self.cart[product_id]
      
      self.save()


  def save(self):
    '''
    კალათის მონაცემების სესიაში შენახვა.
    
    save() მეთოდი ყოველი add, remove, clear ოპერაციის შემდეგ გამოიძახება, წინააღმდეგ შემთხვევაში django-მ შეიძლება ცვლილებები არ შეინახოს.
    '''

    self.session.modified = True
  

  def __iter__(self):
    '''
    კალათის ელემენტებზე ციკლით გავლის შესაძლებლობა.
    '''

    # პროდუქტების ID-ების მიღება კალათიდან
    product_ids = self.cart.keys()

    # პროდუქტების ბაზიდან მიღება
    products = Product.objects.filter(id__in=product_ids)

    # კალათის ასლი, რათა სესიაში ცვლილებები არ მოხდეს
    cart = self.cart.copy()

    # პროდუქტების ობიექტების დამატება ლექსიკონში სახელად cart
    for product in products:
      cart[str(product.id)]['product'] = product
    
    for item in cart.values():
      item['price'] = Decimal(item['price'])
      item['total_price'] = item['price'] * item['quantity']
      
      yield item
  

  def __len__(self):
    '''
    კალათში არსებული პროდუქტების რაოდენობის გამოთვლა.
    '''

    return sum(item['quantity'] for item in self.cart.values())
  

  def get_total_price(self):
    '''
    კალათში არსებული პროდუქტების ჯამური ფასი.
    '''

    return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
  

  def clear(self):
    '''
    კალათის სრულად გასუფთავება.
    '''

    # კალათის მონაცემების წაშლა სესიიდან
    del self.session[settings.CART_SESSION_ID]
    
    # სესიის განახლება
    self.save()