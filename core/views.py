from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .forms import CategoryForm


# IMPORTAÇÕES DE MODELOS
from .models import BlogPost, Event, Category, ContactMessage, GalleryImage

# IMPORTAÇÕES DE FORMS (AJUSTE NECESSÁRIO AQUI)
# 🚨 ATUALIZE ESTA LINHA: Adicione CategoryForm aqui
from .forms import ContactForm, BlogPostForm, EventForm, SearchForm, CategoryForm

User = get_user_model()

# ==========================
# Funções Auxiliares
# ==========================

def is_admin(user):
    """Check if user is admin (using standard Django flags)"""
    # Usando is_staff e is_superuser como critérios de administração
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ==========================
# 🌐 Vistas Públicas
# ==========================

def home_view(request):
    """Home page view"""
    featured_events = Event.objects.filter(featured=True, status='upcoming')[:2]
    recent_posts = BlogPost.objects.filter(status='published').order_by('-created_at')[:3]
    recent_gallery_images = GalleryImage.objects.filter(published=True).order_by('-uploaded_at')[:6]
    
    context = {
        'featured_events': featured_events,
        'recent_posts': recent_posts,
        'recent_gallery_images': recent_gallery_images,
    }
    return render(request, 'pages/home.html', context)


def sobre_view(request):
    """About page view"""
    return render(request, 'pages/sobre.html')


def projetos_view(request):
    """Projects page view"""
    return render(request, 'pages/projetos.html')


def semana_consciencia_negra_view(request):
    """Black consciousness week page view"""
    return render(request, 'pages/semana_consciencia_negra.html')


class BlogListView(ListView):
    """Blog posts list view"""
    model = BlogPost
    template_name = 'pages/blog.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published')
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(author__first_name__icontains=search) |
                Q(author__last_name__icontains=search)
            )
        
        if category and category != 'Todos':
            queryset = queryset.filter(category__name=category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_posts'] = BlogPost.objects.filter(featured=True, status='published')[:3]
        context['search_form'] = SearchForm(self.request.GET)
        return context


class BlogDetailView(DetailView):
    """Blog post detail view"""
    model = BlogPost
    template_name = 'pages/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj


class EventListView(ListView):
    """Events list view"""
    model = Event
    template_name = 'pages/eventos.html'
    context_object_name = 'events'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Event.objects.exclude(status='cancelled')
        category = self.request.GET.get('category')
        event_type = self.request.GET.get('type')
        
        if category and category != 'Todos':
            queryset = queryset.filter(category=category)
        
        if event_type and event_type != 'Todos':
            queryset = queryset.filter(event_type=event_type)
        
        return queryset.order_by('date', 'start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_events'] = Event.objects.filter(featured=True, status='upcoming')[:2]
        context['categories'] = Event.objects.values_list('category', flat=True).distinct()
        context['event_types'] = Event.TYPE_CHOICES
        return context


class EventDetailView(DetailView):
    """Event detail view"""
    model = Event
    template_name = 'pages/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


def contact_view(request):
    """Contact page view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            return redirect('contato')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contato.html', {'form': form})

# 🖼️ View da Galeria (Nova)
class GalleryListView(ListView):
    """View para listar as imagens da Galeria."""
    model = GalleryImage
    template_name = 'pages/galeria.html' 
    context_object_name = 'images' 
    paginate_by = 12 

    def get_queryset(self):
        # Retorna apenas as imagens publicadas
        queryset = GalleryImage.objects.filter(published=True)
        
        # Opcional: Adicionar lógica de filtro por evento
        event_id = self.request.GET.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
            
        return queryset.order_by('-uploaded_at') # Ordem: mais recentes primeiro
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona uma lista de Eventos para um possível filtro no template
        context['events_with_images'] = Event.objects.filter(galleryimage__published=True).distinct()
        return context


# ==========================
# 🔑 Vistas de Autenticação
# ==========================

def admin_login_view(request):
    """Custom admin login view"""
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if is_admin(user):
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.get_full_name()}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Acesso negado.')
        else:
            messages.error(request, 'Email ou senha incorretos.')
    
    return render(request, 'admin/login.html')

@login_required
def admin_logout_view(request):
    """Admin logout view"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('home')

# ==========================
# ⚙️ Vistas Admin (Funções)
# ==========================

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Admin dashboard view"""
    stats = {
        'posts': BlogPost.objects.count(),
        'events': Event.objects.count(),
        'users': User.objects.count(),
        'messages': ContactMessage.objects.filter(is_read=False).count(),
    }
    
    recent_posts = BlogPost.objects.order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')[:5]
    recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_posts': recent_posts,
        'upcoming_events': upcoming_events,
        'recent_messages': recent_messages,
    }
    return render(request, 'admin/dashboard.html', context)

def admin_dashboard(request):
    # Função duplicada, mas mantida por segurança se a URL a estiver chamando
    users_count = User.objects.count()
    posts_count = BlogPost.objects.count()
    events_count = Event.objects.count()
    
    return render(request, 'pages/admin_dashboard.html', {
        'users_count': users_count,
        'posts_count': posts_count,
        'events_count': events_count,
    })

# NOVO: Views de Categorias e Tags (Admin)
# 🟢 CORREÇÃO 1: Remoção da decoração de função duplicada
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminCategoryListView(ListView):
    model = Category
    template_name = 'admin/categories.html'
    context_object_name = 'categories'
    ordering = ['name']    # <-- Adicionando ordenação padrão
    paginate_by = 10       # <-- Adicionando paginação padrão

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 🟢 CORREÇÃO 2: Usa CategoryForm importado do topo
        context['form'] = CategoryForm() 
        return context

@login_required
@user_passes_test(is_admin)
def admin_tags_view(request):
    """View para gerenciamento de tags (apenas Admin)"""
    return render(request, 'admin/tags.html')


# ❌ RECOMENDAÇÃO: Remover ou comentar estas Funções Views
# (Pois foram substituídas pelas Class Views abaixo)

# def admin_posts_view(request, pk=None):
#     """Página de gerenciamento de posts e criação/edição de post"""
#     # ... código
# @login_required
# def admin_edit_post(request, pk):
#     """Página para edição de um post existente"""
#     # ... código
# @login_required
# @user_passes_test(is_admin)
# def admin_events_view(request, pk=None):
#     """Dashboard de eventos: lista todos os eventos e permite criar/editar."""
#     # ... código

@login_required
@user_passes_test(is_admin)
def admin_users_view(request):
    """Página de gerenciamento de usuários"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'pages/admin_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_settings_view(request):
    """Página de configurações do sistema"""
    context = {
        'users_count': User.objects.count(),
        'posts_count': BlogPost.objects.count(),
        'events_count': Event.objects.count(),
    }
    return render(request, 'pages/admin_settings.html', context)


@login_required
@user_passes_test(is_admin)
def admin_messages_view(request):
    """Admin messages view"""
    messages_list = ContactMessage.objects.order_by('-created_at')
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)
    
    context = {
        'messages': messages_page,
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'admin/messages_list.html', context)


