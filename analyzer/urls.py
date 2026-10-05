from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.history, name='history'),
    path('pricing/', views.pricing, name='pricing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:pk>/', views.result, name='result'),
    path('checkout/<str:plan>/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('manage-plan/', views.manage_plan, name='manage_plan'),
    path('downgrade/', views.downgrade_to_free, name='downgrade_to_free'),
]
