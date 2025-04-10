"""
    home/swagger.py: Create swagger.py file and add the below code. 
    This code sets up a Swagger schema view for the Django REST Framework API, 
    defining metadata such as title, version, description, terms of service, contact, and license.
    It allows public access and permits any user to view the schema.
"""

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)