"""
Class: CSC648-848 SW Engineering SU21
Team: Team 4
Name: Kiara Gil, Ostyn Sy, Joshua Stone, Cong Le, Miho Shimizu, Vernon Xie, Melinda Yee
GitHub Name: KiaraGil, OstynSy, JoshLikesToCode, CleGuren, simicity, vxie123, melinda15
GitHub URL: https://github.com/sfsu-joseo/csc648-848-sw-engineering-SU21-T04

File Name: views.py

Description: All functions used for the website.
"""

from django.shortcuts import render, redirect
from django.template import loader
from study_app.forms import *
from study_app.models import *
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
import django.contrib.auth.password_validation as validation
from django.core.exceptions import ValidationError
from django.contrib import messages


# Create your views here.

# show landing page to general users and homepage to logged in users
def index(request):
    # not logged in users don't access the landing page
    if not request.user.is_authenticated:
        return redirect('/landing')
    return redirect('/home')


# show homepage
def home(request):
    #fetch groups the user has joined
    studyGroupMembers = StudyGroupMember.objects.filter(userId=request.user.userId)[:5]
    studyGroupIds = []
    for studyGroupMember in studyGroupMembers:
        studyGroupIds.append(studyGroupMember.studyGroupId.studyGroupId)
    studyGroupsAsMember = StudyGroup.objects.filter(studyGroupId__in=studyGroupIds).order_by('-studyGroupId')

    #if the user belongs to more than 3 groups, display the 3 most recent groups, then 2 most recent they host 
    if len(studyGroupIds) > 3:
        studyGroupsAsHost = StudyGroup.objects.filter(ownerId=request.user).order_by('-studyGroupId')[:2]
        studyGroupsAsMember = studyGroupsAsMember[:(5-len(studyGroupsAsHost))]
    #else display up to the 5 most recent groups they host
    else:
        studyGroupsAsHost = StudyGroup.objects.filter(ownerId=request.user).order_by('-studyGroupId')[:(5-len(studyGroupIds))]

    return render(request, 'index.html', {'studyGroupsAsMember': studyGroupsAsMember, 'studyGroupsAsHost': studyGroupsAsHost})

# NEED COMMENTING
def userStudyGroupListing(request):
    studyGroupMembers = StudyGroupMember.objects.filter(userId=request.user.userId)
    studyGroupIds = []
    for studyGroupMember in studyGroupMembers:
        studyGroupIds.append(studyGroupMember.studyGroupId.studyGroupId)
    studyGroupsAsMember = StudyGroup.objects.filter(studyGroupId__in=studyGroupIds).order_by('-studyGroupId')

    studyGroupsAsHost = StudyGroup.objects.filter(ownerId=request.user).order_by('-studyGroupId')
    return render(request, 'userStudyGroupListing.html', {'studyGroupsAsMember': studyGroupsAsMember, 'studyGroupsAsHost': studyGroupsAsHost})


# show the contact us page
def contactusPage(request):
    context = {}
    context['form'] = ContactForm()
    return render(request, "contactus.html", context)

# show the FAQ page
def FAQ(request):
    return render(request, 'FAQ.html')


# submits the contact us form
def submitContactus(request):
    context = {}
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = Contact()
            contact.fullname = form.cleaned_data['fullname']
            contact.telephone = form.cleaned_data['telephone']
            contact.email = form.cleaned_data['email']
            contact.message = form.cleaned_data['message']
            contact.save()
            return redirect('/contactus')
        else:
            print("Form not valid")
            context['form'] = form
    else:
        context['form'] = ContactForm()
    return render(request, 'contactus.html', context)

# show the under-construction page
def construction(request):
    return render(request, 'construction.html')

# show the about page
def about(request):
    return render(request, 'about.html')


# show landing page
def landing(request):
    # logged in users don't access the landing page
    if request.user.is_authenticated:
        print("user is already logged in")
        return redirect('/')

    return render(request, 'landing.html')

# NEED COMMENTING
def aboutUs(request, member):
    template = loader.get_template('about/T4TM-{name}.html'.format(name=member))
    context = {}
    return HttpResponse(template.render(context, request))

