from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Add a redirect from the root URL to the API root
    path('', RedirectView.as_view(url='/api/', permanent=False)),
]
