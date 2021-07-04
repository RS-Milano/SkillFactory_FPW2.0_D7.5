from django.http import HttpResponseRedirect, request
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import AuthorCategory, Post, Author, Category, RegisterForm, PostCategory
from .filter import PostFilter
from .tasks import new_post_notify

class PostList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'posts'
    ordering = ['-create_data']
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['limit_for_listing'] = Paginator(list(Post.objects.all()), 5).num_pages - 2
        context['all_posts'] = Post.objects.all()
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        context['anonymous'] = self.request.user.is_authenticated
        if self.request.user.is_authenticated:
            context['author'] = Author.objects.filter(user = User.objects.get(username = self.request.user))
        if self.request.user.is_authenticated:
            if Author.objects.filter(user = User.objects.get(username = self.request.user)):
                all_category = ["sport", "politics", "education", "culture"]
                for i in AuthorCategory.objects.filter(author = Author.objects.get(user = User.objects.get(username = self.request.user))):
                    if i.category.category in all_category:
                        all_category.remove(i.category.category)
                context['all_category'] = all_category
        return context

class FilteredPost(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-create_data']
    filterset_class = None
        
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.all()

    def get_page_param(self):
        page_param = self.request.GET.get("page", None)
        return page_param

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['authors'] = Author.objects.all()
        context['paginate'] = self.paginate_by
        context['all_posts'] = Post.objects.all()
        context['page_param'] = self.get_page_param()
        context['limit_for_listing'] = Paginator(list(Post.objects.all()), 5).num_pages - 2
        return context

class PostSearch(FilteredPost):
    filterset_class = PostFilter
    ordering = ['-create_data']
    paginate_by = 5

class AddPost(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Post
    template_name = 'addpost.html'
    permission_required = ('backend.add_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        context['new_post_id'] = len(Post.objects.all()) + 1
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        content = request.POST['content']
        author = request.POST['author']
        post_type = request.POST['post_type']
        my_category = request.POST['category']
        post = Post(author=Author.objects.get(user=author), title=title, content=content, post_type=post_type)
        post.save()
        post.category.add(Category.objects.get(category = my_category))
        new_post_notify.delay(post)
        return HttpResponseRedirect(f'{post.id}')

class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context

class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    fields = []
    template_name = 'editpost.html'
    context_object_name = 'post'
    permission_required = ('backend.change_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=request.get_full_path().split("/")[2])
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.author = Author.objects.get(id=request.POST['author'])
        post.post_type = request.POST['post_type']
        category = request.POST.get('category')
        if category:
            post.category.add(Category.objects.get(category=category))
        post.save()
        return HttpResponseRedirect(f"../{post.id}")

class DeletPost(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'deletpost.html'
    context_object_name = 'post'
    queryset = Post.objects.all()
    success_url = '/../../'

class PortalLogin(LoginView):
    template_name = 'login.html'

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/'

@login_required
def be_author(request):
    user = request.user
    Author.objects.create(user = user)
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')

def subscribe_sport(request):
    user = request.user
    Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "sport"))
    return redirect('/')

def subscribe_politics(request):
    user = request.user
    Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "politics"))
    return redirect('/')

def subscribe_education(request):
    user = request.user
    Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "education"))
    return redirect('/')

def subscribe_culture(request):
    user = request.user
    Author.objects.get(user = user).subscribed_category.add(Category.objects.get(category = "culture"))
    return redirect('/')
