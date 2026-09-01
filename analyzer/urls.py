from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.history, name='history'),
    path('pricing/', views.pricing, name='pricing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:pk>/', views.result, name='result'),
]
