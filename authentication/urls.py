from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register_user'),
    path('login/', LoginUser.as_view(), name='login_user'),
    
    path('user_info/', UserInfoView.as_view(), name='user_info'),
    path('get_alluser_info/', AllUserDataView.as_view(), name='get_alluser_info'),
    path('user_data/', UserDataListView.as_view(), name='user_data_list'),  
    path('user_data/create/', UserDataCreateView.as_view(), name='user_data_create'),  
    path('user_data/<int:pk>/update/', UserDataUpdateView.as_view(), name='user_data_update'),  
    path('user_data/<int:pk>/delete/', UserDataDeleteView.as_view(), name='user_data_delete'),  
    

]

