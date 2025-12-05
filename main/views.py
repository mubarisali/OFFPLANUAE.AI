# main/views.py - COMPLETE FIXED VERSION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Prefetch, Count, Min, Max, Avg,Q
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def home(request):
    """Render the home page with complete filtering"""
    # Get all properties initially
    all_properties = Property.objects.all()
    total_count = all_properties.count()
    
    # Start with all properties for filtering
    filtered_properties = all_properties
    
    # Get filter parameters from request
    search_query = request.GET.get('search', '').strip()
    price_filter = request.GET.get('price', '')
    developer_filter = request.GET.get('developer', '')
    type_filter = request.GET.get('type', '')
    location_filter = request.GET.get('location', '')
    status_filter = request.GET.get('status', '')
    
    # Apply search filter
    if search_query:
        filtered_properties = filtered_properties.filter(
            Q(title__icontains=search_query) |
            Q(developer__name__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(district__name__icontains=search_query)
        )
    
    # Apply price filter
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
    
    # Apply developer filter
    if developer_filter:
        filtered_properties = filtered_properties.filter(developer__name__icontains=developer_filter)
    
    # Apply type filter
    if type_filter:
        filtered_properties = filtered_properties.filter(property_type_id=type_filter)
    
    # Apply location filter
    if location_filter:
        filtered_properties = filtered_properties.filter(city_id=location_filter)
    
    # Apply status filter
    if status_filter:
        filtered_properties = filtered_properties.filter(sales_status_id=status_filter)
    
    # Get count after filtering
    filtered_count = filtered_properties.count()
    
    # Check if any filters are applied
    has_filters = any([search_query, price_filter, developer_filter, type_filter, location_filter, status_filter])
    
    # Limit to 8 for display and order by price
    offplan = filtered_properties.order_by('-low_price')[:8]
    developer = Developer.objects.all()[:10]
    
    # ============================================
    # Community Section Data
    # ============================================
    communities = []
    districts = District.objects.filter(
        properties__isnull=False
    ).distinct().select_related('city')
    
    for district in districts:
        district_properties = Property.objects.filter(district=district).order_by('low_price')
        property_count = district_properties.count()
        
        if property_count > 0:
            first_property = district_properties.first()
            min_price = district_properties.aggregate(Min('low_price'))['low_price__min'] or 0
            max_price = district_properties.aggregate(Max('low_price'))['low_price__max'] or 0
            avg_price = district_properties.aggregate(Avg('low_price'))['low_price__avg'] or 0
            
            communities.append({
                'name': district.name,
                'slug': district.id,
                'city_name': district.city.name if district.city else 'UAE',
                'city_slug': district.city.slug if district.city else 'all',
                'property_count': property_count,
                'first_property_cover': first_property.cover if first_property.cover else 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
                'min_price': min_price,
                'max_price': max_price,
                'avg_price': int(avg_price),
            })
    
    communities = sorted(communities, key=lambda x: x['property_count'], reverse=True)[:8]
    
    cities_with_count = City.objects.filter(
        districts__properties__isnull=False
    ).exclude(
        name__iexact='Unnamed City'
    ).annotate(
        district_count=Count('districts', distinct=True)
    ).filter(district_count__gt=0).order_by('name')
    
    total_communities = len(communities)
    
    context = {
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
        'communities': communities,
        'cities_with_count': cities_with_count,
        'total_communities': total_communities,
        'page_title': 'Home - Off Plan UAE',
        'meta_description': 'Discover premium off-plan properties in UAE',
    }
    return render(request, 'main/home.html', context)

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
    """Render the blog page with all blog posts"""
    blog_posts = [
        {
            'id': 1,
            'title': 'Top 10 Off-Plan Developments in Dubai 2025',
            'excerpt': 'Explore the most promising off-plan projects launching this year in Dubai\'s thriving real estate market. Discover exclusive opportunities.',
            'date': 'Nov 20, 2025',
            'author': 'Sarah Ahmed',
            'image': 'img/hero.avif',
            'content': '''
                <p>Dubai's real estate market continues to flourish with groundbreaking off-plan developments that redefine luxury living. In this comprehensive guide, we explore the top 10 projects that are set to transform the emirate's skyline in 2025.</p>
                
                <h3>1. Palm Residences - Nakheel</h3>
                <p>Located on the iconic Palm Jumeirah, this development offers unparalleled beachfront living with world-class amenities and stunning Arabian Gulf views.</p>
                
                <h3>2. Downtown Villas - Damac Properties</h3>
                <p>Experience urban sophistication in the heart of Downtown Dubai with these premium villas featuring contemporary design and smart home technology.</p>
                
                <h3>3. Marina Heights - Emaar Properties</h3>
                <p>Rising high in Dubai Marina, these luxury apartments offer breathtaking views and direct access to the finest dining and entertainment venues.</p>
                
                <p>Each of these developments represents the pinnacle of modern architecture and lifestyle convenience, making them excellent investment opportunities for both end-users and investors.</p>
            '''
        },
        {
            'id': 2,
            'title': 'How AI is Transforming Property Investment',
            'excerpt': 'Discover how artificial intelligence is revolutionizing the way investors find and evaluate real estate opportunities in the UAE market.',
            'date': 'Nov 18, 2025',
            'author': 'Michael Johnson',
            'image': 'img/hero.avif',
            'content': '''
                <p>Artificial Intelligence is reshaping the real estate industry, bringing unprecedented efficiency and insights to property investment decisions.</p>
                
                <h3>Predictive Analytics</h3>
                <p>AI algorithms analyze vast amounts of market data to predict price trends, helping investors make informed decisions about when and where to invest.</p>
                
                <h3>Property Valuation</h3>
                <p>Machine learning models can accurately assess property values by considering multiple factors including location, amenities, market trends, and historical data.</p>
                
                <h3>Personalized Recommendations</h3>
                <p>AI-powered platforms like OffPlanUAE.ai can match investors with properties that perfectly align with their investment goals and preferences.</p>
            '''
        },
        {
            'id': 3,
            'title': 'Understanding UAE Real Estate Laws',
            'excerpt': 'A comprehensive guide to navigating property ownership regulations and legal requirements in the United Arab Emirates.',
            'date': 'Nov 15, 2025',
            'author': 'Fatima Al-Mansoori',
            'image': 'img/hero.avif',
            'content': '''
                <p>Understanding the legal framework governing real estate in the UAE is crucial for any investor or homebuyer looking to enter this dynamic market.</p>
                
                <h3>Freehold vs Leasehold</h3>
                <p>Learn the difference between freehold areas where foreigners can own property outright and leasehold areas with long-term lease agreements.</p>
                
                <h3>Registration Process</h3>
                <p>All property transactions must be registered with the Dubai Land Department or relevant authority to ensure legal ownership.</p>
                
                <h3>RERA Regulations</h3>
                <p>The Real Estate Regulatory Agency (RERA) oversees all real estate activities, protecting both buyers and sellers in transactions.</p>
            '''
        },
        {
            'id': 4,
            'title': 'Investment Tips for First-Time Buyers',
            'excerpt': 'Essential advice and strategies for those entering the UAE property market for the first time.',
            'date': 'Nov 12, 2025',
            'author': 'John Smith',
            'image': 'img/hero.avif',
            'content': '''
                <p>Entering the real estate market for the first time can be overwhelming. Here are key tips to help you make smart investment decisions.</p>
                
                <h3>Set a Realistic Budget</h3>
                <p>Calculate your budget including down payment, monthly installments, maintenance fees, and additional costs like registration and agency fees.</p>
                
                <h3>Location is Key</h3>
                <p>Choose locations with strong growth potential, good infrastructure, and proximity to key amenities like schools, hospitals, and transportation.</p>
                
                <h3>Research the Developer</h3>
                <p>Invest with reputable developers who have a proven track record of delivering quality projects on time.</p>
            '''
        },
        {
            'id': 5,
            'title': 'Abu Dhabi\'s Emerging Property Hotspots',
            'excerpt': 'Explore the up-and-coming areas in Abu Dhabi that offer excellent investment potential and quality of life.',
            'date': 'Nov 10, 2025',
            'author': 'Ahmed Hassan',
            'image': 'img/hero.avif',
            'content': '''
                <p>Abu Dhabi is experiencing rapid development with several emerging neighborhoods becoming prime investment destinations.</p>
                
                <h3>Yas Island</h3>
                <p>Home to world-class entertainment and leisure facilities, Yas Island continues to attract investors with its diverse residential offerings.</p>
                
                <h3>Saadiyat Island</h3>
                <p>Known as the cultural district of Abu Dhabi, Saadiyat Island offers luxury living combined with art, culture, and natural beauty.</p>
                
                <h3>Reem Island</h3>
                <p>This modern development offers a perfect blend of residential, commercial, and recreational facilities with stunning waterfront views.</p>
            '''
        },
        {
            'id': 6,
            'title': 'Financing Your Off-Plan Property Purchase',
            'excerpt': 'Understanding mortgage options, payment plans, and financial strategies for off-plan property investments.',
            'date': 'Nov 8, 2025',
            'author': 'Lisa Chen',
            'image': 'img/hero.avif',
            'content': '''
                <p>Financing an off-plan property requires careful planning and understanding of available options to make the most of your investment.</p>
                
                <h3>Developer Payment Plans</h3>
                <p>Many developers offer flexible payment plans allowing you to pay in installments during the construction period, typically with minimal or no interest.</p>
                
                <h3>Mortgage Options</h3>
                <p>UAE banks offer competitive mortgage rates for off-plan properties, usually requiring 20-25% down payment for expatriates.</p>
                
                <h3>Investment Returns</h3>
                <p>Off-plan properties often offer better ROI compared to ready properties, with potential for capital appreciation and rental income.</p>
            '''
        },
    ]
    
    context = {
        'page_title': 'Blog - Off Plan UAE',
        'meta_description': 'Latest news and insights about UAE real estate',
        'blog_posts': blog_posts
    }
    return render(request, 'main/blog.html', context)


def blog_detail(request, blog_id):
    """Render individual blog post detail page"""
    blog_posts = [
        {
            'id': 1,
            'title': 'Top 10 Off-Plan Developments in Dubai 2025',
            'excerpt': 'Explore the most promising off-plan projects launching this year in Dubai\'s thriving real estate market. Discover exclusive opportunities.',
            'date': 'Nov 20, 2025',
            'author': 'Sarah Ahmed',
            'image': 'img/hero.avif',
            'content': '''
                <p>Dubai's real estate market continues to flourish with groundbreaking off-plan developments that redefine luxury living. In this comprehensive guide, we explore the top 10 projects that are set to transform the emirate's skyline in 2025.</p>
                
                <h3>1. Palm Residences - Nakheel</h3>
                <p>Located on the iconic Palm Jumeirah, this development offers unparalleled beachfront living with world-class amenities and stunning Arabian Gulf views.</p>
                
                <h3>2. Downtown Villas - Damac Properties</h3>
                <p>Experience urban sophistication in the heart of Downtown Dubai with these premium villas featuring contemporary design and smart home technology.</p>
                
                <h3>3. Marina Heights - Emaar Properties</h3>
                <p>Rising high in Dubai Marina, these luxury apartments offer breathtaking views and direct access to the finest dining and entertainment venues.</p>
                
                <p>Each of these developments represents the pinnacle of modern architecture and lifestyle convenience, making them excellent investment opportunities for both end-users and investors.</p>
            '''
        },
        {
            'id': 2,
            'title': 'How AI is Transforming Property Investment',
            'excerpt': 'Discover how artificial intelligence is revolutionizing the way investors find and evaluate real estate opportunities in the UAE market.',
            'date': 'Nov 18, 2025',
            'author': 'Michael Johnson',
            'image': 'img/hero.avif',
            'content': '''
                <p>Artificial Intelligence is reshaping the real estate industry, bringing unprecedented efficiency and insights to property investment decisions.</p>
                
                <h3>Predictive Analytics</h3>
                <p>AI algorithms analyze vast amounts of market data to predict price trends, helping investors make informed decisions about when and where to invest.</p>
                
                <h3>Property Valuation</h3>
                <p>Machine learning models can accurately assess property values by considering multiple factors including location, amenities, market trends, and historical data.</p>
                
                <h3>Personalized Recommendations</h3>
                <p>AI-powered platforms like OffPlanUAE.ai can match investors with properties that perfectly align with their investment goals and preferences.</p>
            '''
        },
        {
            'id': 3,
            'title': 'Understanding UAE Real Estate Laws',
            'excerpt': 'A comprehensive guide to navigating property ownership regulations and legal requirements in the United Arab Emirates.',
            'date': 'Nov 15, 2025',
            'author': 'Fatima Al-Mansoori',
            'image': 'img/hero.avif',
            'content': '''
                <p>Understanding the legal framework governing real estate in the UAE is crucial for any investor or homebuyer looking to enter this dynamic market.</p>
                
                <h3>Freehold vs Leasehold</h3>
                <p>Learn the difference between freehold areas where foreigners can own property outright and leasehold areas with long-term lease agreements.</p>
                
                <h3>Registration Process</h3>
                <p>All property transactions must be registered with the Dubai Land Department or relevant authority to ensure legal ownership.</p>
                
                <h3>RERA Regulations</h3>
                <p>The Real Estate Regulatory Agency (RERA) oversees all real estate activities, protecting both buyers and sellers in transactions.</p>
            '''
        },
        {
            'id': 4,
            'title': 'Investment Tips for First-Time Buyers',
            'excerpt': 'Essential advice and strategies for those entering the UAE property market for the first time.',
            'date': 'Nov 12, 2025',
            'author': 'John Smith',
            'image': 'img/hero.avif',
            'content': '''
                <p>Entering the real estate market for the first time can be overwhelming. Here are key tips to help you make smart investment decisions.</p>
                
                <h3>Set a Realistic Budget</h3>
                <p>Calculate your budget including down payment, monthly installments, maintenance fees, and additional costs like registration and agency fees.</p>
                
                <h3>Location is Key</h3>
                <p>Choose locations with strong growth potential, good infrastructure, and proximity to key amenities like schools, hospitals, and transportation.</p>
                
                <h3>Research the Developer</h3>
                <p>Invest with reputable developers who have a proven track record of delivering quality projects on time.</p>
            '''
        },
        {
            'id': 5,
            'title': 'Abu Dhabi\'s Emerging Property Hotspots',
            'excerpt': 'Explore the up-and-coming areas in Abu Dhabi that offer excellent investment potential and quality of life.',
            'date': 'Nov 10, 2025',
            'author': 'Ahmed Hassan',
            'image': 'img/hero.avif',
            'content': '''
                <p>Abu Dhabi is experiencing rapid development with several emerging neighborhoods becoming prime investment destinations.</p>
                
                <h3>Yas Island</h3>
                <p>Home to world-class entertainment and leisure facilities, Yas Island continues to attract investors with its diverse residential offerings.</p>
                
                <h3>Saadiyat Island</h3>
                <p>Known as the cultural district of Abu Dhabi, Saadiyat Island offers luxury living combined with art, culture, and natural beauty.</p>
                
                <h3>Reem Island</h3>
                <p>This modern development offers a perfect blend of residential, commercial, and recreational facilities with stunning waterfront views.</p>
            '''
        },
        {
            'id': 6,
            'title': 'Financing Your Off-Plan Property Purchase',
            'excerpt': 'Understanding mortgage options, payment plans, and financial strategies for off-plan property investments.',
            'date': 'Nov 8, 2025',
            'author': 'Lisa Chen',
            'image': 'img/hero.avif',
            'content': '''
                <p>Financing an off-plan property requires careful planning and understanding of available options to make the most of your investment.</p>
                
                <h3>Developer Payment Plans</h3>
                <p>Many developers offer flexible payment plans allowing you to pay in installments during the construction period, typically with minimal or no interest.</p>
                
                <h3>Mortgage Options</h3>
                <p>UAE banks offer competitive mortgage rates for off-plan properties, usually requiring 20-25% down payment for expatriates.</p>
                
                <h3>Investment Returns</h3>
                <p>Off-plan properties often offer better ROI compared to ready properties, with potential for capital appreciation and rental income.</p>
            '''
        },
    ]
    
    blog_post = None
    for post in blog_posts:
        if post['id'] == blog_id:
            blog_post = post
            break
    
    if not blog_post:
        messages.error(request, 'Blog post not found.')
        return redirect('main:blog')
    
    related_posts = [post for post in blog_posts if post['id'] != blog_id][:3]
    
    context = {
        'page_title': f'{blog_post["title"]} - Blog',
        'meta_description': blog_post['excerpt'],
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


def properties(request):
    project = Property.objects.all()
    logo = Developer.objects.all()
    
    price_filter = request.GET.get('price', '')
    
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
    
    paginator = Paginator(project, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'project': page_obj,
        'logo': logo,
        'types': PropertyType.objects.all().exclude(name__iexact='Unknown Type'),
        'developers': Developer.objects.all(),
        'location': City.objects.all().exclude(name__iexact='Unnamed City'),
        'status': SalesStatus.objects.all(),
        'selected_price': price_filter,
    }
    return render(request, 'main/properties.html', context)


def properties_detail(request, slug):
    property_obj = (Property.objects.select_related(
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
    
    if property_obj.address:
        try:
            lat, lng = [coord.strip() for coord in property_obj.address.split(',')]
        except Exception:
            lat, lng = None, None
    else:
        lat, lng = None, None
    
    if not property_obj:
        return render(request, "404.html", status=404)
    
    text = strip_tags(property_obj.description or "")
    text = text.replace("&nbsp;", "").replace("\xa0", " ")
    property_obj.description = text
    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        messages.success(request, "Thank you! We will contact you soon.")
        return redirect("main:properties_detail", slug=slug)
    
    context = {
        "property": property_obj,
        "page_title": f"{property_obj.title} - Property Details",
        "meta_description": property_obj.description[:160] if property_obj.description else "",
        "images": property_obj.property_images.all(),
        "units": property_obj.grouped_apartments.all(),
        "facilities": property_obj.facilities.all(),
        'lat': lat,
        'lng': lng,
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
