from django.urls import path
from .views import RegisterAPIView, LoginAPIView, UserDetailsAPIView, UserDetailedAPIView, LogDeletionView, SearchUserAPIView

urlpatterns = [
    path('login',LoginAPIView.as_view()),
    path('signup',RegisterAPIView.as_view()),
    path('deleteuser/<int:id>', UserDetailsAPIView.as_view()),
    path('updateuser/<int:id>',UserDetailsAPIView.as_view()),
    path('getalluser',UserDetailsAPIView.as_view()),
    path('getuser/<int:id>',UserDetailedAPIView.as_view()),
    path('deletelogs/<int:id>',LogDeletionView.as_view()),
    path('users/search/', SearchUserAPIView.as_view()),
]
