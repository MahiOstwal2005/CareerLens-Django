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
            resume.user = request.user
            resume.save()
            
            # Extract text
            file_path = resume.file.path
            extracted_text = extract_text_from_file(file_path)
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
            
            # Save Resume and ATS Result to MongoDB
            try:
                mongo_db.resumes.insert_one({
                    'username': request.user.username,
                    'file_name': resume.file.name,
                    'doc_type': resume.doc_type,
                    'uploaded_at': datetime.datetime.now(),
                    'extracted_text': extracted_text[:500] + '...', # Store a snippet
                    'score': result_data['score'],
                    'matched_keywords': result_data['matched_keywords'],
                    'missing_keywords': result_data['missing_keywords'],
                    'feedback': result_data['feedback'],
                    'detailed_report': result_data.get('detailed_report', {})
                })
            except Exception as e:
                print("Failed to save to MongoDB:", e)
            
            return redirect('result', pk=resume.pk)
    else:
        form = ResumeUploadForm()
        
    return render(request, 'analyzer/upload.html', {'form': form})

@login_required
@login_required
def history(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'analyzer/history.html', {'resumes': resumes})

@login_required
def pricing(request):
    return render(request, 'analyzer/pricing.html')

@login_required
def result(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    ats_result = get_object_or_404(ATSResult, resume=resume)
    
    mongo_report = None
    try:
        mongo_report = mongo_db.resumes.find_one({
            'username': request.user.username,
            'file_name': resume.file.name
        }, sort=[('uploaded_at', -1)])
    except Exception as e:
        print("Failed to fetch from MongoDB:", e)
        
    detailed_report = mongo_report.get('detailed_report', {}) if mongo_report else {}
    
    return render(request, 'analyzer/result.html', {
        'resume': resume,
        'ats_result': ats_result,
        'detailed_report': detailed_report
    })
