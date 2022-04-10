
from django.urls import path

from .views import *

urlpatterns = [
    path("saml2/login/", login, name="login"),
    path("saml2/acs/", assertion_consumer_service, name="acs"),
]
