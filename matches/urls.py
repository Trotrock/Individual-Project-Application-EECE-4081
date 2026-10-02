from django.urls import path
from . import views

urlpatterns = [
    path('sync/', views.sync_and_render_match, name='sync_match'),
]
