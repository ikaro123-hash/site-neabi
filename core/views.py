from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin # Para garantir que apenas admins acessem
from django.utils.text import slugify

# IMPORTAÇÕES DE FORMULÁRIOS
from .forms import (
    BlogPostForm,
    EventForm,
    SearchForm,
    ContactForm,
    CategoryForm,
    GalleryImageForm,
    UserRegistrationForm,
    UserPermissionForm,
    TagForm,
    CadastroUsuarioForm,
    ProjectForm,
)

from .models import BlogPost, Event, Category, ContactMessage, GalleryImage ,Tag ,Project

User = get_user_model()


# ==========================
# Função Auxiliar
# ==========================
def is_admin(user):
    """Verifica se o usuário é admin (is_staff ou is_superuser)."""
    return user.is_staff or user.is_superuser


# ==========================
# 🌐 Views Públicas
# ==========================
def home_view(request):
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
    return render(request, 'pages/sobre.html')

def projetos_view(request):
    return render(request, 'pages/projetos.html')

def semana_consciencia_negra_view(request):
    return render(request, 'pages/semana_consciencia_negra.html')

class BlogListView(ListView):
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
    
# LISTAR TAGS
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'admin/tags_list.html', {'tags': tags})


# CRIAR TAG
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_tag_list')
    else:
        form = TagForm()
    
    return render(request, 'admin/tag_form.html', {
        'form': form,
        'title': 'Criar Tag'
    })


# EDITAR TAG
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('admin_tag_list')
    else:
        form = TagForm(instance=tag)

    return render(request, 'admin/tag_form.html', {
        'form': form,
        'title': 'Editar Tag'
    })


# EXCLUIR TAG
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    return redirect('admin_tag_list')

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'pages/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(status='published')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Incrementa visualizações
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj
    

def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)  # Busca o evento pelo ID

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)  # Passa a instância
        if form.is_valid():
            form.save()
            messages.success(request, "Evento atualizado com sucesso!")
            return redirect('admin_event_list')  # Redireciona para a lista de eventos
    else:
        form = EventForm(instance=event)  # Preenche o formulário com os dados existentes

    return render(request, 'admin/edit_event.html', {'form': form, 'event': event})
    


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso!")
            return redirect('admin_login')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

    

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, 'admin_area/login.html')

    
# Listar usuários
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin_area/user_list.html', {'users': users})

def admin_user_list(request):
    users = User.objects.all().order_by("id")
    return render(request, "admin_area/user_list.html", {"users": users})


def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "Usuário excluído com sucesso!")
        return redirect("admin_user_list")


    return render(request, "admin_area/confirm_delete_user.html", {"user": user})



    

class EventListView(ListView):
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
    model = Event
    template_name = 'pages/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem enviada com sucesso!')
            return redirect('contato')
    else:
        form = ContactForm()
    return render(request, 'pages/contato.html', {'form': form})

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'admin/admin_event_form.html'
    success_url = reverse_lazy('event_list')

    # ⚠ configurando slug
    slug_field = 'slug'          # campo do modelo
    slug_url_kwarg = 'slug'      # nome do parâmetro na URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Evento'
        return context

    

class GalleryListView(ListView):
    model = GalleryImage
    template_name = 'pages/galeria.html'
    context_object_name = 'images'
    paginate_by = 12

    def get_queryset(self):
        queryset = GalleryImage.objects.filter(published=True)
        event_id = self.request.GET.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        return queryset.order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events_with_images'] = Event.objects.filter(galleryimage__published=True).distinct()
        return context


def event_register(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if not event.registration_required:
        messages.error(request, 'Este evento não requer inscrição.')
        return redirect('event_detail', slug=slug)
    # Assumindo que is_full é um método que existe no modelo Event
    if hasattr(event, 'is_full') and event.is_full():
        messages.error(request, 'Evento lotado.')
        return redirect('event_detail', slug=slug)
        
    # Lógica de registro simples
    # Nota: Em um sistema real, você registraria o usuário (ou um objeto Inscrição) aqui
    event.registered += 1
    event.save()
    messages.success(request, f'Inscrição realizada com sucesso para "{event.title}"!')
    return redirect('event_detail', slug=slug)

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST) # ⬅️ CORRIGIDO
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm() # ⬅️ CORRIGIDO

    return render(request, 'pages/register.html', {'form': form})


