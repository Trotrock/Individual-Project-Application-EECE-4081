from django.contrib import admin
from django.urls import path, include
from matches import views as match_views

urlpatterns = [
    # Routing the empty root path directly to your user-facing standings display!
    path('', match_views.standings_dashboard, name='home'),
    path('admin/', admin.site.urls),
    path('matches/', include('matches.urls')),
]
