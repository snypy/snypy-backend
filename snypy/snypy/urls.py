"""snypy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

from rest_registration.api.views import register, verify_registration


# Invoked to load REST URLs
from core.utils.rest_router import router
from snippets import urls as snippets_urls
from teams import urls as teams_urls
from users import urls as users_urls


from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    # Rest Routes
    path(
        "api/v1/",
        include(
            [
                path("", include(router.urls)),
                path(
                    "schema/",
                    include(
                        [
                            path("", SpectacularAPIView.as_view(), name="schema"),
                            # Optional UI:
                            path("swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
                            path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
                        ]
                    ),
                ),
                path(
                    "auth/",
                    include(
                        [
                            path(
                                "token/",
                                include(
                                    ("django_rest_multitokenauth.urls", "django_rest_multitokenauth"),
                                    namespace="multi_token_auth",
                                ),
                            ),
                            url("^register/$", register, name="register"),
                            url("^verify-registration/$", verify_registration, name="verify-registration"),
                        ]
                    ),
                ),
                path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
            ]
        ),
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
