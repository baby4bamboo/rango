from django.http import HttpResponse ,HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category,Page
from rango.forms import CategoryForm,PageForm,User,UserProfile,UserForm,UserProfileForm
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


def encode(with_blanke):
    no_blanke=with_blanke.replace('_', ' ')
    return no_blanke

def decode(no_blanke):
    with_blanke=no_blanke.replace(' ','_')
    return with_blanke
'''
def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages':pages_list}
    for category in category_list:
        #category.url = category.name.replace(' ', '_')
        category.url =  decode(category.name)
    return render_to_response('rango/index.html', context_dict, RequestContext(request))
'''
def index(request):
    context = RequestContext(request)

    category_list = Category.objects.all()
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = decode(category.name)

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    #### NEW CODE ####
    # Obtain our Response object early so we can add cookie information.
    response = render_to_response('rango/index.html', context_dict, context)

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = int(request.COOKIES.get('visits', '0'))

    # Does the cookie last_visit exist?
    if 'last_visit' in request.COOKIES:
        # Yes it does! Get the cookie's value.
        last_visit = request.COOKIES['last_visit']
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 5:
            # ...reassign the value of the cookie to +1 of what it was before...
            response.set_cookie('visits', visits+1)
            response.set_cookie('id', "svan")
            # ...and update the last visit cookie, too.
            response.set_cookie('last_visit', datetime.now())
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        response.set_cookie('last_visit', datetime.now())

    # Return response back to the user, updating any cookies that need changed.
    return response
    '''
def index(request):
    context = RequestContext(request)

    category_list = Category.objects.all()
    context_dict = {'categories': category_list}

    for category in category_list:
        category.url = decode(category.name)

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    #### NEW CODE ####
    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    #### END NEW CODE ####

    # Render and return the rendered response back to the user.
    return render_to_response('rango/index.html', context_dict, context)
'''

def about(request):
    context_dict={'boldmessage':"Rango says: Here is the about page."}
    if 'visits' in request.COOKIES:
        visits = request.COOKIES['visits']
    context_dict['visits']=visits
    return render_to_response('rango/about.html', context_dict, RequestContext(request))

def category(request, category_name_url):
    #category_name = category_name_url.replace('_', ' ')
    category_name = encode(category_name_url)
    context_dict = {'category_name': category_name}
    context_dict['category_name_url']=category_name_url
    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    return render_to_response('rango/category.html', context_dict, RequestContext(request))

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    return render_to_response('rango/add_category.html', {'form': form}, RequestContext(request))



def add_page(request, category_name_url):
    context = RequestContext(request)
    category_name = encode(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)
            page.views = 0
            page.save()
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            RequestContext(request))


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render_to_response('rango/login.html', {}, RequestContext(request))

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')