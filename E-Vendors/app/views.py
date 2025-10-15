from django.shortcuts import get_object_or_404, render,redirect
from django.views import View
from . models import Product,Customer,Cart,Wishlist,Vendor
from django.db.models import Count
from . forms import CustomerRegistrationForm,CustomerProfile, ReviewForm
from django.contrib import messages
from django.http import JsonResponse 
from django.db.models import Q
from django.contrib.auth.models import User
import razorpay
from django.conf import settings
from .models import Payment,OrderPlaced
from django.http import HttpResponseBadRequest
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import VendorProfileForm,ProductForm
from django.contrib.auth import login
from django.views.decorators.http import require_POST


def home(request):
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))

    return render(request,"app/home.html",locals())

def about(request):
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/about.html",locals())

def terms_conditions(request):
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/terms_condition.html",locals())

def privacy_policy(request):
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/privacy_policy.html",locals())

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        wishItem = 0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/customerRegistration.html", locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Check if the email already exists
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.warning(request, "Email already exists.")
            else:
                # Save the user
                form.save()
                messages.success(request, "Congratulations! User registered successfully.")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, "app/customerRegistration.html", locals())

    
def return_category(val):
    if val == 'CR':
        return "Curd"
    elif val == 'ML':
        return "Milk"
    elif val == 'LS':
        return "Lassi"
    elif val == 'MS':
        return "Milkshake"
    elif val == 'PN':
        return "Paneer"
    elif val == 'GH':
        return "Ghee"
    elif val == 'CZ':
        return "Cheese"
    elif val == 'IC':
        return "Ice-creams"
        

@method_decorator(login_required, name='dispatch')
class CategoryView(View):
    def get(self, request, val):
        wishItem = 0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        
        product_list = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')

        # Paginator for 6 products per page
        paginator = Paginator(product_list, 4)  # 4 products per page
        page = request.GET.get('page', 1)  # Get the page number from the request
        
        try:
            product = paginator.page(page)
        except PageNotAnInteger:
            product = paginator.page(1)
        except EmptyPage:
            product = paginator.page(paginator.num_pages)

        category = return_category(val)
        return render(request, "app/category.html", locals())

@method_decorator(login_required, name='dispatch')
class CategoryTitle(View):
    def get(self, request, val):
        wishItem = 0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        
        product_list = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product_list[0].category).values('title')

        # Paginator for 6 products per page
        paginator = Paginator(product_list, 4)
        page = request.GET.get('page', 1)
        
        try:
            product = paginator.page(page)
        except PageNotAnInteger:
            product = paginator.page(1)
        except EmptyPage:
            product = paginator.page(paginator.num_pages)

        return render(request, "app/category.html", locals())
    
def vendor_register(request):
    vendor = Vendor.objects.filter(user=request.user).first()  # Check if the vendor exists for the user
    if vendor:
        # Fetch all products uploaded by the vendor
        products_list = Product.objects.filter(vendor=vendor)

        # Pagination - Show 6 products per page
        paginator = Paginator(products_list, 4)  # 4 products per page
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        # Render the vendor's profile and their products
        return render(request, 'app/vendor.html', {'vendor': vendor, 'products': products})
    else:
        # If the vendor is not available, display the registration form
        if request.method == 'POST':
            form = VendorProfileForm(request.POST)
            if form.is_valid():
                vendor = form.save(commit=False)
                vendor.user = request.user
                vendor.save()
                return redirect('vendor_dashboard')  # Redirect after successful registration
        else:
            form = VendorProfileForm()

        # Render the form if vendor is not present
        return render(request, 'app/vendor.html', {'form': form})
    
def vendor_info(request,pk):
    vendor = Vendor.objects.get(id = pk)  # Check if the vendor exists for the user
    if vendor:
        # Fetch all products uploaded by the vendor
        products_list = Product.objects.filter(vendor=vendor)

        # Pagination - Show 6 products per page
        paginator = Paginator(products_list, 4)  # 4 products per page
        page_number = request.GET.get('page')
        products = paginator.get_page(page_number)

        # Render the vendor's profile and their products
        return render(request, 'app/vendor_info.html', {'vendor': vendor, 'products': products})
    else:
        return HttpResponse("<h2>Page not found</h2>")
    
