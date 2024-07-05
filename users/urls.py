from django.urls import path
from django.contrib.auth import views as auth_views
from .views.allauth_views import CustomPasswordSetView
from .views.views import *
# from .views.custom_login_V import CustomLoginView
from .admin_views.custom_user_assign_view_V import *
from .admin_views.users_detail_views import *
from .admin_views.users_list_views import *
from .admin_views.create_users_groups_V import *


urlpatterns = [
    # path('', home, name='home'),
    # path('register/', register, name='signup'),
    # path('profile_home/', profile_home, name='profile-home'),
    path('your/profile/', profile, name='profile'),
    path('profile/Edit/', profile_edit, name='profile_edit'),
    path('delete-account/', login_required(DeleteAccountView.as_view()), name='delete_account'),
    # path('login/', CustomLoginView.as_view(), name='custom_login'),
    # CustomPasswordSetView IS FOR ADDING MORE FUNCTIONALITY TO THE ORIGINAL 
    # DJANGO-ALLAUTH PASSWORDS_SET VIEW
    path('password/set/', CustomPasswordSetView.as_view(), name='account_set_password'),
    
    # ========ADMIN URLS VIEWS=======================
    path('assign_group/<int:user_id>/', assign_user_group, name='assign_user_group'),
    
    path('users/list/', user_list, name='user_list'),
    path('user/profile/<int:user_id>/', user_detail, name='user_detail'),
    path('user/profile-edit/<int:user_id>/', user_edit, name='user_edit'),
    path('user/profile-edit/<int:user_id>/', custom_admin_view, name='custom_admin_view'),
    
    path('groups/', group_list_view, name='group_list'),
    path('group/<int:pk>/', group_detail, name='group_detail'),
    path('group edit/<int:pk>/', add_group, name='add_group'),
    path('add group/', add_group, name='add_group'),
    # path('login/', auth_views.LoginView(template_name='users/login.html'), name='login'),

    # path('logout/', auth_views.LogoutView(template_name='users/logout.html'), name='logout'),
]