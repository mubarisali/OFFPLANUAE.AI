from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('properties/', views.properties, name='properties'),
    # path('properties_detail/', views.properties_detail, name='properties_detail'),
    path('property/<slug:slug>/', views.properties_detail, name='properties_detail'),
     path('community/<int:slug>/', views.community_properties, name='community_properties'),
      path('communities/', views.all_communities, name='all_communities'),

]   
