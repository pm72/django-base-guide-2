from django.db import models
from django.urls import reverse


class Category(models.Model):
  name = models.CharField(max_length=100, db_index=True)
  slug = models.SlugField(max_length=100, unique=True)


  class Meta:
    ordering =('name',)
    verbose_name = 'კატეგორია'
    verbose_name_plural = 'კატეგორიები'


  def __str__(self):
      return self.name
  

  def get_absolute_url(self):
    return reverse('main:product-list-by-category', args=[self.slug])


class Product(models.Model):
  category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
  name = models.CharField(max_length=100, db_index=True)
  slug = models.SlugField(max_length=100, unique=True)
  image = models.ImageField(upload_to='products/%Y/%m/%d/')
  description = models.TextField(blank=True)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  available = models.BooleanField(default=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)


  class Meta:
    ordering = ('name',)
    verbose_name = 'პროდუქტი'
    verbose_name_plural = 'პროდუქტები'


  def __str__(self):
    return self.name
  

  def get_absolute_url(self):
    return reverse('main:product-detail', args=[self.pk, self.slug])