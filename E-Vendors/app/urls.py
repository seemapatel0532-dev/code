from django.urls import path
from django.contrib import admin
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm,MyPasswordChangeForm,MySetPasswordForm

urlpatterns = [
    path('', views.home, name = "home"),
    path("about/",views.about,name="about"),
    path("customer-registration/",views.CustomerRegistrationView.as_view(),name="customer-registration"),
    path("terms-conditions/",views.terms_conditions,name="terms-conditions"),
    path("privacy-policy/",views.privacy_policy,name="privacy-policy"),
    path("category/<slug:val>",views.CategoryView.as_view(),name="category"),
    path("category-title/<val>",views.CategoryTitle.as_view(),name="category-title"),
    path('vendor_dashboard/', views.vendor_register, name='vendor_dashboard'),
    path('vendor_info/<int:pk>/', views.vendor_info, name='vendor_info'),
     path('add-product/', views.add_product, name='add_product'),
     path('product/<int:pk>/submit-review/', views.ProductDetail.as_view(), name='submit_review'),

    # password change
    path("password-change/",auth_view.PasswordChangeView.as_view(template_name="app/changePassword.html",form_class=MyPasswordChangeForm, success_url="/password-change-done"), name="password-change"),
    path("password-change-done/",auth_view.PasswordChangeDoneView.as_view(template_name="app/passwordChangeDone.html"), name="password-change-done"),
    path('logout/', auth_view.LogoutView.as_view(next_page='login'), name='logout'),
    path("password-reset/", auth_view.PasswordResetView.as_view(
        template_name="app/passwordReset.html",
        form_class=MyPasswordResetForm), name="password_reset"),

    path("password-reset/done/", auth_view.PasswordResetDoneView.as_view(
        template_name="app/passwordResetDone.html"), name="password_reset_done"),

    path("password_reset_confirm/<uidb64>/<token>/", auth_view.PasswordResetConfirmView.as_view(
        template_name="app/passwordResetConfirm.html",
        form_class=MySetPasswordForm), name="password_reset_confirm"),

    path("password_reset_complete/", auth_view.PasswordResetCompleteView.as_view(
        template_name="app/passwordResetComplete.html"), name="password_reset_complete"),

    path('profile/',views.ProfileView.as_view(),name="profile"),
    path('address/',views.address,name="address"),
    path('updateAddress/<int:pk>',views.UpdateAddress.as_view(),name="updateAddress"),

    path("product-detail/<int:pk>",views.ProductDetail.as_view(),name="product-detail"),

    path('remove-cart/', views.remove_cart, name='remove_cart'),
    path('pluscart/',views.plus_cart,),
    path('minuscart/',views.minus_cart,),
    path('add-to-cart/',views.add_to_cart,name="add-to-cart"), 
    path('cart/',views.show_cart,name="showcart"),
    path('orders/',views.orders,name='orders'),
    path('pluswishlist/',views.plus_wishlist,),
    path('minuswishlist/',views.minus_wishlist,),
    path('wishlists/',views.wishlists,name="wishlists"),
    path("search/",views.search,name='search'),
    path('add-all-to-cart/', views.add_all_to_cart, name='add-all-to-cart'),

    path('checkout/',views.Checkout.as_view(),name="checkout"),
    path('buynow/<int:pk>',views.buynow,name="buynow"),
    path('paymentdone/', views.PaymentDone.as_view(), name='paymentdone'),
    path('BuyNowPaymentDone/', views.BuyNowPaymentDone.as_view(), name='BuyNowPaymentDone'),
]