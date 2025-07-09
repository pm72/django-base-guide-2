from django.conf import settings
from main.models import Product
from decimal import Decimal


class Cart:
  def __init__(self, request):
    '''
    კალათის ინიციალიზაცია

    პარამეტრები:
    – request: Django HTTP request მოთხოვნა

    ნაბიჯები:
    1. სესიის მიღება request-დან
    2. კალათის მონაცემების მიღება სესიისგან
    3. თუ კალათის მონაცემები არ არსებობს, შექმენით ცარიელი კალათი – dictionary
    '''

    # მომხობელის სესიის მიღება
    self.session = request.session

    # კალათის მონაცემების მიღება სესიისგან
    # CART_SESSION_ID – კალათის კლასი სესიაში (მაგ.: 'cart')
    cart = self.session.get(settings.CART_SESSION_ID)

    # თუ კალათის მონაცემები არ არსებობს, შექმენით ცარიელი კალათი
    if not cart:
      cart = self.session[settings.CART_SESSION_ID] = {}  # ცარიელი კალათი
    
    '''მაგალითი:
    # პირველი ვიზიტი
    cart = Cart(request)  # self.cart = {}

    # მეორე ვიზიტი
    cart = Cart(request)  # self.cart = {'5': {'quantity': 2 'price': '25.50'}}
    '''
  

  def add(self, product, quantity=1, override_quantity=False):
    '''
    პროდუქტის კალათში დამატება ან რაოდენობის შეცვლა

    პარამეტრები:
    – product: პროდუქტის ობიექტი
    – quantity: რაოდენობა (ნაგულისხმევია 1)
    – update_quantity: თუ True, განაახლებს რაოდენობას, თუ False, დაამატებს ახალ პროდუქტს

    ნაბიჯები:
    1. product_id = str(product.id) – ID-ს სტრიქონად გარდაქმნა (სესია მხოლოდ JSON serializable მონაცემებს ინახავს)
    2. ახალი პროდუქტის შემთხვევაში ლექსიკონის (dictionary) შექმნა
    3. რაოდენობის მართვა: დამატება ან განახლება
    '''

    product_id = str(product.id)  # ID-ს სტრიქონად გარდაქმნა

    if product_id not in self.cart:
      self.cart[product_id] = {
        'quantity': 0,
        'price': str(product.price)
      }
    
    if override_quantity:
      self.cart[product_id]['quantity'] = quantity
    else:
      self.cart[product_id]['quantity'] += quantity
    
    self.save()  # კალათის შენახვა სესიაში

    '''მაგალითები:

    # პროდუქტის დამატება კალათში
    cart.add(product, quantity=3)
    # Result: {'5': {'quantity': 3, 'price': '25.50'}}

    # რაოდენობის გაზრდა
    cart.add(product, quantity=2)
    # Result: {'5': {'quantity': 5, 'price': '25.50'}}

    # რაოდენობის ჩანაცვლება
    cart.add(product, quantity=2, override_quantity=True)
    # Result: {'5': {'quantity': 2, 'price': '25.50'}}
    '''
  
  def remove(self, product):
    '''
    პროდუქტის კალათიდან წაშლა

    ნაბიჯები:
    1. product_id = str(product.id) – ID-ს სტრიქონად გარდაქმნა
    2. კალათაში პროდუქტის არსებობის შემოწმება
    3. პროდუქტის წაშლა კალათიდან
    4. კალათის შენახვა სესიაში
    '''

    product_id = str(product.id)
    
    if product_id in self.cart:
      del self.cart[product_id]  # პროდუქტის წაშლა კალათიდან
    
      self.save()  # კალათის შენახვა სესიაში
    
    '''მაგალითი:
    # პროდუქტის წაშლამდე
    # self.cart = {'5': {'quantity': 3, 'price': '25.50'}, '8': {'quantity': 1, 'price': '15.00'}}
    cart.remove(product) # product_id = '5'

    # პროდუქტის წაშლის შემდეგ
    # self.cart = {'8': {'quantity': 1, 'price': '15.00'}}
    '''
  
  def save(self):
    '''
    სესიაში ცვლილებების შენახვა

    მნიშვნელობა:
    * self.session.modified = True – ჯანგოს ეუბნება, რომ სესიის მონაცემები შეიცვალა და საჭიროა შენახვა
    * ამის გარეშე ჯანგომ შეიძლება არ შეინახოს ცვლილებები
    * save() მეთოდი ყოველი add, remove, clear ოპერაციის შემდეგ უნდა გამოიძახოს
    '''

    self.session.modified = True  # სესიის შენახვა
    
    '''მაგალითი:
    # save() მეთოდის გარეშე
    self.cart['5']['quantity'] = 10  # შეიძლება არ შეინახოს

    # save() მეთოდის გამოყენება
    self.cart['5']['quantity'] = 10
    self.save()  # სესიის შენახვა 100%-ით
    '''
  
  def __iter__(self):
    '''
    კალათის ელემენტებზე ციკლით გავლის შესაძლებლობა
    '''

    product_ids = self.cart.keys()  # პროდუქტის ID-ების მიღება
    products = Product.objects.filter(id__in=product_ids)  # პროდუქტის ობიექტების მიღება
    cart = self.cart.copy()  # კალათის ასლის შექმნა

    for product in products:
      cart[str(product.id)]['product'] = product  # პროდუქტის ობიექტის დამატება კალათში
    
    for item in cart.values():
      item['price'] = Decimal(item['price'])  # ფასის Decimal ტიპად გარდაქმნა
      item['total_price'] = item['price'] * item['quantity']  # ჯამური ფასი
      
      yield item  # ელემენტის დაბრუნება
    
    '''მაგალითი:
    
    # კალათის ელემენტებზე ციკლით გავლა
    for item in cart:
      print(f"Product: {item['product'].name}")
      print(f"Quantity: {item['quantity']}")
      print(f"Price: {item['price']}")
      print(f"Total Price: {item['total_price']}")
    
    # იტერაციის შედეგი:
    {
      'product': Product(id=5, name='Laptop'),
      'quantity': 2,
      'price': Decimal('25.50'),
      'total_price': Decimal('51.00')
    }
    '''

  
  def __len__(self):
    '''
    კალათში არსებული პროდუქტის რაოდენობის გამოთვლა

    ფორმულა:
    return sum(item['quantity'] for item in self.cart.values()) – ყველა პროდუქტის რაოდენობის ჯამი
    '''

    return sum(item['quantity'] for item in self.cart.values())  # კალათის სიგრძე
    
    '''მაგალითი:
    
    self.cart = {
      '5': {'quantity': 2, 'price': '25.50'},
      '8': {'quantity': 1, 'price': '15.00'}
    }
    
    print(len(cart))  # შედეგი: 3 (2 + 1)
    '''


  def get_total_price(self):
    '''
    კალათში არსებული პროდუქტის ჯამური ფასი

    ფორმულა:
    return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values()) – ყველა პროდუქტის ფასისა და რაოდენობის ჯამი
    '''

    return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())  # ჯამური ფასი
    
    '''მაგალითი:
    
    self.cart = {
      '5': {'quantity': 2, 'price': '25.50'},
      '8': {'quantity': 1, 'price': '15.00'}
    }
    
    print(cart.get_total_price())  # შედეგი: Decimal('66.00') (2 * 25.50 + 1 * 15.00)
    '''


  def clear(self):
    '''
    კალათის გასუფთავება
    '''

    del self.session[settings.CART_SESSION_ID] = {}  # კალათის გასუფთავება
    self.save()  # სესიის შენახვა
    
    '''მაგალითი:
    
    # გასუფთავებამდე
    self.cart = {
      '5': {'quantity': 2, 'price': '25.50'},
      '8': {'quantity': 1, 'price': '15.00'}
    }

    # კალათის გასუფთავება
    cart.clear()
    
    # შედეგი: self.cart = {}
    '''