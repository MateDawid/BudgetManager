from app_users.views.authenticated_user_view import AuthenticatedUserView
from app_users.views.create_token_view import CreateTokenView
from app_users.views.create_user_view import CreateUserView
from app_users.views.list_user_view import ListUserView
from django.urls import path

app_name = 'app_users'

urlpatterns = [
    path('', ListUserView.as_view(), name='list'),
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateTokenView.as_view(), name='token'),
    path('me/', AuthenticatedUserView.as_view(), name='me'),
]
