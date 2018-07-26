"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from mylibrary import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('user.urls')),
    path('signup/', views.signup),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),
    path('books/', views.books),
    path('search/', views.search),
    path('book_manage/', views.book_manage),
    path('card/', views.card),
    #path('delete_card/<int:cno>', views.delete_card, name="delete_card")
    path('borrow_book/', views.borrow_book),
    path('books/sort_books/', views.sort_books),
    path('return_book/', views.return_book),
]