#shows terms of service
def tos(request):
    return render(request, 'termsofservice.html')

# ----------------------------
#  User
# ----------------------------

# show the user registration page
def register(request):
    # logged in users must not access
    if request.user.is_authenticated:
        print("user is already logged in")
        return redirect('/')

    context = {}
    context['form'] = RegistrationForm()
    return render(request, "register.html", context)

# show the user registration page
def registerEducator(request):
    # logged in users must not access
    if request.user.is_authenticated:
        print("user is already logged in")
        return redirect('/')

    context = {}
    context['form'] = EducatorRegistrationForm()
    return render(request, "registerEducator.html", context)

# create a user account
def createUser(request):
    context = {}
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['tosCheck']:
            user = User()
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.password = form.cleaned_data['password']
            user.confirmPassword = form.cleaned_data['confirmPassword']
            username_exist = User.objects.filter(username=form.cleaned_data['username'])
            email_exist = User.objects.filter(email=form.cleaned_data['email'])
            # password and confirm password must match
            if user.password == user.confirmPassword:
                # validate password
                try:
                    validation.validate_password(user.password, user)
                except ValidationError as val_err:
                    return render(request, 'register.html',
                                  {'form': form,
                                   'error': True,
                                   'valMessages': val_err.messages,
                                   'user_error': username_exist,
                                   'email_error': email_exist,
                                   'different_pw_error': False})

                if username_exist or email_exist:
                    # username or email already exist, user cannot register with this username/email
                    return render(request, 'register.html',
                                  {'form': form,
                                   'error': True,
                                   'valMessages': False,
                                   'user_error': username_exist,
                                   'email_error': email_exist,
                                   'different_pw_error': False})
                # no credential error, proceed to record information
                else:
                    try:
                        # hash password
                        user.password = make_password(user.password)
                        # register the user
                        messages.success(request, "New account created!")
                        user.save()
                        return redirect('/login')
                    except:
                        pass
            # confirm password does not match, throw error
            else:
                context['form'] = form
                return render(request, 'register.html',
                              {'form': form,
                               'error': True,
                               'valMessages': False,
                               'user_error': username_exist,
                               'email_error': email_exist,
                               'different_pw_error': True})
        else:
            messages.error(request, "Invalid login credentials")
            context['form'] = form
    else:
        messages.error(request, "Something is wrong")
        context['form'] = RegistrationForm()

    # user creation failed (this should never be called, but exist as precaution
    return render(request, 'register.html', context)

# create an educator user account
def createEducatorUser(request):
    context = {}
    if request.method == "POST":
        form = EducatorRegistrationForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['tosCheck']:
            user = User()
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.password = form.cleaned_data['password']
            user.confirmPassword = form.cleaned_data['confirmPassword']
            user.role = "educator"
            username_exist = User.objects.filter(username=form.cleaned_data['username'])
            email_exist = User.objects.filter(email=form.cleaned_data['email'])
            # password and confirm password must match
            if user.password == user.confirmPassword:
                # validate password
                try:
                    validation.validate_password(user.password, user)
                except ValidationError as val_err:
                    return render(request, 'registerEducator.html',
                                  {'form': form,
                                   'error': True,
                                   'valMessages': val_err.messages,
                                   'user_error': username_exist,
                                   'email_error': email_exist,
                                   'different_pw_error': False})

                if username_exist or email_exist:
                    # username or email already exist, user cannot register with this username/email
                    return render(request, 'registerEducator.html',
                                  {'form': form,
                                   'error': True,
                                   'valMessages': False,
                                   'user_error': username_exist,
                                   'email_error': email_exist,
                                   'different_pw_error': False})
                # no credential error, proceed to record information
                else:
                    try:
                        # hash password
                        user.password = make_password(user.password)
                        # register a user
                        messages.success(request, "New account created!")
                        user.save()
                        return redirect('/login')
                    except:
                        pass
            # confirm password does not match, throw error
            else:
                context['form'] = form
                return render(request, 'register.html',
                              {'form': form,
                               'error': True,
                               'valMessages': False,
                               'user_error': username_exist,
                               'email_error': email_exist,
                               'different_pw_error': True})
        else:
            messages.error(request, "Invalid form data")
            context['form'] = form
    else:
        messages.error(request, "Something is wrong")
        context['form'] = EducatorRegistrationForm()

    # user creation failed (this should never be called, but exist as failsafe
    return render(request, 'registerEducator.html', context)