# ==========================
# 🔑 Vistas de Autenticação/Admin
# ==========================

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')  # ajuste para o dashboard
        else:
            messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'admin_area/login.html')

def edit_user_permissions(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user_obj.is_active = 'is_active' in request.POST
        user_obj.is_staff = 'is_staff' in request.POST
        user_obj.is_superuser = 'is_superuser' in request.POST
        user_obj.save()

        return redirect('user_list')

    return render(request, 'admin_area/edit_user_permissions.html', {
        'user_obj': user_obj
    })


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        # Tenta autenticar por username
        user = authenticate(request, username=username_or_email, password=password)

        # Se não achou, tenta por email (opcional)
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo, {user.get_full_name()}!")
            return redirect('home')  # Coloque aqui a rota da página inicial
        else:
            messages.error(request, "Usuário ou senha incorretos!")

    return render(request, 'login.html')


# CORREÇÃO NA VIEW criar_conta
def criar_conta(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # ✅ Ação: Logar o usuário automaticamente após o registro
            login(request, user) 
            
            messages.success(request, 'Conta criada com sucesso! Bem-vindo(a)!')
            
            # ✅ Redireciona para o painel de controle (dashboard)
            return redirect('admin_dashboard') 
        
        else:
            # Se o formulário não for válido, os erros são renderizados no template
            messages.error(request, 'Ocorreu um erro no registro. Verifique os campos.')
            
    else:
        form = CadastroUsuarioForm()
        
    return render(request, 'criar_conta.html', {'form': form})

@login_required
def admin_logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('home')


# =======================================================
#  ADMIN – LISTAR PROJETOS
# =======================================================
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminProjectListView(ListView):
    model = Project
    template_name = 'admin/admin_project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectForm()
        return context


# =======================================================
#  ADMIN – CRIAR PROJETO
# =======================================================
@login_required
@user_passes_test(is_admin)
def admin_project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_project_list')

    else:
        form = ProjectForm()

    return render(request, 'admin/admin_project_form.html', {
        'form': form,
        'object': None
    })


# =======================================================
#  ADMIN – EDITAR PROJETO
# =======================================================
@login_required
@user_passes_test(is_admin)
def admin_project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('admin_project_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'admin/admin_project_form.html', {
        'form': form,
        'object': project
    })




# =======================================================
#  ADMIN – DELETAR PROJETO
# =======================================================
@login_required
@user_passes_test(is_admin)
def admin_project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('admin_project_list')


# =======================================================
#  SITE – LISTA PÚBLICA DE PROJETOS
# =======================================================
class ProjectListView(ListView):
    model = Project
    template_name = "projetos.html"
    context_object_name = "projects"

    def get_queryset(self):
        # Filtra apenas projetos ativos (status=True) e ordena do mais recente para o mais antigo
        return Project.objects.filter(status=True).order_by('-created_at')

# =======================================================
#  SITE – DETALHE DO PROJETO PÚBLICO
# =======================================================
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'


# -----------------------------------
# 1. LISTAR (Tabela de categorias)
class AdminCategoryListView(ListView):
    model = Category
    template_name = 'admin/categories_list.html'
    context_object_name = 'object_list'

class AdminCategoryCreateView(CreateView):
    model = Category
    # ADICIONADO 'slug' AQUI:
    fields = ['name', 'slug'] 
    template_name = 'admin/category_create.html'
    success_url = reverse_lazy('admin_category_list')

class AdminCategoryUpdateView(UpdateView):
    model = Category
    fields = ['name', 'slug']
    template_name = 'admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')
