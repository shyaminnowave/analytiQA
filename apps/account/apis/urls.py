from django.urls import path
from apps.account.apis import views


app_name = 'account'

urlpatterns = [
    path('sign-up', views.AccountCreateView.as_view(), name='sign-up'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('profile/<slug:username>', views.UserProfileView.as_view()),
    path('user-list', views.UserListView.as_view()),
    path('user-update/<slug:username>', views.UserUpdateGroup.as_view()),
    path('permissions', views.PermissionListView.as_view()),
    path('group', views.GroupView.as_view()),
    path('create-group/', views.GroupCreateView.as_view()),
    path('group-detail/<int:pk>/', views.GroupDetailView.as_view()),

    # ACTIVATE TOKEN
    path('user/activate', views.UserActivateView.as_view()),

    # REFRESH TOKEN
    path('token/access', views.AccountTokenAccessView.as_view(), name='token_access'),
]
