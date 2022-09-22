from ast import Pass
from ssl import HAS_TLSv1_1
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import LikePost, Profile ,Post, FollowersCount
import random

# Create your views here.


@login_required(login_url="/signin")
def index(request):
    user_profile = Profile.objects.get(user=request.user)

    #user_object = User.objects.get(username = request.user.username)
    #user_profile = Profile.objects.get(user=user_object)

    username_followings=[]
    user_following_lst = FollowersCount.objects.filter(follower = request.user.username)
    for users in user_following_lst:
        username_followings.append(users)
    feed = []

    for usernames in username_followings:
        feed_lst = Post.objects.filter(user=usernames)
        for e in feed_lst:
            feed.append(e)
    
    current_user = User.objects.filter(username = request.user.username)
    feed.append(Post.objects.filter(user=request.user.username)[0])

    user_following_all=[]
    for user in user_following_lst:
        user_lst=User.objects.filter(username=user.user)
        user_following_all.extend(user_lst)

    all_users = User.objects.all()
    final_suggestion_list = [x for x in all_users if not (x in user_following_all or x in current_user)]
    random.shuffle(final_suggestion_list)

    """username_profile_list = []

    for users in final_suggestion_list:

        username_profile_list.append(Profile.objects.get(user = users))"""
    
    username_profile = []
    username_profile_list = []
    
    for users in final_suggestion_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_list = Profile.objects.filter(id_user = ids)
        for w in profile_list:
            username_profile_list.append(w)


    
    return render(request, "index.html",{"user_profile":user_profile,"posts":feed,"username_profile_list":username_profile_list[:4]})

@login_required(login_url="/signin")
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get("image_upload")
        caption = request.POST["caption"]

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect("/")
    else:
        return redirect("/")

    return HttpResponse("<h1>Upload View</h1>")

@login_required(login_url="/signin")
def like_post(request):
    username = request.user.username
    post_id = request.GET.get("post_id")

    post = Post.objects.get(id = post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.no_of_likes += 1
        post.save()

        return redirect("/")

    else:
        like_filter.delete()
        #locate_like = LikePost.objects.get(post_id=post_id, username=username)
        #locate_like.delete()
        post.no_of_likes -= 1
        post.save()

        return redirect("/")

@login_required(login_url="/signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    if request.method == "POST":
        username = request.POST["username"]
        username_object = User.objects.filter(username__icontains = username)

        username_profile_list=[]

        for users in username_object:
            username_profile_list.append(Profile.objects.get(user = users))
            

    
    
    return render(request, "search.html", {"user_profile":user_profile, "username_profile_list":username_profile_list})


@login_required(login_url="/signin")
def profile(request,pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower = follower, user = user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_followings = len(FollowersCount.objects.filter(follower=pk))



    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_posts_length": user_posts_length,
        "button_text": button_text,
        "user_followers": user_followers,
        "user_followings": user_followings,
    }



    return render(request,"profile.html",context)

@login_required(login_url="/signin")
def follow(request):
    if request.method=="POST":
        follower = request.POST["follower"]
        user = request.POST["user"]

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower = follower, user = user)
            new_follower.save()    
            return redirect('/profile/'+user)
            #redirect(f'/profile/{user.profile.slug}/{user.pk}')

    else:
        return redirect("/")
    

@login_required(login_url="/signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get("image") == None:
            image = user_profile.profileimg
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        if request.FILES.get("image") != None:
            image = request.FILES.get("image")
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect("settings")
    

    return render(request,"setting.html",{"user_profile":user_profile})

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request,"Username already taken")
                return redirect("signup")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request,user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()
                return redirect("settings")

        else:
            messages.info(request, "Passwords not matching")
            return redirect("signup")

    else:
        return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "Credentials invalid")
            return redirect("/signin")
        
    else:
        return render(request,"signin.html")

@login_required(login_url="/signin")
def logout(request):
    auth.logout(request)
    return redirect("signin")