# show the edit user profile page
def editUserProfile(request):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You're not logged in")
        return redirect('/login')

    user = User.objects.get(userId=request.user.userId)
    context = {}
    context['form'] = UserProfileForm(instance=user)
    return render(request, 'editUserProfile.html', context)


# update user profile
def updateUserProfile(request):
    context = {}
    user = User.objects.get(userId=request.user.userId)
    form = UserProfileForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
        form.save()
        return redirect(f'/{user.userId}/userprofile')
    else:
        messages.error(request, "Invalid form data")
    context['form'] = form
    return render(request, 'edituserprofile.html', context)


# show the login page
def loginPage(request):
    # logged in users must not access
    if request.user.is_authenticated:
        print("user is already logged in")
        return redirect('/')

    context = {}
    context['form'] = LoginForm()
    return render(request, "login.html", context)


# let a user login
def loginUser(request):
    context = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            # proceed with log in process if user is not already logged in
            if user is not None:
                messages.success(request, "You are successfully logged in!")
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, "Authentication failed")
                context['form'] = form
        else:
            messages.error(request, "Invalid form data")
            context['form'] = form
    else:
        context['form'] = LoginForm()
    return render(request, 'login.html', context)


# let a user logout
def logoutUser(request):
    messages.success(request, "You are logged out!")
    logout(request)
    return redirect('/')


# show the confirm delete user page
def confirmDeleteUser(request):
    # not logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    context = {}
    context['form'] = ContactForm()
    return render(request, "deleteAccountActionPage.html", context)


# delete a user account
def deleteUser(request):
    # logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    # delete the currently logged in user
    user = User.objects.get(userId=request.user.userId)
    user.delete()
    return redirect('/')

#show the edit password page
def editPassword(request):
    # not logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    context = {}
    context['form'] = UserPasswordForm()
    return render(request, "updatePassword.html", context)

#update password
def updatePassword(request):
    context = {}
    if request.method == "POST":
        form = UserPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(userId=request.user.userId)
            currentPassword = form.cleaned_data['currentPassword']
            newPassword = form.cleaned_data['newPassword']
            confirmPassword = form.cleaned_data['confirmPassword']
            auth = authenticate(email=user.email, password=currentPassword)
            if auth is not None:
                if newPassword == confirmPassword:
                    if newPassword == currentPassword:
                        # new password cannot be the same as current password
                        return render(request, 'updatePassword.html',
                                      {'form': form,
                                       'error': True,
                                       'valMessages': False,
                                       'different_pw_error': False,
                                       'incorrect_pw_error': False,
                                       'unchanged_pw_error': True})
                    else:
                        try:
                            # validate the new password
                            validation.validate_password(newPassword, user)
                        except ValidationError as val_err:
                            # new password does not meet the criteria of a good password
                            return render(request, 'updatePassword.html',
                                          {'form': form,
                                           'error': True,
                                           'valMessages': val_err.messages,
                                           'different_pw_error': False,
                                           'incorrect_pw_error': False,
                                           'unchanged_pw_error': False})
                        # no credential error
                        try:
                            # hash password
                            user.password = make_password(newPassword)
                            # register a user
                            messages.success(request, "New Password Updated!")
                            user.save()
                            return redirect('/login')
                        except:
                            pass
                # "new password" and "confirm new password" do not match
                else:
                    return render(request, 'updatePassword.html',
                                  {'form': form,
                                   'error': True,
                                   'valMessages': False,
                                   'different_pw_error': True,
                                   'incorrect_pw_error': False,
                                   'unchanged_pw_error': False})
            # incorrect "current password"
            else:
                return render(request, 'updatePassword.html',
                              {'form': form,
                               'error': True,
                               'valMessages': False,
                               'different_pw_error': False,
                               'incorrect_pw_error': True,
                               'unchanged_pw_error': False})
        else:
            messages.error(request, "Invalid form data")
            context['form'] = form
    else:
        context['form'] = UserPasswordForm()
    return render(request, "updatePassword.html", context)

