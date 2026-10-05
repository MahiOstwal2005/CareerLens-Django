from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserProfileForm
from pymongo import MongoClient
from django.conf import settings

# Initialize MongoDB client
try:
    mongo_client = MongoClient(settings.MONGO_URI)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
except Exception as e:
    print("MongoDB connection error:", e)

from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            # Save User Data to MongoDB
            try:
                mongo_db.users.insert_one({
                    'django_id': user.id,
                    'username': username,
                    'email': email,
                    'role': 'student/job-seeker',
                    'college': None,
                    'program': None,
                    'semester': None,
                    'skills': None,
                    'areas_of_interest': None
                })
            except Exception as e:
                print("Failed to save to MongoDB:", e)
                
            # Log the user in immediately
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Try to fetch some extra data from MongoDB if needed, or just rely on Django user
    mongo_user = None
    try:
        mongo_user = mongo_db.users.find_one({'django_id': request.user.id})
    except Exception as e:
        print("Failed to fetch user from MongoDB:", e)
        
    context = {
        'user': request.user,
        'profile': profile,
        'role': mongo_user.get('role', 'student/job-seeker') if mongo_user else 'student/job-seeker'
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            
            # Update MongoDB
            try:
                mongo_db.users.update_one(
                    {'django_id': request.user.id},
                    {'$set': {
                        'college': profile.college,
                        'program': profile.program,
                        'semester': profile.semester,
                        'skills': profile.skills,
                        'areas_of_interest': profile.areas_of_interest,
                        'portfolio_url': profile.portfolio_url,
                        'resume_link': profile.resume_link
                    }},
                    upsert=True
                )
            except Exception as e:
                print("Failed to update user in MongoDB:", e)
                
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'users/edit_profile.html', {'form': form})

from django.contrib.auth import logout
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_account(request):
    user = request.user
    try:
        mongo_db.users.delete_one({'django_id': user.id})
        mongo_db.resumes.delete_many({'username': user.username})
        mongo_db.portfolios.delete_many({'username': user.username})
    except Exception as e:
        print("Failed to delete user from MongoDB:", e)
    
    # Log out the user to clear the session BEFORE deleting the user object!
    logout(request)
    user.delete()
    
    messages.success(request, 'Your account has been successfully deleted.')
    return redirect('index')

from django.http import JsonResponse

@login_required
@require_POST
def toggle_theme(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return JsonResponse({'status': 'success', 'dark_mode': profile.dark_mode})
