from django.urls import path
from . import views
from django.contrib.auth import views as auth_views   # <-- this import was missing

urlpatterns = [
    path('', views.landing, name='landing'),
    path('list/', views.expense_list, name='expense_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('add/', views.add_expense, name='add_expense'),
]