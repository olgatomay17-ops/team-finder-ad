from django.urls import path
from . import views


app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='home'),
    path('list/', views.ProjectListView.as_view(), name='list'),
    path('create-project/', views.ProjectCreateView.as_view(), name='create'),
    path('favorites/', views.FavoriteProjectView.as_view(), name='favorites'),
    path('<int:pk>', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/complete/', views.complete_project, name='complete'),
    path('<int:pk>/toggle-participate/',
         views.toggle_participate, name='toggle_participate'),
    path('<int:pk>/toggle-favorite/',
         views.toggle_favorite, name='toggle_favorite'),
]
