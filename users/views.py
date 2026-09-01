from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from pymongo import MongoClient
from django.conf import settings

# Initialize MongoDB client
try:
    mongo_client = MongoClient(settings.MONGO_URI)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
except Exception as e:
    print("MongoDB connection error:", e)

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
                    'role': 'student/job-seeker'
                })
            except Exception as e:
                print("Failed to save to MongoDB:", e)
                
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
