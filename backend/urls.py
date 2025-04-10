from django.urls import path

from backend.views import (
    ClaimView,
    InviteView,
    ListCreateStepsPerDayView,
    UserStepsPerDayView,
    WalkUserView,
)

from .swagger import schema_view

app_name = "backend"


urlpatterns = [
    # for swagger
    # re_path(r"^auth/", include("drf_social_oauth2.urls", namespace="drf")),
    # re_path(r"^auth/", include("drf_social_oauth2.urls", namespace="social")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # path("userisauth/", view=user_is_authenticated),
    path(
        "user/",
        view=WalkUserView.as_view(
            lookup_field="email",
            #     # tell it, i'm querying with uuid
        ),
    ),
    path(
        "steps-today/",
        view=ListCreateStepsPerDayView.as_view(
            # lookup_field="email",
            #     # tell it, i'm querying with uuid
        ),
    ),
    path(
        "user-claims/",
        view=ClaimView.as_view(
            # lookup_field="email",
            #     # tell it, i'm querying with uuid
        ),
    ),
    path(
        "user-invites/",
        view=InviteView.as_view(
            # lookup_field="email",
            #     # tell it, i'm querying with uuid
        ),
    ),
    path(
        "user-step/",
        view=UserStepsPerDayView.as_view(
            # lookup_field="email",
            #     # tell it, i'm querying with uuid
        ),
    ),
]


"""home/urls.py: This Django code imports the admin module for administrative tasks, 
defines URL patterns for the admin interface and Swagger documentation. 
The schema_view is imported from a module named swagger, 
and it's used to render the Swagger UI for API documentation at the '/swagger/' endpoint with zero caching."""
