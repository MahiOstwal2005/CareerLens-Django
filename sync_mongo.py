import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerlens_core.settings')
django.setup()

from users.models import UserProfile
from django.conf import settings
from pymongo import MongoClient

mongo_client = MongoClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

profiles = UserProfile.objects.all()
for profile in profiles:
    mongo_db.users.update_one(
        {'django_id': profile.user.id},
        {'$set': {
            'college': profile.college,
            'program': profile.program,
            'semester': profile.semester,
            'skills': profile.skills,
            'areas_of_interest': profile.areas_of_interest
        }}
    )
print('Successfully synced all existing UserProfile fields to MongoDB.')
