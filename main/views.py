# offplanuae/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    """Render the home page"""
    context = {
        'page_title': 'Home - Off Plan UAE',
        'meta_description': 'Discover premium off-plan properties in UAE',
    }
    return render(request, 'main/home.html', context)

def about(request):
    """Render the about page"""
    context = {
        'page_title': 'About Us - Off Plan UAE',
        'meta_description': 'Learn more about Off Plan UAE',
    }
    return render(request, 'main/about.html', context)

def blog(request):
    """Render the blog page"""
    context = {
        'page_title': 'Blog - Off Plan UAE',
        'meta_description': 'Latest news and insights about UAE real estate',
        'blog_posts': [
            {
                'title': 'Top 10 Off-Plan Projects in Dubai 2024',
                'excerpt': 'Discover the most promising off-plan developments...',
                'date': '2024-11-15',
                'image': '/static/images/blog1.jpg'
            },
            {
                'title': 'Investment Guide: Abu Dhabi Real Estate',
                'excerpt': 'Everything you need to know about investing...',
                'date': '2024-11-10',
                'image': '/static/images/blog2.jpg'
            },
        ]
    }
    return render(request, 'main/blog.html', context)

@csrf_exempt
def contact(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            message = data.get('message')
            
            # Here you can add email sending logic or save to database
            # For now, just return success
            
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for contacting us! We will get back to you soon.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    context = {
        'page_title': 'Contact Us - Off Plan UAE',
        'meta_description': 'Get in touch with Off Plan UAE',
    }
    return render(request, 'main/contact.html', context)