# show a specified user's profile
def showUserProfile(request, userId):
    #fetch user information
    user = User.objects.get(userId=userId)

    #fetch information of groups the user joined
    studyGroupMembers = StudyGroupMember.objects.filter(userId=request.user.userId)
    studyGroupIds = []
    for studyGroupMember in studyGroupMembers:
        studyGroupIds.append(studyGroupMember.studyGroupId.studyGroupId)
    studyGroupsAsMember = StudyGroup.objects.filter(studyGroupId__in=studyGroupIds).order_by('-studyGroupId')

    #fetch information of groups hosted by the user
    studyGroupsAsHost = StudyGroup.objects.filter(ownerId=user).order_by('-studyGroupId')

    #fetch information of the user's main forum posts
    mainPosts = MainPost.objects.filter(userId=user).order_by('-postDateTime')

    #fetch information of the user's study group forum posts
    studyGroupPosts = StudyGroupPost.objects.filter(userId=userId).order_by('-postDateTime')

    return render(request, 'userProfile.html', {'userprofile': user, 'studyGroupsAsMember': studyGroupsAsMember, 'studyGroupsAsHost': studyGroupsAsHost, 'mainPosts': mainPosts, 'studyGroupPosts': studyGroupPosts})


# ----------------------------
#  Main Forum Post
# ----------------------------

# show main forum
def showMainForum(request):
    mainposts = MainPost.objects.all().order_by('-postDateTime')
    return render(request, 'mainforum.html', {'mainposts': mainposts})


# show a main post
def showMainPost(request, postId):
    mainpost = MainPost.objects.get(postId=postId)
    comments = MainComment.objects.filter(postId=postId)
    form = MainCommentForm()
    return render(request, 'mainPostPage.html', {'mainpost': mainpost, 'comments': comments, 'form': form})


# show the main post creation page
def createMainPost(request):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to create a Forum Post!")
        return redirect('/login')

    context = {}
    context['form'] = MainPostForm()
    return render(request, "createMainPost.html", context)


# create a main post
def execCreateMainPost(request):
    context = {}
    if request.method == "POST":
        form = MainPostForm(request.POST)
        if form.is_valid():
            mainPost = MainPost()
            mainPost.postTitle = form.cleaned_data['postTitle']
            mainPost.post = form.cleaned_data['post']
            # owner is the currently logged in user
            mainPost.userId = User.objects.get(userId=request.user.userId)
            try:
                messages.success(request, "New post created")
                mainPost.save()
                return redirect('/mainforum')
            except:
                pass
        else:
            messages.error(request, "Invalid form data")

    context['form'] = MainPostForm()
    return render(request, 'createMainPost.html', context)


