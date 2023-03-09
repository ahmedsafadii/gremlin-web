"""chatbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from gremlin.settings_dev import SECRET_ADMIN_URL, DEBUG
from api.v1.app import urls as app
from api.v1.user import urls as user
from api.v1.assistant import urls as assistant

admin.site.site_header = _("Gremlin Control Panel")
admin.site.index_title = _("Gremlin Control Panel")
admin.site.site_title = _("Gremlin AI")

urlpatterns = i18n_patterns(
    path(SECRET_ADMIN_URL + "/dashboard/", admin.site.urls),
)

urlpatterns += [
    path("i18n/", include("django.conf.urls.i18n"), name="app"),
    path("api/v1/app/", include(app.urlpatterns)),
    path("api/v1/user/", include(user.urlpatterns)),
    path("api/v1/assistant/", include(assistant.urlpatterns)),
]

if DEBUG:
    # urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
