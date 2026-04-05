import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    u = User.objects.get(username='admin')
    u.set_password('admin123')
    u.save()
    print("Password resett successful!")
except User.DoesNotExist:
    u = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created!")