# show the edit post page
def editMainPost(request, postId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You're not logged in")
        return redirect('/login')

    mainPost = MainPost.objects.get(postId=postId)
    context = {}
    context['form'] = MainPostForm(instance=mainPost)
    return render(request, 'editMainPost.html', context)


# update a main post
def updateMainPost(request, postId):
    context = {}
    mainPost = MainPost.objects.get(postId=postId)
    form = MainPostForm(request.POST, instance=mainPost)
    if form.is_valid():
        form.save()
        messages.success(request, "Post edited!")
        return redirect(f'/{postId}/mainpost')
    else:
        messages.error(request, "Title or Description cannot be left blank")
    context['form'] = form
    return render(request, 'editMainPost.html', context)


# delete a main post
def deleteMainPost(request, postId):
    # logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    mainPost = MainPost.objects.get(postId=postId)
    mainPost.delete()
    return redirect('/mainforum')


# ----------------------------
#  Main Forum Post Comment
# ----------------------------

# show the main comment creation page (currently not in use)
def createMainComment(request, postId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to create a study group")
        return redirect('/login')

    context = {}
    context['form'] = MainCommentForm()
    return render(request, "createMainComment.html", context)


# create a comment for a main post
def execCreateMainComment(request, postId):
    context = {}
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to comment on a Post!")
        return redirect('/login')

    if request.method == "POST":
        form = MainCommentForm(request.POST)
        if form.is_valid():
            mainComment = MainComment()
            mainComment.comment = form.cleaned_data['comment']
            # owner is the currently logged in user
            mainComment.userId = User.objects.get(userId=request.user.userId)
            mainComment.postId = MainPost.objects.get(postId=postId)
            try:
                messages.success(request, "Comment added")
                mainComment.save()
                return redirect(f'/{postId}/mainpost')
            except:
                pass
        else:
            messages.error(request, "Invalid form data")

    context['form'] = MainCommentForm()
    return render(request, 'createMainComment.html', context)


# show the edit main comment page
def editMainComment(request, postId, commentId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You're not logged in")
        return redirect('/login')

    mainComment = MainComment.objects.get(commentId=commentId)
    form = MainCommentForm(instance=mainComment)
    return render(request, 'editMainComment.html', {'form': form, 'mainpostId': postId})


# update a main comment
def updateMainComment(request, postId, commentId):
    context = {}
    mainComment = MainComment.objects.get(commentId=commentId)
    form = MainCommentForm(request.POST, instance=mainComment)
    if form.is_valid():
        form.save()
        return redirect(f'/{postId}/mainpost')
    else:
        messages.error(request, "Edited comment cannot be left blank")
    context['form'] = form
    return render(request, 'editMainComment.html', {'form': form, 'mainpostId': postId})


# delete a main comment
def deleteMainComment(request, postId, commentId):
    # logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You are not logged in")
        return redirect('/login')

    mainComment = MainComment.objects.get(commentId=commentId)
    mainComment.delete()
    return redirect(f'/{postId}/mainpost')


# ----------------------------
#  Study Group
# ----------------------------

# show study group listing
def showStudyGroupListing(request, subject):
    studyGroups = StudyGroup.objects.filter(subject__contains=subject).order_by('-studyGroupId')
    return render(request, 'studyGroupListing.html', {'studygroups': studyGroups})

# show a main post
def showMainPost(request, postId):
    mainpost = MainPost.objects.get(postId=postId)
    comments = MainComment.objects.filter(postId=postId)
    form = MainCommentForm()
    return render(request, 'mainPostPage.html', {'mainpost': mainpost, 'comments': comments, 'form': form})


# show a study group page
def showStudyGroup(request, studyGroupId):
    studygroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    studygroupposts = StudyGroupPost.objects.filter(studyGroupId=studyGroupId).order_by('-postDateTime')
    members = StudyGroupMember.objects.filter(studyGroupId=studyGroupId)
    sizeLimit = EDUCATOR_STUDY_GROUP_CAPACITY if studygroup.ownerId.role == "educator" else STUDY_GROUP_CAPACITY
    if not request.user.is_authenticated:
        # display a default study group page if the current session user is not a logged in user
        return render(request, 'studyGroupPage.html',
                  {'studygroup': studygroup, 'studygroupposts': studygroupposts, 'members': members, 'isHost': False, 'isMember': False, 'isUnreg': True})
    # display the page differently if the current session user is a host of the study group, or if they are a member of the study group
    checkMem = isMember(request, studyGroupId)
    checkHost = isHost(request, studyGroupId)
    return render(request, 'studyGroupPage.html',
                  {'studygroup': studygroup, 'studygroupposts': studygroupposts, 'members': members, 'isHost': checkHost, 'isMember': checkMem, 'sizeLimit': sizeLimit})

# show the study group creation page
def createStudyGroup(request):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to create a Study Group")
        return redirect('/login')

    context = {}
    context['form'] = StudyGroupForm()
    return render(request, "createStudyGroup.html", context)


# create a study group
def execCreateStudyGroup(request):
    context = {}
    if request.method == "POST":
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            studyGroup = StudyGroup()
            studyGroup.groupName = form.cleaned_data['groupName']
            studyGroup.description = form.cleaned_data['description']
            studyGroup.subject = form.cleaned_data['subject']
            # owner is the currently logged in user
            studyGroup.ownerId = User.objects.get(userId=request.user.userId)
            studyGroup.save()
            messages.success(request, "New study group created")
            return redirect(f'/{studyGroup.studyGroupId}/studygroup')
        else:
            messages.error(request, "Title, Description, and Subject cannot be left blank")

    context['form'] = StudyGroupForm()
    return render(request, 'createStudyGroup.html', context)


# show the edit study group page
def editStudyGroup(request, studyGroupId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You're not logged in")
        return redirect('/login')

    studygroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    context = {}
    context['form'] = StudyGroupForm(instance=studygroup)
    return render(request, 'editStudyGroup.html', context)


# update a study group
def updateStudyGroup(request, studyGroupId):
    studygroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    form = StudyGroupForm(request.POST, instance=studygroup)
    if form.is_valid():
        form.save()
        return redirect(f'/{studyGroupId}/studygroup')
    else:
        messages.error(request, "Title, Description, and Subject cannot be empty")
    context = {}
    context['form'] = form
    return render(request, 'editStudyGroup.html', context)


# delete a study group
def deleteStudyGroup(request, studyGroupId):
    # logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You must first log in!")
        return redirect('/login')

    studygroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    studygroup.delete()
    messages.success(request, "Your Study Group was deleted!")
    return redirect('/home')


# check if the logged in user is a member of the study group
def isMember(request, studyGroupId):
    studyGroupMember = StudyGroupMember.objects.filter(userId=request.user.userId, studyGroupId=studyGroupId)
    return True if studyGroupMember else False

# check if the logged in user is the host of the study group
def isHost(request, studyGroupId):
    studyGroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    return True if request.user == studyGroup.ownerId else False

# let the logged in user join a study group
def joinStudyGroup(request, studyGroupId):
    studyGroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    # requires current session user to log in if they are not logged in
    if not request.user.is_authenticated:
        messages.error(request, "Login to Join Groups!")
        return redirect('/login')
    # a user can only join when the study group is full and when the user is not a member of this group
    if not studyGroup.isFull() and not isMember(request, studyGroupId):
        studyGroupMember = StudyGroupMember()
        studyGroupMember.userId = User.objects.get(userId=request.user.userId)
        studyGroupMember.studyGroupId = studyGroup
        studyGroupMember.save()

        studyGroup.memberCount += 1
        studyGroup.save()
        messages.success(request, "Joined the group!")
    else:
        messages.warning(request, "This group is full!")
    return redirect(f'/{studyGroupId}/studygroup')


# let the logged in user leave a study group
def leaveStudyGroup(request, studyGroupId):
    studyGroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    if studyGroup.memberCount > 0:
        studyGroup.memberCount -= 1
        studyGroup.save()

    studyGroupMember = StudyGroupMember.objects.filter(userId=request.user.userId, studyGroupId=studyGroupId)
    studyGroupMember.delete()
    messages.success(request, "Left the group!")
    return redirect(f'/{studyGroupId}/studygroup')

# search study groups
def searchStudyGroups(request):
    found = False
    maybe = False
    foundStudyGroups = None
    maybeStudyGroups = None
    suggestStudyGroups = None

    if request.method == "POST":
        searched = request.POST['searched']
        if searched:
            #find groups whose name contains the searched word
            foundStudyGroups = StudyGroup.objects.filter(groupName__icontains=searched).order_by('-studyGroupId')
            if foundStudyGroups:
                found = True
            else:
                #find groups whose description contains the searched word
                maybeStudyGroups = StudyGroup.objects.filter(description__icontains=searched).order_by('-studyGroupId')
                if len(maybeStudyGroups) > 10:
                    maybe = True

    if not found and not maybe:
        #no search word was inputted. suggest not-full popular groups
        suggestStudyGroups = StudyGroup.objects.filter(memberCount__lt=20).order_by('-memberCount')[:10]

    return render(request, 'searchResults.html', {'searched': searched, 'foundStudyGroups': foundStudyGroups, 'maybeStudyGroups': maybeStudyGroups, 'suggestStudyGroups': suggestStudyGroups})



# ----------------------------
#  Study Group Forum Post
# ----------------------------

# show a study group post
def showStudyGroupPost(request, studyGroupId, postId):
    studygroup = StudyGroup.objects.get(studyGroupId=studyGroupId)
    studygrouppost = StudyGroupPost.objects.get(postId=postId)
    comments = StudyGroupComment.objects.filter(postId=postId)
    form = StudyGroupCommentForm()
    return render(request, 'studyGroupPostPage.html',
                  {'studygroup': studygroup, 'studygrouppost': studygrouppost, 'comments': comments, 'form': form})


# show the study group post creation page
def createStudyGroupPost(request, studyGroupId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You must log in to create a post!")
        return redirect('/login')

# Host(ownerId) needs to be able to create studygroup posts and comments
    if not (isMember(request, studyGroupId) or isHost(request, studyGroupId)):
        messages.error(request, "You must join the group to create a post!")
        return redirect(f'/{studyGroupId}/studygroup')

    context = {}
    context['form'] = StudyGroupPostForm()
    return render(request, "createStudyGroupPost.html", context)


# create a study group forum post
def execCreateStudyGroupPost(request, studyGroupId):
    context = {}

    if not request.user.is_authenticated:
        messages.error(request, "You must be login before you can post!")
        return redirect('/login')

    if not (isMember(request, studyGroupId) or isHost(request, studyGroupId)):
        messages.error(request, "You must join the group to create a post!")
        return redirect(f'/{studyGroupId}/studygroup')

    if request.method == "POST":
        form = StudyGroupPostForm(request.POST)
        if form.is_valid():
            studyGroupPost = StudyGroupPost()
            studyGroupPost.postTitle = form.cleaned_data['postTitle']
            studyGroupPost.post = form.cleaned_data['post']
            # owner is the currently logged in user
            studyGroupPost.userId = User.objects.get(userId=request.user.userId)
            studyGroupPost.studyGroupId = StudyGroup.objects.get(studyGroupId=studyGroupId)
            try:
                messages.success(request, "New post created")
                studyGroupPost.save()
                return redirect(f'/{studyGroupId}/studygroup')
            except:
                pass
        else:
            messages.error(request, "Invalid form data")

    context['form'] = StudyGroupPostForm()
    return render(request, 'createStudyGroupPost.html', context)


# show the edit study group forum post page
def editStudyGroupPost(request, studyGroupId, postId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You're not logged in")
        return redirect('/login')

    studyGroupPost = StudyGroupPost.objects.get(postId=postId)
    context = {}
    context['form'] = StudyGroupPostForm(instance=studyGroupPost)
    return render(request, 'editStudyGroupPost.html', context)


# update a study group forum post
def updateStudyGroupPost(request, studyGroupId, postId):
    context = {}
    studyGroupPost = StudyGroupPost.objects.get(postId=postId)
    form = StudyGroupPostForm(request.POST, instance=studyGroupPost)
    if form.is_valid():
        form.save()
        messages.success(request, "Post edited")
        return redirect(f'/{studyGroupId}/{postId}/studygrouppost')
    else:
        messages.error(request, "Title or Description cannot be left blank")
    context['form'] = form
    return render(request, 'editStudyGroupPost.html', context)


# delete a study group forum post
def deleteStudyGroupPost(request, studyGroupId, postId):
    # logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    studyGroupPost = StudyGroupPost.objects.get(postId=postId)
    studyGroupPost.delete()
    return redirect(f'/{studyGroupId}/studygroup')


# ----------------------------
#  StudyGroup Forum Post Comment
# ----------------------------

# show the study group comment page (currently not in use)
def createStudyGroupComment(request, studyGroupId, postId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to create a study group")
        return redirect('/login')

    context = {}
    context['form'] = StudyGroupCommentForm()
    return render(request, "createStudyGroupComment.html", context)


# create a comment for a study group forum post
def execCreateStudyGroupComment(request, studyGroupId, postId):
    context = {}

    if not request.user.is_authenticated:
        messages.error(request, "You must be login before you can post!")
        return redirect('/login')

    if not (isMember(request, studyGroupId) or isHost(request, studyGroupId)):
        messages.error(request, "You must join the group to comment!")
        return redirect(f'/{studyGroupId}/studygroup')

    if request.method == "POST":
        form = StudyGroupCommentForm(request.POST)
        if form.is_valid():
            studyGroupComment = StudyGroupComment()
            studyGroupComment.comment = form.cleaned_data['comment']
            # owner is the currently logged in user
            studyGroupComment.userId = User.objects.get(userId=request.user.userId)
            studyGroupComment.postId = StudyGroupPost.objects.get(postId=postId)
            try:
                messages.success(request, "Comment added")
                studyGroupComment.save()
                return redirect(f'/{studyGroupId}/{postId}/studygrouppost')
            except:
                pass
        else:
            messages.error(request, "Invalid form data")

    context['form'] = StudyGroupCommentForm()
    return render(request, 'createStudyGroupComment.html', context)


# show the edit study group comment page
def editStudyGroupComment(request, studyGroupId, postId, commentId):
    # not logged in users must not access
    if not request.user.is_authenticated:
        messages.error(request, "You are not logged in")
        return redirect('/login')

    studyGroupComment = StudyGroupComment.objects.get(commentId=commentId)
    form = StudyGroupCommentForm(instance=studyGroupComment)
    return render(request, 'editStudyGroupComment.html', {'form': form, 'studygroupID': studyGroupId, 'studygrouppostID': postId})


# update a study group comment
def updateStudyGroupComment(request, studyGroupId, postId, commentId):
    context = {}
    studyGroupComment = StudyGroupComment.objects.get(commentId=commentId)
    form = StudyGroupCommentForm(request.POST, instance=studyGroupComment)
    if form.is_valid():
        form.save()
        messages.success(request, "Comment edited")
        return redirect(f'/{studyGroupId}/{postId}/studygrouppost')
    else:
        messages.error(request, "Edited comment cannot be left blank")
    context['form'] = form
    # return render(request, 'editStudyGroupComment.html', context)
    return render(request, 'editStudyGroupComment.html', {'form': form, 'studygroupID': studyGroupId, 'studygrouppostID': postId})

# delete a study group comment
def deleteStudyGroupComment(request, studyGroupId, postId, commentId):
    # logged in users must not access
    if not request.user.is_authenticated:
        print("You're not logged in")
        return redirect('/login')

    studyGroupComment = StudyGroupComment.objects.get(commentId=commentId)
    studyGroupComment.delete()
    return redirect(f'/{studyGroupId}/{postId}/studygrouppost')

# ----------------------------
#  Front End Testing 
# ----------------------------

def testEditStudyGroup(request):
    context = {}
    context['form'] = StudyGroupForm()
    return render(request, 'testEditStudyGroup.html', context)


def testCreateStudyPost(request):
    context = {}
    context['form'] = StudyGroupPostForm()
    return render(request, "testCreateStudyPost.html", context)


def testCreateMainPost(request):
    context = {}
    context['form'] = MainPostForm()
    return render(request, "testCreateMainPost.html", context)


def testEditMainPost(request):
    context = {}
    context['form'] = MainPostForm()
    return render(request, 'testEditMainPost.html', context)


def testEditStudyGroupPost(request):
    context = {}
    context['form'] = StudyGroupPostForm()
    return render(request, 'testEditStudyGroupPost.html', context)


def report(request):
    return render(request, 'report.html')


def testUserProfile(request):
    return render(request, 'testUserProfile.html')


def testEditUserProfile(request):
    context = {}
    context['form'] = UserProfileForm()
    return render(request, 'testEditUserProfile.html', context)