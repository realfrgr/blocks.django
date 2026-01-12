
from django.urls import path
from django.contrib.auth.views import LoginView 


from . import views
from .views import UpdatePostView , LogoutView 

urlpatterns = [
    path("main/" , views.index_view, name="index_view"),
    path("profile/" , views.profile_view, name="profile_view"),
    path("posts/" , views.posts_view, name="posts_view"),
    path("friends/" , views.friends_view, name="friends_view"),
    path("signup/" , views.signup_system, name="signup_system"),
    path((""), views.index_view, name="index_view"),
    #path("login/",views.login,name="login"),
    path("post/<int:id>",views.post_id,name="post_id"),
    path("post/<int:id>/delete",views.post_delete,name="post_delete"),
    path('post/create/',views.post_create_view,name="post_create"),
    path("post/edit/<int:pk>",UpdatePostView.as_view(),name="post_edit"),
    path("login/",LoginView.as_view(template_name="login.html"),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("registration/",views.regist_view,name="registration"),
    path("sort-posts/",views.post_sort_api,name="sort_post_api"),
    path("likes/<int:id>/",views.likepost,name="like_post"),

]

