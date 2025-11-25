from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import slugify
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Event, Category, Tag, ContactMessage
from .forms import PostForm, EventForm
from .decorators import admin_required, AdminRequiredMixin

# ==========================
# DASHBOARD ADMIN
# ==========================
@admin_required
def admin_dashboard(request):
    # 1. Recuperar os dados (usando os nomes CORRETOS)
    context = {
        'total_events': Event.objects.count(),
        'upcoming_events': Event.objects.filter(status='upcoming').count(),
        'recent_posts': Post.objects.all().order_by('-published_date')[:5],
        'recent_events': Event.objects.all().order_by('date', 'start_time')[:5],
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(), # ⬅️ Corrigido de 'read' para 'is_read' (conforme o modelo)
    }

    # 2. Renderizar o template com o contexto
    return render(request, 'admin_area/dashboard.html', context)

# ==========================
# POSTS CRUD
# ==========================
class AdminPostListView(AdminRequiredMixin, ListView):
    model = Post
    template_name = 'admin_area/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')


class AdminPostCreateView(AdminRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'admin_area/post_form.html'
    success_url = reverse_lazy('admin_post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.title)
        messages.success(self.request, 'Post criado com sucesso!')
        return super().form_valid(form)


class AdminPostUpdateView(AdminRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'admin_area/post_form.html'
    success_url = reverse_lazy('admin_post_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        messages.success(self.request, 'Post atualizado com sucesso!')
        return super().form_valid(form)


class AdminPostDeleteView(AdminRequiredMixin, DeleteView):
    model = Post
    template_name = 'admin_area/post_confirm_delete.html'
    success_url = reverse_lazy('admin_post_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Post excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# ==========================
# Events CRUD usando slug
# ==========================
class AdminEventUpdateView(AdminRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'admin_area/event_form.html'
    success_url = reverse_lazy('admin_event_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        messages.success(self.request, 'Evento atualizado com sucesso!')
        return super().form_valid(form)


class AdminEventDeleteView(AdminRequiredMixin, DeleteView):
    model = Event
    template_name = 'admin_area/event_confirm_delete.html'
    success_url = reverse_lazy('admin_event_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Evento excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# ==========================



@admin_required
def admin_message_detail(request, pk):
    """Detalhes de uma mensagem específica"""
    message = get_object_or_404(ContactMessage, pk=pk)

    if not message.read:
        message.read = True
        message.save()

    return render(request, 'admin_area/message_detail.html', {'message': message})

# ==========================
# CATEGORIAS
# ==========================
@admin_required
def admin_categories(request):
    """Gerenciar categorias"""
    categories = Category.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name, slug=slugify(name))
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('admin_categories')

    return render(request, 'admin_area/categories.html', {'categories': categories})

# ==========================
# TAGS
# ==========================
@admin_required
def admin_tags(request):
    """Gerenciar tags"""
    tags = Tag.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Tag.objects.create(name=name, slug=slugify(name))
            messages.success(request, 'Tag criada com sucesso!')
            return redirect('admin_tags')

    return render(request, 'admin_area/tags.html', {'tags': tags})
