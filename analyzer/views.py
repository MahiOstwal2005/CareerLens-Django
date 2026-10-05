from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Resume, ATSResult
from .forms import ResumeUploadForm
from .utils.extractor import extract_text_from_file
from .utils.ats_scorer import calculate_ats_score
import os
import datetime
from pymongo import MongoClient
from django.conf import settings

# Initialize MongoDB client
try:
    mongo_client = MongoClient(settings.MONGO_URI)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
except Exception as e:
    print("MongoDB connection error:", e)

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = ResumeUploadForm()
    return render(request, 'analyzer/index.html', {'form': form})

@login_required
def dashboard(request):
    # Retrieve resumes for the user
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    # Calculate highest ATS score
    from django.db.models import Max
    highest_score = ATSResult.objects.filter(resume__in=resumes).aggregate(max_score=Max('score'))['max_score']
    # Build score history for chart (date, score)
    score_history = []
    for res in resumes:
        try:
            ats = ATSResult.objects.get(resume=res)
            score_history.append({
                'date': res.uploaded_at.date().strftime('%Y-%m-%d'),
                'score': ats.score,
            })
        except ATSResult.DoesNotExist:
            continue
    # Determine health tier based on highest score
    if highest_score is None:
        health_tier = 'No Data'
        tier_color = 'secondary'
    elif highest_score < 40:
        health_tier = 'Novice'
        tier_color = 'danger'
    elif highest_score < 60:
        health_tier = 'Emerging'
        tier_color = 'warning'
    elif highest_score < 80:
        health_tier = 'Competitive'
        tier_color = 'info'
    elif highest_score < 90:
        health_tier = 'Proficient'
        tier_color = 'primary'
    else:
        health_tier = 'Top 1%'
        tier_color = 'success'
    # Action items from the latest ATS result feedback
    latest_result = ATSResult.objects.filter(resume__in=resumes).order_by('-analyzed_at').first()
    action_items = []
    if latest_result:
        # Simple split on newlines or bullet points
        for line in latest_result.feedback.split('\n'):
            line = line.strip('-•* ').strip()
            if line:
                action_items.append(line)
    # Build dates and scores arrays for Chart.js
    score_dates = [h['date'] for h in score_history]
    score_scores = [h['score'] for h in score_history]
    # Context now includes chart data and health tier info
    context = {
        'resumes': resumes,
        'highest_score': highest_score,
        'health_tier': health_tier,
        'tier_color': tier_color,
        'score_history': score_history,
        'score_chart_data': {'dates': score_dates, 'scores': score_scores},
        'action_items': action_items,
    }
    return render(request, 'analyzer/dashboard_home.html', context);

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            
            # Get user profile and tier
            from users.models import UserProfile
            from django.utils import timezone
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            tier = profile.tier
            
            # Reset monthly resume limit if it's a new month
            now = timezone.now().date()
            if profile.last_scan_reset_date.month != now.month or profile.last_scan_reset_date.year != now.year:
                profile.resumes_scanned_this_month = 0
                profile.last_scan_reset_date = now
                profile.save()

            if tier == 'free':
                from django.contrib import messages
                
                if resume.doc_type == 'portfolio':
                    if profile.portfolios_scanned_total >= 1:
                        messages.error(request, 'You have used your 1 free Portfolio scan! Upgrade to Pro for unlimited scans.')
                        return redirect('pricing')
                    else:
                        profile.portfolios_scanned_total += 1
                        profile.save()
                        
                elif resume.doc_type == 'resume':
                    if profile.resumes_scanned_this_month >= 5:
                        messages.error(request, 'You have reached your limit of 5 free resume scans this month. Upgrade to Pro for unlimited scans!')
                        return redirect('pricing')
                    else:
                        profile.resumes_scanned_this_month += 1
                        profile.save()
                
            resume.user = request.user
            resume.save()
            
            # Extract text
            from .utils.extractor import extract_text_from_file, extract_text_from_url
            extracted_text = ""
            if resume.file:
                file_path = resume.file.path
                extracted_text = extract_text_from_file(file_path)
            elif resume.portfolio_url:
                extracted_text = extract_text_from_url(resume.portfolio_url)
                
            if not extracted_text:
                from django.contrib import messages
                messages.error(request, "We couldn't extract any text from the provided file or URL.")
                return redirect('dashboard')
                
            resume.extracted_text = extracted_text
            resume.save()
            
            # Calculate ATS Score
            result_data = calculate_ats_score(extracted_text, doc_type=resume.doc_type)
            
            ATSResult.objects.create(
                resume=resume,
                score=result_data['score'],
                matched_keywords=result_data['matched_keywords'],
                missing_keywords=result_data['missing_keywords'],
                feedback=result_data['feedback']
            )
            
                        # Save Resume and ATS Result to MongoDB clean without nulls
            doc_data = {
                'username': request.user.username,
                'doc_type': resume.doc_type,
                'uploaded_at': datetime.datetime.now(),
                'extracted_text': extracted_text[:500] + '...',
                'score': result_data['score'],
                'matched_keywords': result_data['matched_keywords'],
                'missing_keywords': result_data['missing_keywords'],
                'feedback': result_data['feedback'],
                'comprehensive_report': result_data.get('comprehensive_report', {})
            }
            if resume.file:
                doc_data['file_name'] = resume.file.name
            if resume.portfolio_url:
                doc_data['portfolio_url'] = resume.portfolio_url
                
            try:
                if resume.doc_type == 'portfolio':
                    mongo_db.portfolios.insert_one(doc_data)
                else:
                    mongo_db.resumes.insert_one(doc_data)
            except Exception as e:
                print("Failed to save to MongoDB:", e)
            
            return redirect('result', pk=resume.pk)
    else:
        form = ResumeUploadForm()
        
    from users.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    resumes_remaining = max(0, 5 - profile.resumes_scanned_this_month)
    portfolios_remaining = max(0, 1 - profile.portfolios_scanned_total)
        
    return render(request, 'analyzer/upload.html', {
        'form': form,
        'tier': profile.tier,
        'resumes_remaining': resumes_remaining,
        'portfolios_remaining': portfolios_remaining
    })

