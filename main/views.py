# main/views.py - COMPLETE FIXED VERSION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch, Count, Min, Max, Avg, Q, FloatField
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import strip_tags
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Min, Max, Avg, Q
import re

def home(request):
    """Render the home page with complete filtering + city/district tabs"""

    # ---------------------------
    # EXISTING PROPERTY FILTERING
    # ---------------------------
    all_properties = Property.objects.all()
    total_count = all_properties.count()

    filtered_properties = all_properties

    search_query = request.GET.get('search', '').strip()
    price_filter = request.GET.get('price', '')
    developer_filter = request.GET.get('developer', '')
    type_filter = request.GET.get('type', '')
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')

    has_filters = any([
        search_query, price_filter, developer_filter,
        type_filter, location_filter, status_filter
    ])

    if search_query:
        filtered_properties = filtered_properties.filter(
            Q(title__icontains=search_query) |
            Q(developer__name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(district__name__icontains=search_query)
        )

    # PRICE FILTERS
    if price_filter == 'under_500k':
        filtered_properties = filtered_properties.filter(low_price__lt=500000)
    elif price_filter == '500k_1m':
        filtered_properties = filtered_properties.filter(low_price__gte=500000, low_price__lt=1000000)
    elif price_filter == '1m_2m':
        filtered_properties = filtered_properties.filter(low_price__gte=1000000, low_price__lt=2000000)
    elif price_filter == '2m_3m':
        filtered_properties = filtered_properties.filter(low_price__gte=2000000, low_price__lt=3000000)
    elif price_filter == '3m_4m':
        filtered_properties = filtered_properties.filter(low_price__gte=3000000, low_price__lt=4000000)
    elif price_filter == '4m_5m':
        filtered_properties = filtered_properties.filter(low_price__gte=4000000, low_price__lt=5000000)
    elif price_filter == 'above_5m':
        filtered_properties = filtered_properties.filter(low_price__gte=5000000)

    # OTHER FILTERS
    if developer_filter:
        filtered_properties = filtered_properties.filter(developer__name__icontains=developer_filter)

    if type_filter:
        filtered_properties = filtered_properties.filter(property_type_id=type_filter)

    if location_filter:
        filtered_properties = filtered_properties.filter(city_id=location_filter)

    if status_filter:
        filtered_properties = filtered_properties.filter(sales_status_id=status_filter)

    filtered_count = filtered_properties.count()
    has_more_properties = filtered_count > 8

    offplan = filtered_properties.order_by('-low_price')[:8]
    developer = Developer.objects.all()[:10]

    # --------------------------------------
    # NEW: CITY & DISTRICT TAB FUNCTIONALITY
    # --------------------------------------

    cities = City.objects.all().order_by("name").exclude(name__iexact='Unnamed City')

    # Get active city from GET parameter (tabs switch without JS)
    active_city_slug = request.GET.get("city", None)

    if active_city_slug:
        active_city = City.objects.filter(slug=active_city_slug).first()
    else:
        active_city = cities.first()

    # Districts with average price + property count
    if active_city:
        districts = (
            active_city.districts.all()
            .annotate(
                property_count=Count('properties'),
                avg_price=Coalesce(Avg('properties__low_price'), 0, output_field=FloatField())
            )
            .order_by("name")[:8]
        )
    else:
        districts = District.objects.none()


    # --------------------------------------
    # CONTEXT
    # --------------------------------------
    context = {
        # FILTER SYSTEM
        'offplan': offplan,
        'developer': developer,
        'developers': Developer.objects.all(),
        'types': PropertyType.objects.all().exclude(name__iexact='Unknown Type'),
        'location': City.objects.all().exclude(name__iexact='Unnamed City'),
        'status': SalesStatus.objects.all(),
        'selected_price': price_filter,
        'selected_developer': developer_filter,
        'selected_type': type_filter,
        'selected_location': location_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'filtered_count': filtered_count,
        'total_count': total_count,
        'has_filters': has_filters,
        'has_more_properties': has_more_properties,

        # NEW - CITY / DISTRICTS TAB DATA
        'cities': cities,
        'active_city': active_city,
        'districts': districts,

        # SEO
        'page_title': 'Home - Off Plan UAE',
        'meta_description': 'Discover premium off-plan properties in UAE',
    }

    return render(request, 'main/home.html', context)


# def home(request):
#     """Render the home page with complete filtering"""
#     # Get all properties initially
#     all_properties = Property.objects.all()
#     total_count = all_properties.count()
    
#     # Start with all properties for filtering
#     filtered_properties = all_properties
    
#     # Get filter parameters from request
#     search_query = request.GET.get('search', '').strip()
#     price_filter = request.GET.get('price', '')
#     developer_filter = request.GET.get('developer', '')
#     type_filter = request.GET.get('type', '')
#     location_filter = request.GET.get('location', '')
#     status_filter = request.GET.get('status', '')
    
#     # Check if any filters are applied
#     has_filters = any([search_query, price_filter, developer_filter, type_filter, location_filter, status_filter])
    
#     # Apply search filter
#     if search_query:
#         filtered_properties = filtered_properties.filter(
#             Q(title__icontains=search_query) |
#             Q(developer__name__icontains=search_query) |
#             Q(city__name__icontains=search_query) |
#             Q(district__name__icontains=search_query)
#         )
    
#     # Apply price filter
#     if price_filter == 'under_500k':
#         filtered_properties = filtered_properties.filter(low_price__lt=500000)
#     elif price_filter == '500k_1m':
#         filtered_properties = filtered_properties.filter(low_price__gte=500000, low_price__lt=1000000)
#     elif price_filter == '1m_2m':
#         filtered_properties = filtered_properties.filter(low_price__gte=1000000, low_price__lt=2000000)
#     elif price_filter == '2m_3m':
#         filtered_properties = filtered_properties.filter(low_price__gte=2000000, low_price__lt=3000000)
#     elif price_filter == '3m_4m':
#         filtered_properties = filtered_properties.filter(low_price__gte=3000000, low_price__lt=4000000)
#     elif price_filter == '4m_5m':
#         filtered_properties = filtered_properties.filter(low_price__gte=4000000, low_price__lt=5000000)
#     elif price_filter == 'above_5m':
#         filtered_properties = filtered_properties.filter(low_price__gte=5000000)
    
#     # Apply developer filter
#     if developer_filter:
#         filtered_properties = filtered_properties.filter(developer__name__icontains=developer_filter)
    
#     # Apply type filter
#     if type_filter:
#         filtered_properties = filtered_properties.filter(property_type_id=type_filter)
    
#     # Apply location filter
#     if location_filter:
#         filtered_properties = filtered_properties.filter(city_id=location_filter)
    
#     # Apply status filter
#     if status_filter:
#         filtered_properties = filtered_properties.filter(sales_status_id=status_filter)
    
#     # Get count AFTER filtering but BEFORE limiting to 8
#     filtered_count = filtered_properties.count()
    
#     # Check if there are more properties than the displayed 8
#     has_more_properties = filtered_count > 8
    
#     # Limit to 8 for display and order by price
#     offplan = filtered_properties.order_by('-low_price')[:8]
#     developer = Developer.objects.all()[:10]
    
   
    
#     context = {
#         'offplan': offplan,
#         'developer': developer,
#         'developers': Developer.objects.all(),
#         'types': PropertyType.objects.all().exclude(name__iexact='Unknown Type'),
#         'location': City.objects.all().exclude(name__iexact='Unnamed City'),
#         'status': SalesStatus.objects.all(),
#         'selected_price': price_filter,
#         'selected_developer': developer_filter,
#         'selected_type': type_filter,
#         'selected_location': location_filter,
#         'selected_status': status_filter,
#         'search_query': search_query,
#         'filtered_count': filtered_count,  # Count AFTER filtering, BEFORE [:8]
#         'total_count': total_count,        # Total count WITHOUT any filters
#         'has_filters': has_filters,        # Boolean to check if filters are active
#         'has_more_properties': has_more_properties,  # NEW: Flag for "View More" button
        
#         'page_title': 'Home - Off Plan UAE',
#         'meta_description': 'Discover premium off-plan properties in UAE',
#     }
#     return render(request, 'main/home.html', context)

def about(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, 'Thank you for subscribing!')
        return redirect('about')
    
    context = {
        'page_title': 'About Us - OffPlanUAE.ai',
        'meta_description': 'Learn about OffPlanUAE.ai - transforming property discovery in UAE with AI technology.',
    }
    return render(request, 'main/about.html', context)



def about(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, 'Thank you for subscribing!')
        return redirect('about')
    
    context = {
        'page_title': 'About Us - OffPlanUAE.ai',
        'meta_description': 'Learn about OffPlanUAE.ai - transforming property discovery in UAE with AI technology.',
    }
    return render(request, 'main/about.html', context)

def blog(request):
    """Render the blog page with all blog posts from database"""
    # Get all blog posts from database, ordered by published date
    blog_posts = BlogPost.objects.all().order_by('-published_at')
    
    # Pagination - 12 posts per page
    paginator = Paginator(blog_posts, 6)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_title': 'Blog - Off Plan UAE',
        'meta_description': 'Latest news and insights about UAE real estate',
        'blog_posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'main/blog.html', context)

def blog_detail(request, blog_id):
    """Render individual blog post detail page from database"""
    # Get the blog post or return 404
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    
    # Increment view count
    blog_post.views += 1
    blog_post.save(update_fields=['views'])
    
    # Get related posts (excluding current post, limited to 3)
    related_posts = BlogPost.objects.exclude(id=blog_id).order_by('-published_at')[:3]
    
    # Handle contact form submission from sidebar
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        if name and email and phone and message:
            # Save contact submission
            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=f"Blog Contact Form - {blog_post.title}\n\n{message}"
            )
            messages.success(request, 'Thank you for contacting us! We will get back to you within 24 hours.')
            return redirect('main:blog_detail', blog_id=blog_id)
    
    context = {
        'page_title': f'{blog_post.title} - Blog',
        'meta_description': blog_post.excerpt if blog_post.excerpt else strip_tags(blog_post.content)[:160],
        'blog_post': blog_post,
        'related_posts': related_posts,
    }
    return render(request, 'main/blog_detail.html', context)

