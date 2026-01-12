from django.shortcuts import render , get_object_or_404 , redirect
from django.views.generic import UpdateView
from django.http import HttpResponse , JsonResponse , HttpResponseRedirect
from .models import Post
from .forms import PostForm , RegistrationForm
from django.urls import reverse_lazy , reverse
from django.views import View
from django.contrib.auth import logout


def index_view(request):
    posts=Post.objects.all()
    return render(request,"home.html",{"posts":posts})

def profile_view(request):
    return render(request,"profile.html")

def friends_view(request):
    return render(request,"friends.html")

def posts_view(request):
    

    if request.GET.get("sort")=="1":
        posts=Post.objects.filter(author=request.user).order_by("-created_at")
    else:
        posts=Post.objects.filter(author=request.user)
    return render(request,"posts.html",{"posts":posts})

def signup_system(request):
    return render(request,"signup.html")

def login(request):
    return render(request,"login.html")

def post_id(request,id):
    postid=Post.objects.get(id=id)


    return render(request,"post_id.html",{"post":postid})

def post_delete(request,id):
    post= get_object_or_404(Post,id=id)
    if request.method=="POST":
        post.delete()
        return redirect("posts_view")
    return render(request,"post_delete.html",{"post":post})

def post_create_view(request):
    form=PostForm()
    if request.method=="POST":
        title=request.POST.get("title")
        content=request.POST.get("content")
        author=request.user
        post=Post(title=title,content=content,author=author)
        post.save()
        return redirect("posts_view")
    return render(request,"post_create.html",{"form":form})

class UpdatePostView(UpdateView):
    model=Post
    template_name="post_edit.html"
    fields=["title","content"]
    
    
    def get_success_url(self):
        return reverse_lazy("posts_view")

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect("index_view")


def regist_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return  redirect("login")
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form}) 

def post_sort_api(request):
    sort_by = request.GET.get("sort","newest")
    if sort_by == "newest":
        posts = Post.objects.filter(author=request.user).order_by("-created_at")
    elif sort_by == "oldest":
         posts = Post.objects.filter(author=request.user).order_by("created_at")
    elif sort_by == "title":
        posts = Post.objects.filter(author=request.user).order_by("title")
    else:
        return JsonResponse({"Error" : "Wrong sort parameter"})
    

    post_list=[
        {"title":post.title,
         "content":post.content ,
         "created_at":post.created_at,
         "author":post.author.id }
         for post in posts
         ]
    print(post_list)
    return JsonResponse({"posts":post_list})

def likepost(request,id):
    
    print(request.POST)
    post = get_object_or_404(Post,id=id)
    print(post)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return JsonResponse({"total_likes":post.total_likes()})
   