# 4. EXCLUIR (Confirmação de deleção)
class AdminCategoryDeleteView(DeleteView):
    model = Category
    template_name = 'admin/category_confirm_delete.html'
    success_url = reverse_lazy('admin_category_list')

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """
    CORRIGIDO: Esta função calcula todas as estatísticas necessárias do banco de dados 
    para o dashboard e passa para o template.
    """
    stats = {
        'total_posts': BlogPost.objects.count(),
        # Total de posts com status='published'
        'published_posts': BlogPost.objects.filter(status='published').count(), 
        'total_events': Event.objects.count(),
        # Total de imagens na galeria
        'total_images': GalleryImage.objects.count(),                           
        'users': User.objects.count(),
        # Total de mensagens não lidas
        'messages': ContactMessage.objects.filter(is_read=False).count(),
    }
    
    recent_posts = BlogPost.objects.order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')[:5]
    recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
    
    context = {
        'stats': stats, # Passando todas as estatísticas em um único dicionário
        'recent_posts': recent_posts,
        'upcoming_events': upcoming_events,
        'recent_messages': recent_messages,
    }
    return render(request, 'admin/dashboard.html', context)



@login_required
@user_passes_test(lambda u: u.is_superuser)  # Apenas superusuários
def admin_edit_user_permissions(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Ativo/desativo
        user_obj.is_active = 'is_active' in request.POST

        # Role (função NEABI)
        role = request.POST.get("role")
        user_obj.role = role  # salva no campo customizado

        # Sincroniza is_staff / is_superuser
        if role == "admin":
            user_obj.is_staff = True
            user_obj.is_superuser = True
        elif role == "reader":
            user_obj.is_staff = True
            user_obj.is_superuser = False
        else:
            user_obj.is_staff = False
            user_obj.is_superuser = False

        # DEBUG
        print(f"Salvando: Active={user_obj.is_active}, Staff={user_obj.is_staff}, Superuser={user_obj.is_superuser}, Role={user_obj.role}")

        # Salva alterações
        user_obj.save()

        messages.success(request, f"Permissões de {user_obj.username} atualizadas com sucesso!")

        return redirect(request.path)

    return render(request, "admin_area/user_permissions.html", {"user_obj": user_obj})


# ==========================
# Outras Vistas Administrativas
# ==========================
@login_required
@user_passes_test(is_admin)
def admin_users_view(request):
    users = User.objects.all()
    return render(request, 'pages/admin_users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def admin_settings_view(request):
    context = {
        'users_count': User.objects.count(),
        'posts_count': BlogPost.objects.count(),
        'events_count': Event.objects.count(),
    }
    return render(request, 'pages/admin_settings.html', context)

@login_required
@user_passes_test(is_admin)
def admin_messages_view(request):
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
    """Marca uma mensagem de contato como lida via AJAX."""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_admin)
def admin_tags_view(request):
    return render(request, 'admin/tags.html')

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    """Lista todos os usuários para o admin."""
    users = User.objects.all().order_by("id")
    return render(request, "admin/user_list.html", {"users": users})

@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'admin_area/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Usuário atualizado com sucesso!')
        return redirect('admin_user_list')
    return render(request, 'admin_area/user_edit.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'Usuário {user.username} excluído com sucesso!')
        return redirect('admin_user_list')
    return render(request, 'admin_area/user_delete.html', {'user': user})
# ==========================
# Admin Posts CRUD
# ==========================
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostListView(ListView):
    model = BlogPost
    template_name = 'admin/posts_list.html'
    context_object_name = 'admin_post_list'
    paginate_by = 20
    ordering = ['-created_at']

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'admin/post_form.html'
    success_url = reverse_lazy('admin_post_list')

    def form_valid(self, form):
        # Define o autor do post
        form.instance.author = self.request.user

        # Gera um slug único
        base_slug = slugify(form.instance.title)
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        form.instance.slug = slug

        # Adiciona mensagem de sucesso
        messages.success(self.request, 'Post criado com sucesso!')

        return super().form_valid(form)

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostUpdateView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'admin/post_form.html'
    success_url = reverse_lazy('admin_post_list')
    def form_valid(self, form):
        messages.success(self.request, 'Post atualizado com sucesso!')
        return super().form_valid(form)

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'admin/post_confirm_delete.html'
    success_url = reverse_lazy('admin_post_list')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Post deletado com sucesso!')
        return super().delete(request, *args, **kwargs)
    
@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminGalleryListView(ListView):
    model = GalleryImage
    template_name = 'admin/gallery_list.html'
    context_object_name = 'images'
    ordering = ['-uploaded_at'] 
    paginate_by = 20




# ==========================
# Admin Eventos CRUD
# ==========================
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventListView(ListView):
    model = Event
    template_name = 'admin/admin_event_list.html'
    context_object_name = 'events'
    paginate_by = 20
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EventForm()  # Cria o formulário vazio para renderizar
        return context


# -------------------- CREATE --------------------
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'admin/admin_event_form.html'  # ou 'admin/event_list.html' se usar o template que você enviou
    success_url = reverse_lazy('admin_event_list')  # lista de eventos no admin

    def form_valid(self, form):
        # Gera slug único automaticamente
        base_slug = slugify(form.instance.title)
        slug = base_slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        form.instance.slug = slug

        # Mensagem de sucesso
        messages.success(self.request, "Evento criado com sucesso!")
        return super().form_valid(form)


# -------------------- UPDATE --------------------
class AdminEventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'admin/admin_event_form.html'
    success_url = reverse_lazy('admin_event_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        # Atualiza o slug se o título mudou
        if 'title' in form.changed_data:
            base_slug = slugify(form.instance.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.object.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            form.instance.slug = slug

        messages.success(self.request, "Evento atualizado com sucesso!")
        return super().form_valid(form)


@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminEventDeleteView(DeleteView):
    model = Event
    template_name = 'admin/admin_event_confirm_delete.html'
    success_url = reverse_lazy('admin_event_list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Evento deletado com sucesso!')
        return super().delete(request, *args, **kwargs)
    


# ==========================
# Admin Categorias CRUD
# ==========================
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminCategoryListView(ListView):
    model = Category
    template_name = 'admin/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CategoryForm()
        return context

# ==========================
# Admin Galeria CRUD
# ==========================
@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminGalleryListView(ListView):
    model = GalleryImage
    template_name = 'admin/gallery_list.html'
    context_object_name = 'images'
    paginate_by = 20
    ordering = ['-uploaded_at']

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminGalleryCreateView(CreateView):
    model = GalleryImage
    form_class = GalleryImageForm
    template_name = 'admin/gallery_form.html'
    success_url = reverse_lazy('admin_gallery_list')
    def form_valid(self, form):
        messages.success(self.request, 'Imagem adicionada à galeria com sucesso!')
        return super().form_valid(form)

@method_decorator([login_required, user_passes_test(is_admin)], name='dispatch')
class AdminGalleryUpdateView(UpdateView):
    model = GalleryImage
    form_class = GalleryImageForm
    template_name = 'admin/gallery_form.html'
    success_url = reverse_lazy('admin_gallery_list')  # <-- nome correto
    def form_valid(self, form):
        messages.success(self.request, 'Imagem atualizada com sucesso!')
        return super().form_valid(form)

@method_decorator(user_passes_test(is_admin), name='dispatch')
class AdminGalleryDeleteView(DeleteView):
    model = GalleryImage
    template_name = 'admin/gallery_confirm_delete.html' # Template de confirmação
    success_url = reverse_lazy('admin_gallery_list') # Redireciona para a lista
    
    # Você já corrigiu o IndentationError neste método:
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Imagem excluída com sucesso.")
        return super().delete(request, *args, **kwargs)

@method_decorator([login_required], name='dispatch')
class UserListView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'admin_area/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def test_func(self):
        # Só admins podem acessar
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para acessar esta página.")
        return redirect('home')  # ou qualquer outra página segura

@method_decorator([login_required], name='dispatch')
class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserPermissionForm  # ou UserRegistrationForm se quiser editar nome/email/senha
    template_name = 'admin_area/user_edit.html'
    success_url = reverse_lazy('admin_user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para editar usuários.")
        return redirect('home')

@method_decorator([login_required], name='dispatch')
class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'admin_area/user_delete.html'
    success_url = reverse_lazy('admin_user_list')

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para excluir usuários.")
        return redirect('home')