@csrf_exempt
def contact(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            subject = data.get('subject', '').strip()
            message = data.get('message', '').strip()
            
            errors = {}
            if not name:
                errors['name'] = 'Name is required'
            if not email or '@' not in email:
                errors['email'] = 'Valid email is required'
            if not phone:
                errors['phone'] = 'Phone number is required'
            if not subject:
                errors['subject'] = 'Subject is required'
            if not message:
                errors['message'] = 'Message is required'
            
            if errors:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill all required fields',
                    'errors': errors
                }, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for contacting us! We will get back to you within 24 hours.'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred. Please try again later.'
            }, status=500)
    
    context = {
        'page_title': 'Contact Us - Off Plan UAE',
        'meta_description': 'Get in touch with Off Plan UAE for property inquiries',
    }
    return render(request, 'main/contact.html', context)

def clean_description(text):
    if not text:
        return ""

    # Remove HTML tags
    text = strip_tags(text)

    # Remove CSS property-like junk inside text
    text = re.sub(r"[a-zA-Z\-]+:\s*[^;]+;", "", text)

    # Remove leftover symbols, brackets, and extra spaces
    text = re.sub(r"[<>]", "", text)
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

# def properties(request):
#     # Get all properties
#     project = Property.objects.all()
    
#     # Get all filter parameters
#     price_filter = request.GET.get('price', '')
#     developer_filter = request.GET.get('developer', '')
#     type_filter = request.GET.get('type', '')
#     location_filter = request.GET.get('location', '')
#     status_filter = request.GET.get('status', '')
#     search_query = request.GET.get('search', '')
    
