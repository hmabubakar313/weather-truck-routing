from django.urls import path

from . import views

urlpatterns = [
    path("routes/", views.plan_routes, name="plan-routes"),
]