@login_required
def history(request):
    documents = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    
    total_uploaded = documents.count()
    total_resumes = documents.filter(doc_type='resume').count()
    total_portfolios = documents.filter(doc_type='portfolio').count()
    
    context = {
        'resumes': documents,
        'total_uploaded': total_uploaded,
        'total_resumes': total_resumes,
        'total_portfolios': total_portfolios
    }
    return render(request, 'analyzer/history.html', context)

@login_required
def pricing(request):
    from users.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'analyzer/pricing.html', {'tier': profile.tier})

@login_required
def result(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    ats_result = get_object_or_404(ATSResult, resume=resume)
    
    mongo_report = None
    try:
        if resume.doc_type == 'portfolio':
            # Match by file_name if uploaded, else by portfolio_url
            query = {'username': request.user.username}
            if resume.file:
                query['file_name'] = resume.file.name
            else:
                query['portfolio_url'] = resume.portfolio_url
            mongo_report = mongo_db.portfolios.find_one(query, sort=[('uploaded_at', -1)])
        else:
            mongo_report = mongo_db.resumes.find_one({
                'username': request.user.username,
                'file_name': resume.file.name
            }, sort=[('uploaded_at', -1)])
    except Exception as e:
        print("Failed to fetch from MongoDB:", e)
        
    tier = request.user.profile.tier if hasattr(request.user, 'profile') else 'free'
    if tier == 'free':
        comprehensive_report = {}
    else:
        comprehensive_report = mongo_report.get('comprehensive_report', {}) if mongo_report else {}
    
    return render(request, 'analyzer/result.html', {
        'resume': resume,
        'ats_result': ats_result,
        'report': comprehensive_report,
        'tier': tier
    })

import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request, plan):
    cycle = request.GET.get('cycle', 'monthly')
    
    # Map plans to prices and names
    plan_details = {
        'pro': {'name': 'Pro Plan', 'price': 999, 'annual_price': 9900},
        'premium': {'name': 'Premium Plan', 'price': 2999, 'annual_price': 29900}
    }
    
    if plan not in plan_details:
        plan = 'pro'
        
    details = plan_details[plan]
    current_price = details['annual_price'] if cycle == 'annual' else details['price']

    # Dummy implementation for testing if no stripe keys are provided or they are masked
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == 'sk_test_dummy' or settings.STRIPE_SECRET_KEY == '********************':
        return render(request, 'analyzer/mock_checkout.html', {
            'plan_name': details['name'],
            'plan_price': current_price / 100,
            'plan_id': plan,
            'cycle': cycle
        })
        
    # Real Stripe implementation
    domain_url = request.build_absolute_uri('/')[:-1]
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            success_url=domain_url + f'/analyzer/success?session_id={{CHECKOUT_SESSION_ID}}&plan={plan}',
            cancel_url=domain_url + '/analyzer/cancel/',
            payment_method_types=['card'],
            mode='subscription',
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': details['name'] + f" ({cycle.capitalize()})",
                        },
                        'unit_amount': current_price,
                        'recurring': {
                            'interval': 'month' if cycle == 'monthly' else 'year',
                        },
                    },
                    'quantity': 1,
                }
            ]
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def downgrade_to_free(request):
    from users.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.tier = 'free'
    profile.save()
    from django.contrib import messages
    messages.success(request, "Successfully downgraded to Free Plan.")
    return redirect('manage_plan')

@login_required
def manage_plan(request):
    from users.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    resumes_used = profile.resumes_scanned_this_month
    portfolios_used = profile.portfolios_scanned_total
    total_scans = Resume.objects.filter(user=request.user).count()
    
    return render(request, 'analyzer/manage_plan.html', {
        'profile': profile,
        'resumes_used': resumes_used,
        'portfolios_used': portfolios_used,
        'total_scans': total_scans
    })

@login_required
def payment_success(request):
    # Retrieve the session
    session_id = request.GET.get('session_id')
    plan = request.GET.get('plan', 'pro')
    
    from users.models import UserProfile
    from django.contrib import messages
    
    # Handle Mock Checkout Success
    if session_id == 'cs_test_mock_dummy_session_123':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.tier = plan
        profile.stripe_customer_id = 'mock_customer_id'
        profile.stripe_subscription_id = 'mock_sub_id'
        profile.save()
        messages.success(request, f"Successfully upgraded to {plan.capitalize()}!")
        return redirect('manage_plan')

    # Handle Real Stripe Checkout Success
    if session_id and settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != 'sk_test_dummy' and settings.STRIPE_SECRET_KEY != '********************':
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.tier = plan
                profile.stripe_customer_id = session.customer
                profile.stripe_subscription_id = session.subscription
                profile.save()
                messages.success(request, f"Successfully upgraded to {plan.capitalize()}!")
        except Exception as e:
            print("Error retrieving session", e)
            
    return redirect('manage_plan')

@login_required
def payment_cancel(request):
    from django.contrib import messages
    messages.warning(request, "Payment was cancelled.")
    return redirect('pricing')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handled in success_url typically, but good to have here as well
    return HttpResponse(status=200)