@login_required
@user_passes_test(is_admin)
def mark_message_read(request, message_id):
    """Mark message as read"""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'})


# Event registration (for authenticated users)
@login_required
def event_register(request, slug):
    """Register for an event"""
    event = get_object_or_404(Event, slug=slug)
    
    if not event.registration_required:
        messages.error(request, 'Este evento não requer inscrição.')
        return redirect('event_detail', slug=slug)
    
    # É preciso um método is_full() no seu modelo Event.
    # Assumindo que ele existe:
    if hasattr(event, 'is_full') and event.is_full():
        messages.error(request, 'Evento lotado.')
        return redirect('event_detail', slug=slug)
    
    # Simple registration - just increment counter
    event.registered += 1
    event.save()
    
    messages.success(request, f'Inscrição realizada com sucesso para o evento "{event.title}"!')
    return redirect('event_detail', slug=slug)


# ==========================
# ⚙️ Vistas Admin (Classes)
# ==========================

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostListView(ListView):
    model = BlogPost
    template_name = 'admin/posts_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__first_name__icontains=search) |
                Q(author__last_name__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'admin/post_form.html'
    success_url = reverse_lazy('admin_posts')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post criado com sucesso!')
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostUpdateView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'admin/post_form.html'
    success_url = reverse_lazy('admin_posts')
    
    def form_valid(self, form):
        messages.success(self.request, 'Post atualizado com sucesso!')
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'admin/post_confirm_delete.html'
    success_url = reverse_lazy('admin_posts')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deletado com sucesso!')
        return super().delete(request, *args, **kwargs)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventListView(ListView):
    model = Event
    template_name = 'pages/admin_event_form.html'
    context_object_name = 'events'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(organizer__icontains=search) |
                Q(location__icontains=search)
            )

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        # A importação local de EventForm aqui é redundante se estiver no topo.
        # Mas mantive a estrutura original, assumindo que EventForm está no topo.
        context = super().get_context_data(**kwargs)
        context['form'] = EventForm()
        context['is_edit'] = False
        return context

    def post(self, request, *args, **kwargs):
        # A importação local de EventForm aqui é redundante se estiver no topo.
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('admin_events')
        else:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/admin_event_form.html'
    success_url = reverse_lazy('admin_events')
    
    def form_valid(self, form):
        messages.success(self.request, 'Evento criado com sucesso!')
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'pages/admin_event_form.html'
    success_url = reverse_lazy('admin_events')

    def form_valid(self, form):
        messages.success(self.request, "Evento atualizado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar o evento. Verifique os dados.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['event'] = self.object
        return context


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventDeleteView(DeleteView):
    model = Event
    template_name = 'admin/event_confirm_delete.html'
    success_url = reverse_lazy('admin_events')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Evento deletado com sucesso!')
        return super().delete(request, *args, **kwargs)