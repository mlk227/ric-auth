"""ric_auth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from profiles import views as profiles_views
from ric_auth.tasks import GetTaskProgressView

router = routers.DefaultRouter()
router.register(r'CustomUser', profiles_views.CustomUserViewSet)
router.register(r'organization', profiles_views.OrganizationViewSet)
router.register(r'password_reminder_question', profiles_views.PasswordReminderQuestionsViewSet)
router.register(r'password_reminder', profiles_views.PasswordReminderViewSet)
router.register(r'group', profiles_views.GroupViewSet)
router.register(r'email_reset', profiles_views.EmailResetViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]

# JWT auth views
urlpatterns += [
    path('api/token/', profiles_views.RicAuthTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', profiles_views.RicAuthTokenRefreshView.as_view(), name='token_refresh'),
    path('api/task_progress/<slug:task_id>', GetTaskProgressView.as_view(), name="task_progress"),
    path('api/random_user_avatar/', profiles_views.RandomUserAvatarViewSet.as_view(), name='random_user_avatar'),
]

# drf_spectacular schema view
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
