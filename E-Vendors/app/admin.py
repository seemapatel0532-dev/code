from django.contrib import admin
from . models import Product,Customer,Cart,Payment,OrderPlaced,Wishlist,Review,Vendor
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.
@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ["id","title","price","category","image_url"]

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    liist_display = ['id','user','locality','city','state','zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']
    # def products(self,obj):
    #     link = reverse("admin:app_product_change",args=[obj.product.pk])
    #     return format_html("<a href='{}'>{}</a>",link,obj.product.title)

@admin.register(Payment)
class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']
@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
     list_display = ['id','user','customer','product','quantity','ordered_date','status','payment']

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin): 
    list_display = ['id','user','product']

@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin): 
    list_display = ['id','rating','created_at']

@admin.register(Vendor)
class VendorModelAdmin(admin.ModelAdmin): 
    list_display = ['id','vendor_name','contact_number']


