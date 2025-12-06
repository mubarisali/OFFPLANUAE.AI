

# main/admin.py
from django.contrib import admin
from .models import *


class PropertyImageInline(admin.TabularInline):
    model = PropertyImages
    extra = 3

admin.site.register(Developer)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug','district']
    list_filter = ['title','created_at']
    search_fields = ['title', 'location', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'views', 'published_at']
    list_filter = ['published_at', 'author']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'submitted_at', 'is_read']
    list_filter = ['is_read', 'submitted_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_read']
    date_hierarchy = 'submitted_at'
    readonly_fields = ['name', 'email', 'phone', 'message', 'submitted_at']

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    date_hierarchy = 'subscribed_at'

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display= ['name','slug']

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display= ['name']
