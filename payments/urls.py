from django.urls import path, include
from . import views
from . paypal import PayPalPaymentView, CaptureOrderView


    


urlpatterns = [
    path('paypal-create-order', PayPalPaymentView.as_view(), name="paypal-create-order"),
    path('paypal-capture-order', CaptureOrderView.as_view(), name="paypal-capture-order"),
    path('get-client-id',views.GetClientId.as_view(), name='get-client-id'),
    path('create-product',views.Product.as_view(),name='create-product'),
    path('create-plan',views.ProductPlanView.as_view(),name='create-plan'),
    path('user-subscription',views.SubscriptionView.as_view(),name='user-subscription'),
    
]