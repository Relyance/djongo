from django.urls import path
from . import views

urlpatterns = [
    path('create_user/', views.create_user, name='create_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('session_check/', views.session_check, name='session_check'),
    path('protected/', views.protected_view, name='protected'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_user_to_group/<int:user_id>/<str:group_name>/', views.add_user_to_group, name='add_user_to_group'),
    path('remove_user_from_group/<int:user_id>/<str:group_name>/', views.remove_user_from_group, name='remove_user_from_group'),
    path('add_permission_to_user/<int:user_id>/<str:perm_codename>/', views.add_permission_to_user, name='add_permission_to_user'),
    path('remove_permission_from_user/<int:user_id>/<str:perm_codename>/', views.remove_permission_from_user, name='remove_permission_from_user'),
]
