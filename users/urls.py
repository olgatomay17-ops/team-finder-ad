from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('list/', views.UserListView.as_view(), name='list'),
    path('change-password/', views.CustomPasswordChangeView.as_view(),
         name='change_password'),
    path('edit-profile/', views.get_profile_redirect, name='edit_profile'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.UserUdpateView.as_view(), name='edit'),
]
