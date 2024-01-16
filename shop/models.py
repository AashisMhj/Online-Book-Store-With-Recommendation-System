from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg, Sum, F, ExpressionWrapper, FloatField, Subquery

class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True ,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True )
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    thumbnail = models.ImageField(upload_to='products/thumbnails', blank=True)
    author = models.CharField(max_length=50,db_index=True,default='Author_Name')
    publisher = models.CharField(max_length=50,db_index=True,default='Publisher_Name')
    isbn_no = models.CharField(max_length=50,db_index=True,default='isbn_no')

    class Meta:
        ordering = ('name', )
        index_together = (('id', 'slug'),)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])
    
    @property
    def weighted_score(self, weight_rating=0.7, weight_orders=0.3):
        avg_rating = self.rated_products.aggregate(average_rating=Avg('rating'))['average_rating'] or 0
        total_orders = self.order_items.aggregate(total_orders=models.Sum('quantity'))['total_orders'] or 0
        weighted_score = (weight_rating * avg_rating) + (weight_orders * total_orders)

        return weighted_score

class Myrating(models.Model):
    user    = models.ForeignKey(User,related_name='rating',on_delete=models.CASCADE) 
    product = models.ForeignKey(Product,related_name='rated_products',on_delete=models.CASCADE)
    rating  = models.IntegerField(default=1,validators=[MaxValueValidator(5),MinValueValidator(0)])
    
    def __str__(self):
        return 'Rated Book: {}'.format(self.product)

    def get_absolute_url(self):
         return reverse('shop:product_detail', args=[self.id, self.slug])

# class ProductManager(models.Manager):
#     def get_trending_books(self, limit=10, weight_rating=0.7, weight_books_ordered = 0.3):
#         trending_books = (
#             self.get_queryset()
#             .annotate(weight_score = models.ExpressionWrapper(
#                 models.F('rating__value__avg') * weight_rating + models.F('bookssold__quantity') * weight_books_ordered,
#                 output_field = models.FloatField()
#             ))
#             .order_by('-weighted_score')[:limit]
#         )
#         return trending_books