def add_product(request):
    vendor = Vendor.objects.filter(user=request.user).first()

    if not vendor:
        return redirect('vendor_register')  # Redirect to vendor registration if vendor doesn't exist

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle file upload with request.FILES
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor  # Assign the vendor automatically
            product.save()
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()

    return render(request, 'app/add_product.html', {'form': form, 'vendor': vendor})

@method_decorator(login_required, name='dispatch')    
class ProfileView(View):
    def get(self,request):
        form = CustomerProfile()
        wishItem=0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/profile.html",locals())
    def post(self,request):
        form = CustomerProfile(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulation! User Data saved Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,"app/profile.html",locals())
@login_required
def address(request):
    add = Customer.objects.filter(user = request.user)
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    return render(request,"app/address.html",locals())
@method_decorator(login_required, name='dispatch')
class UpdateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfile(instance=add)
        wishItem=0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/updateAddress.html",locals())
    def post(self,request,pk):
        form = CustomerProfile(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.user = request.user
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']

            add.save()
            messages.success(request,"Congratulation! User Data Updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")
    
@method_decorator(login_required, name='dispatch')
class ProductDetail(View):
    def get(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user)).exists()
        totalItem = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
        wishItem = Wishlist.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
        category = return_category(product.category)
        reviews_list = product.reviews.all()

        # Pagination for reviews
        paginator = Paginator(reviews_list, 3)  # Show 5 reviews per page
        page_number = request.GET.get('page')
        reviews = paginator.get_page(page_number)
        return render(request, "app/productDetail.html", locals())

    def post(self, request, pk):
        product = get_object_or_404(Product, id=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.save()
            return redirect('home')
        else:
            form = ReviewForm()
        return render(request, "app/productDetail.html", {
            'product': product,
            'form': form,
            'reviews': product.reviews.all()
        })
    
@login_required   
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user = user,product = product).save()
    return redirect("/cart")

@login_required   
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.price
        amount = amount + value
    totalamount = amount + 40
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/addtocart.html',locals())

@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        
        try:
            cart_item = Cart.objects.get(Q(user=request.user, product_id=prod_id))
            cart_item.quantity += 1
            cart_item.save()
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found.'}, status=404)
        except Cart.MultipleObjectsReturned:
            cart_items = Cart.objects.filter(Q(user=request.user, product_id=prod_id))
            cart_item = cart_items.first()
            cart_items.exclude(id=cart_item.id).delete()
            cart_item.quantity += 1
            cart_item.save()

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(item.quantity * item.product.price for item in cart)
        totalamount = amount + 40

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')

        try:
            cart_item = Cart.objects.get(Q(user=request.user, product_id=prod_id))
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # Optionally, you might want to handle the case where quantity is 1 and should not be decremented further
                cart_item.quantity = 1  # Ensure it stays at 1
                cart_item.save()
        except Cart.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found.'}, status=404)
        except Cart.MultipleObjectsReturned:
            cart_items = Cart.objects.filter(Q(user=request.user, product_id=prod_id))
            cart_item = cart_items.first()
            cart_items.exclude(id=cart_item.id).delete()
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.quantity = 1
                cart_item.save()

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(item.quantity * item.product.price 
                     for item in cart)
        totalamount = amount + 40

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    
@login_required
def remove_cart(request):
    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        
        if not prod_id:
            return HttpResponse('Product ID is required.', status=400)
        
        try:
            cart_item = Cart.objects.get(user=request.user, product_id=int(prod_id))
            cart_item.delete()
        except Cart.DoesNotExist:
            return HttpResponse('Cart item not found.', status=404)

        return redirect('home')  # Redirect to cart page after removal
    else:
        return HttpResponse('Invalid request method.', status=405)


    
@login_required        
def orders(request):
    orders = OrderPlaced.objects.filter(user=request.user)
    wishItem = 0
    totalItem = 0

    if request.user.is_authenticated: 
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    
    # Remove pagination logic
    ord = False
    if len(orders) < 1:
        ord = True

    return render(request, "app/orders.html", locals())

    
@login_required
def plus_wishlist(request):
    print(request.user,"******************")
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data = {
            "message":"Wishlist Added Successfully",
        }
        return JsonResponse(data)
@login_required   
def minus_wishlist(request):
    print(request.user,"******************")
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data = {
            "message":"Wishlist Remove Successfully",
        }
        return JsonResponse(data)
@login_required
def wishlists(request):
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user)
    products = [item.product for item in wishlist_items]
    context = {
        'products': products,
    }
    return render(request, "app/wishlist.html", context)