#     # Apply search filter
#     if search_query:
#         project = project.filter(
#             Q(title__icontains=search_query) |
#             Q(developer__name__icontains=search_query) |
#             Q(city__name__icontains=search_query) |
#             Q(district__name__icontains=search_query)
#         )
    
#     # Apply price filter
#     if price_filter == 'under_500k':
#         project = project.filter(low_price__lt=500000)
#     elif price_filter == '500k_1m':
#         project = project.filter(low_price__gte=500000, low_price__lt=1000000)
#     elif price_filter == '1m_2m':
#         project = project.filter(low_price__gte=1000000, low_price__lt=2000000)
#     elif price_filter == '2m_3m':
#         project = project.filter(low_price__gte=2000000, low_price__lt=3000000)
#     elif price_filter == '3m_4m':
#         project = project.filter(low_price__gte=3000000, low_price__lt=4000000)
#     elif price_filter == '4m_5m':
#         project = project.filter(low_price__gte=4000000, low_price__lt=5000000)
#     elif price_filter == 'above_5m':
#         project = project.filter(low_price__gte=5000000)
    
#     # Apply developer filter
#     if developer_filter:
#         project = project.filter(developer__name=developer_filter)
    
#     # Apply type filter
#     if type_filter:
#         project = project.filter(property_type__name=type_filter)
    
