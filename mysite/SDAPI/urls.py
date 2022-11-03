from . import views
from django.urls import path

urlpatterns = [
    path("<int:seed_val>/<int:guidance_scale>/<int:height>/<int:width>/<int:steps>/<str:prompt_txt>/",
    views.SDAPI_request, name="show"),
    path("media/", views.test_imshow),
]