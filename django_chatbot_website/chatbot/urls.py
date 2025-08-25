from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('api/upload-dataset/', views.upload_dataset, name='upload_dataset'),
    path('api/create-chart/', views.create_chart, name='create_chart'),
    path('api/dataset-info/', views.get_dataset_info, name='dataset_info'),
]