#     # Apply location filter
#     if location_filter:
#         project = project.filter(city__name=location_filter)
    
#     # Apply status filter
#     if status_filter:
#         project = project.filter(property_status__name=status_filter)
    
    
    
#     # Pagination
#     paginator = Paginator(project, 12)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
    
#     context = {
#         'project': page_obj,
#         'logo': Developer.objects.all(),
#         'types': PropertyType.objects.all().exclude(name__iexact='Unknown Type'),
#         'developers': Developer.objects.all(),
#         'location': City.objects.all().exclude(name__iexact='Unnamed City'),
#         'status': SalesStatus.objects.all(),
#         'selected_price': price_filter,
#         'selected_developer': developer_filter,
#         'selected_type': type_filter,
#         'selected_location': location_filter,
#         'selected_status': status_filter,
#         'search_query': search_query,
#         'footer_property_types': GroupedApartment.objects.all().exclude(unit_type__iexact='Unknown Type'),
#     } 
#     return render(request, 'main/properties.html', context)



from django.core.paginator import Paginator
from django.db.models import Q

def properties(request):
    # ---------------------------
    # Base queryset
    # ---------------------------
    project = Property.objects.all()
    
    # ---------------------------
    # Get filter parameters
    # ---------------------------
    price_filter = request.GET.get('price', '')
    developer_filter = request.GET.get('developer', '')
    type_filter = request.GET.get('type', '')  # From footer links
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # ---------------------------
    # Apply search filter
    # ---------------------------
    if search_query:
        project = project.filter(
            Q(title__icontains=search_query) |
            Q(developer__name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(district__name__icontains=search_query)
        )
    
    # ---------------------------
    # Apply price filter
    # ---------------------------
    if price_filter == 'under_500k':
        project = project.filter(low_price__lt=500000)
    elif price_filter == '500k_1m':
        project = project.filter(low_price__gte=500000, low_price__lt=1000000)
    elif price_filter == '1m_2m':
        project = project.filter(low_price__gte=1000000, low_price__lt=2000000)
    elif price_filter == '2m_3m':
        project = project.filter(low_price__gte=2000000, low_price__lt=3000000)
    elif price_filter == '3m_4m':
        project = project.filter(low_price__gte=3000000, low_price__lt=4000000)
    elif price_filter == '4m_5m':
        project = project.filter(low_price__gte=4000000, low_price__lt=5000000)
    elif price_filter == 'above_5m':
        project = project.filter(low_price__gte=5000000)
    
    # ---------------------------
    # Apply developer filter
    # ---------------------------
    if developer_filter:
        project = project.filter(developer__name=developer_filter)
    
    # ---------------------------
    # Apply property type filter
    # ---------------------------
    if type_filter:
        # Only filter if the type is one of the footer unit types
        allowed_types = ['Villa', 'Apartment', 'Townhouse', 'Penthouse', 'Studio', 'Duplex']
        if type_filter in allowed_types:
            project = project.filter(grouped_apartments__unit_type__iexact=type_filter).distinct()
    
    # ---------------------------
    # Apply location filter
    # ---------------------------
    if location_filter:
        project = project.filter(city__name=location_filter)
    
    # ---------------------------
    # Apply status filter
    # ---------------------------
    if status_filter:
        project = project.filter(property_status__name=status_filter)
    
    # ---------------------------
    # Pagination
    # ---------------------------
    paginator = Paginator(project, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # ---------------------------
    # Context
    # ---------------------------
    context = {
        'project': page_obj,
        'logo': Developer.objects.all(),
        'types': PropertyType.objects.all().exclude(name__iexact='Unknown Type'),
        'developers': Developer.objects.all(),
        'location': City.objects.all().exclude(name__iexact='Unnamed City'),
        'status': SalesStatus.objects.all(),
        'selected_price': price_filter,
        'selected_developer': developer_filter,
        'selected_type': type_filter,
        'selected_location': location_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'footer_property_types': GroupedApartment.objects.all().exclude(unit_type__iexact='Unknown Type'),
    } 
    return render(request, 'main/properties.html', context)

from collections import defaultdict

def properties_detail(request, slug):

    property_obj = (
        Property.objects.select_related(
            "developer", "city", "district",
            "property_type", "property_status",
            "sales_status"
        )
        .prefetch_related(
            "property_images",
            "facilities",
            Prefetch("grouped_apartments", queryset=GroupedApartment.objects.all())
        )
        .filter(slug=slug)
        .first()
    )

    if not property_obj:
        return render(request, "404.html", status=404)

    # -------------------------------------
    # Parse latitude, longitude
    # -------------------------------------
    if property_obj.address:
        try:
            lat, lng = [coord.strip() for coord in property_obj.address.split(",")]
        except:
            lat, lng = None, None
    else:
        lat, lng = None, None

    # -------------------------------------
    # CLEAN DESCRIPTION (no bleach)
    # -------------------------------------
    text = property_obj.description or ""

    # Remove style="..."
    text = re.sub(r'style="[^"]*"', "", text, flags=re.IGNORECASE)

    # Remove class="..."
    text = re.sub(r'class="[^"]*"', "", text, flags=re.IGNORECASE)

    # Remove leftover CSS-like attributes (ANYTHING like: color: red;)
    text = re.sub(r"[a-zA-Z\-]+\s*:\s*[^;]+;", "", text)

    # Strip HTML tags
    text = strip_tags(text)

    # Remove &nbsp; etc.
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Assign back to object (NOT saving in DB)
    property_obj.description = text

    # -------------------------------------
    # Contact form
    # -------------------------------------
    if request.method == "POST":
        messages.success(request, "Thank you! We will contact you soon.")
        return redirect("main:properties_detail", slug=slug)

    # -------------------------------------
    # Group units by bedroom count
    # -------------------------------------
    bedroom_units = defaultdict(list)
    for unit in property_obj.grouped_apartments.all():
        if unit.rooms and unit.rooms.split()[0].isdigit():
            bedrooms = int(unit.rooms.split()[0])
            bedroom_units[bedrooms].append(unit)

    bedroom_units = dict(sorted(bedroom_units.items()))

    # -------------------------------------
    # Context
    # -------------------------------------
    context = {
        "property": property_obj,
        "page_title": f"{property_obj.title} - Property Details",
        "meta_description": text[:160] if text else "",
        "images": property_obj.property_images.all(),
        "facilities": property_obj.facilities.all(),
        "units": property_obj.grouped_apartments.all(),
        "units_by_bedroom": bedroom_units,
        "lat": lat,
        "lng": lng,
        "clean_description": text,   # FIXED key
    }

    return render(request, "main/properties_detail.html", context)

def community_properties(request, slug):
    """Show all properties in a specific community (district)"""
    district = get_object_or_404(District, id=slug)
    
    properties = Property.objects.filter(
        district=district
    ).select_related(
        'developer', 'city', 'district', 
        'property_type', 'property_status', 'sales_status'
    ).prefetch_related('property_images')
    
    price_filter = request.GET.get('price', '')
    developer_filter = request.GET.get('developer', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    
    if price_filter == 'under_500k':
        properties = properties.filter(low_price__lt=500000)
    elif price_filter == '500k_1m':
        properties = properties.filter(low_price__gte=500000, low_price__lt=1000000)
    elif price_filter == '1m_2m':
        properties = properties.filter(low_price__gte=1000000, low_price__lt=2000000)
    elif price_filter == '2m_3m':
        properties = properties.filter(low_price__gte=2000000, low_price__lt=3000000)
    elif price_filter == '3m_4m':
        properties = properties.filter(low_price__gte=3000000, low_price__lt=4000000)
    elif price_filter == '4m_5m':
        properties = properties.filter(low_price__gte=4000000, low_price__lt=5000000)
    elif price_filter == 'above_5m':
        properties = properties.filter(low_price__gte=5000000)
    
    if developer_filter:
        properties = properties.filter(developer_id=developer_filter)
    
    if type_filter:
        properties = properties.filter(property_type_id=type_filter)
    
    if status_filter:
        properties = properties.filter(sales_status_id=status_filter)
    
    total_count = properties.count()
    min_price = properties.aggregate(Min('low_price'))['low_price__min'] or 0
    avg_price = properties.aggregate(Avg('low_price'))['low_price__avg'] or 0
    
    paginator = Paginator(properties.order_by('-low_price'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'district': district,
        'properties': page_obj,
        'total_count': total_count,
        'min_price': min_price,
        'avg_price': int(avg_price),
        'developers': Developer.objects.filter(
            properties__district=district
        ).distinct(),
        'types': PropertyType.objects.filter(
            properties__district=district
        ).distinct().exclude(name__iexact='Unknown Type'),
        'status': SalesStatus.objects.filter(
            properties__district=district
        ).distinct(),
        'selected_price': price_filter,
        'page_title': f'{district.name} - Properties',
        'meta_description': f'Explore {total_count} properties in {district.name}, {district.city.name if district.city else "UAE"}',
    }
    
    return render(request, 'main/community_properties.html', context)
  

def all_communities(request):
    """Display all communities with filtering, sorting, and pagination"""
    
    # Get all cities excluding unnamed
    cities = City.objects.all().order_by("name").exclude(name__iexact='Unnamed City')
    
    # Get all districts with aggregated data
    all_districts = (
        District.objects.all()
        .select_related('city')
        .prefetch_related('properties')
        .annotate(
            property_count=Count('properties'),
            avg_price=Coalesce(Avg('properties__low_price'), 0, output_field=FloatField())
        )
        .filter(property_count__gt=0)  # Only show districts with properties
        .order_by('name')
    )
    
    # Filter by city if requested
    city_filter = request.GET.get('city', '')
    if city_filter:
        all_districts = all_districts.filter(city__slug=city_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name-asc')
    if sort_by == 'name-desc':
        all_districts = all_districts.order_by('-name')
    elif sort_by == 'projects-desc':
        all_districts = all_districts.order_by('-property_count')
    elif sort_by == 'projects-asc':
        all_districts = all_districts.order_by('property_count')
    elif sort_by == 'price-desc':
        all_districts = all_districts.order_by('-avg_price')
    elif sort_by == 'price-asc':
        all_districts = all_districts.order_by('avg_price')
    else:  # name-asc (default)
        all_districts = all_districts.order_by('name')
    
    # Pagination - 12 communities per page
    paginator = Paginator(all_districts, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare community data for template
    communities = []
    for district in page_obj:
        first_property = district.properties.first()
        communities.append({
            'id': district.id,
            'name': district.name,
            'city_name': district.city.name if district.city else 'UAE',
            'city_slug': district.city.slug if district.city else 'uae',
            'property_count': district.property_count,
              'avg_price': district.avg_price if district.avg_price > 0 else None, 
            'first_property_cover': first_property.cover if first_property else '/static/images/no-image.jpg',
        })
    
    # Calculate totals
    total_communities = all_districts.count()
    total_properties = Property.objects.filter(district__in=all_districts).count()
    
    context = {
        'communities': communities,
        'cities': cities,
        'total_communities': total_communities,
        'total_properties': total_properties,
        'page_obj': page_obj,
        'selected_city': city_filter,
        'selected_sort': sort_by,
        'page_title': 'All Communities - UAE Real Estate',
        'meta_description': f'Explore {total_communities} communities across UAE with {total_properties} premium properties',
    }
    
    return render(request, 'main/all_communities.html', context)  