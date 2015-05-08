from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category,Page
from rango.forms import CategoryForm,PageForm

def encode(with_blanke):
    no_blanke=with_blanke.replace('_', ' ')
    return no_blanke

def decode(no_blanke):
    with_blanke=no_blanke.replace(' ','_')
    return with_blanke

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,'pages':pages_list}
    for category in category_list:
        #category.url = category.name.replace(' ', '_')
        category.url =  decode(category.name)
    return render_to_response('rango/index.html', context_dict, RequestContext(request))

def about(request):
    context_dict={'boldmessage':"Rango says: Here is the about page."}
    return render_to_response('rango/about.html', context_dict, RequestContext(request))

def category(request, category_name_url):
    #category_name = category_name_url.replace('_', ' ')
    category_name = encode(category_name_url)
    context_dict = {'category_name': category_name}
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


'''
def add_page(request, category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
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
             '''