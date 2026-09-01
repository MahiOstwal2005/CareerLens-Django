# Empty migration to fix unapplied migration state
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('analyzer', '0001_initial')]
    operations = []
