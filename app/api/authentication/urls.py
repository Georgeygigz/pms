
from django.urls import path
from .views import RegistrationApiView, LoginAPIView

urlpatterns = [
    path('signup/', RegistrationApiView.as_view(), name='user-registration'),
    path('login/', LoginAPIView.as_view(), name='user-registration'),
]