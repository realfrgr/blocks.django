from django.shortcuts import render , get_object_or_404 , redirect
from django.views.generic import UpdateView
from django.http import HttpResponse , JsonResponse , HttpResponseRedirect , HttpResponseForbidden
from .models import Post , Tournament , TournamentMatch
from .forms import PostForm , RegistrationForm, TournamentForm
from django.urls import reverse_lazy , reverse
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import random
import math


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
   
@login_required
def tournament_list_view(request):
    tournaments = Tournament.objects.all().order_by('-created_at')
    return render(request, "tournament_list.html", {"tournaments": tournaments})

@login_required
def tournament_create_view(request):
    # Only staff/admin should create tournaments
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can create tournaments.")
        
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tournament_list")
    else:
        form = TournamentForm()
    return render(request, "tournament_create.html", {"form": form})

@login_required
def tournament_join_view(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    
    if tournament.is_active or tournament.is_finished:
        return HttpResponse("Tournament already started or finished.")
        
    if request.user in tournament.participants.all():
        return HttpResponse("You have already joined.")

    if tournament.participants.count() < tournament.max_participants:
        tournament.participants.add(request.user)
        
        # Check if full, then start
        if tournament.participants.count() == tournament.max_participants:
            start_tournament(tournament)
            
        return redirect("tournament_detail", id=id)
    else:
        return HttpResponse("Tournament is full.")

def start_tournament(tournament):
    participants = list(tournament.participants.all())
    random.shuffle(participants)
    
    # Generate Round 1
    # Pair up: (0,1), (2,3), etc.
    match_num = 1
    for i in range(0, len(participants), 2):
        TournamentMatch.objects.create(
            tournament=tournament,
            round_number=1,
            match_number=match_num,
            player1=participants[i],
            player2=participants[i+1]
        )
        match_num += 1
        
    tournament.is_active = True
    tournament.save()

@login_required
def tournament_detail_view(request, id):
    tournament = get_object_or_404(Tournament, id=id)
    matches = tournament.matches.all().order_by('round_number', 'match_number')
    
    # Group by round for the template
    rounds = {}
    for match in matches:
        if match.round_number not in rounds:
            rounds[match.round_number] = []
        rounds[match.round_number].append(match)
        
    return render(request, "tournament_detail.html", {
        "tournament": tournament, 
        "rounds": rounds
    })

@login_required
def set_match_winner(request, match_id):
    # Only staff can declare winners
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can referee matches.")
        
    match = get_object_or_404(TournamentMatch, id=match_id)
    
    if request.method == "POST":
        winner_id = request.POST.get("winner_id")
        winner = get_object_or_404(match.tournament.participants, id=winner_id)
        
        if match.winner:
            return HttpResponse("Winner already set.")
            
        match.winner = winner
        match.save()
        
        # Logic to advance winner to next round
        advance_winner(match)
        
        return redirect("tournament_detail", id=match.tournament.id)
        
    return HttpResponse("Method not allowed")

def advance_winner(match):
    tournament = match.tournament
    current_round = match.round_number
    current_match_num = match.match_number
    
    # Calculate next match position
    # Match 1 and 2 of Round 1 -> Match 1 of Round 2
    # Match 3 and 4 of Round 1 -> Match 2 of Round 2
    next_round = current_round + 1
    next_match_num = math.ceil(current_match_num / 2)
    
    # If this was the final, mark tournament finished
    # (Simplified: if only 1 match in this round and it has a winner)
    matches_in_round = tournament.matches.filter(round_number=current_round).count()
    if matches_in_round == 1:
        tournament.is_finished = True
        tournament.winner = match.winner
        tournament.save()
        return

    # Get or create the next match slot
    next_match, created = TournamentMatch.objects.get_or_create(
        tournament=tournament,
        round_number=next_round,
        match_number=next_match_num
    )
    
    # Determine if winner goes to player1 or player2 slot
    # Odd match number -> Player 1 slot, Even match number -> Player 2 slot
    if current_match_num % 2 != 0:
        next_match.player1 = match.winner
    else:
        next_match.player2 = match.winner
    
    next_match.save()