@login_required
def add_all_to_cart(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user)
    for item in wishlist_items:
        # Check if the item already exists in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=item.product,
            defaults={'quantity': 1}
        )
        if not created:
            # If the item already exists in the cart, increase the quantity
            cart_item.quantity += 1
            cart_item.save()
    
    # Delete all items from the wishlist
    wishlist_items.delete()
    
    # Redirect to a page showing the cart, assuming 'cart' is the name of that view
    return redirect('showcart')


@login_required
def search(request):
    query = request.GET['search']
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,"app/search.html",locals())

@method_decorator(login_required, name='dispatch')
class Checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        wishItem=0
        totalItem = 0
        if request.user.is_authenticated:
            totalItem = len(Cart.objects.filter(user=request.user))
            wishItem = len(Wishlist.objects.filter(user=request.user))
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.price
            famount = famount + value
        totalamount = famount + 40
        razoramounnt = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data = {'amount':razoramounnt,'currency':"INR","receipt":"order_recptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id = order_id,
                razorpay_payment_status = order_status
            )
            payment.save()
        return render(request,"app/checkout.html",locals())

@method_decorator(login_required, name='dispatch')
class PaymentDone(View):
    def get(self, request):
        print(10)
        try:
            order_id = request.GET.get('order_id')
            payment_id = request.GET.get('payment_id')
            cust_id = int(request.GET.get('cust_id'))
            #print(cust_id)

            # Check if cust_id is not None and is not empty
            if cust_id:
                # Cust_id is provided, proceed with your logic
                # Fetch the payment object
                customer = Customer.objects.get(id=cust_id)

                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.paid = True
                payment.save()

                # Move items from Cart to OrderPlaced
                user = request.user
                cart_items = Cart.objects.filter(user=user)
                for item in cart_items:
                    OrderPlaced(user=user, customer=customer, product=item.product, quantity=item.quantity,payment=payment).save()
                    item.delete()

                #return render(request, 'app/orders.html')
                return redirect('orders')
            else:
                # Cust_id is missing or empty, handle the error gracefully
                return HttpResponse("cust_id is missing or empty.", status=400)
        except Payment.DoesNotExist:
            return HttpResponse("Payment record not found.", status=404)
        except Exception as e:
            # Return the error message along with the exception details
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

@login_required
def buynow(request,pk):
    user = request.user
    add = Customer.objects.filter(user=user)
    product = Product.objects.get(id=pk)
    wishItem=0
    totalItem = 0
    if request.user.is_authenticated:
        totalItem = len(Cart.objects.filter(user=request.user))
        wishItem = len(Wishlist.objects.filter(user=request.user))
    totalamount = product.price + 40
    razoramounnt = int(totalamount * 100)
    client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
    data = {'amount':razoramounnt,'currency':"INR","receipt":"order_recptid_12"}
    payment_response = client.order.create(data=data)
    print(payment_response)
    order_id = payment_response['id']
    order_status = payment_response['status']
    if order_status == 'created':
        payment = Payment(
            user=user,
            amount=totalamount,
            razorpay_order_id = order_id,
            razorpay_payment_status = order_status
        )
        payment.save()
    return render(request,"app/buynow.html",locals())

@method_decorator(login_required, name='dispatch')
class BuyNowPaymentDone(View):
    def get(self, request):
        try:
            order_id = request.GET.get('order_id')
            payment_id = request.GET.get('payment_id')
            cust_id = int(request.GET.get('cust_id'))
            prod_id = request.GET.get('prod_id')
            #print(cust_id)

            # Check if cust_id is not None and is not empty
            if cust_id:
                # Cust_id is provided, proceed with your logic
                # Fetch the payment object
                customer = Customer.objects.get(id=cust_id)

                payment = Payment.objects.get(razorpay_order_id=order_id)
                payment.razorpay_payment_id = payment_id
                payment.paid = True
                payment.save()

                # Move items from Cart to OrderPlaced
                user = request.user 
                product = Product.objects.get(id=prod_id)
                
                OrderPlaced(user=user, customer=customer, product=product, quantity=1,payment=payment).save()

                #return render(request, 'app/orders.html')
                return redirect('orders')
            else:
                # Cust_id is missing or empty, handle the error gracefully
                return HttpResponse("cust_id is missing or empty.", status=400)
        except Payment.DoesNotExist:
            return HttpResponse("Payment record not found.", status=404)
        except Exception as e:
            # Return the error message along with the exception details
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

