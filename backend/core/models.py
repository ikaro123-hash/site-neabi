from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import itertools
# Importação para usar a função de tradução (opcional, mas boa prática)
from django.utils.translation import gettext_lazy as _ 


class User(AbstractUser):
    """Extended user model with role-based permissions"""
    ROLE_CHOICES = [
        ('admin', _('Administrador')),
        ('reader', _('Leitor')),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='reader',
        verbose_name=_('Função')
    )
    first_name = models.CharField(max_length=150, verbose_name=_('Nome'))
    last_name = models.CharField(max_length=150, verbose_name=_('Sobrenome'))
    
    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_admin(self):
        return self.role == 'admin'



class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_("URL"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))  

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 1. Se NÃO tem slug, cria pelo nome
        if not self.slug:
            self.slug = slugify(self.name)
        # 2. Se TEM slug (você digitou), garante que ele esteja formatado (sem espaços, minúsculo)
        else:
            self.slug = slugify(self.slug)
        
        # 3. Garante que não é duplicado
        orig_slug = self.slug
        for x in itertools.count(1):
            if not Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                break
            self.slug = '%s-%d' % (orig_slug, x)
            
        super().save(*args, **kwargs)
    
class Tag(models.Model):
    """Tags for blog posts and events"""
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Nome'))
    slug = models.SlugField(unique=True, verbose_name=_('URL'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Blog post model"""
    
    STATUS_CHOICES = [
        ('draft', _('Rascunho')), 
        ('published', _('Publicado')),
        ('archived', _('Arquivado')),

    ]

    title = models.CharField(max_length=200, verbose_name=_('Título'))
    slug = models.SlugField(unique=True, verbose_name=_('URL'))
    excerpt = models.TextField(max_length=300, verbose_name=_('Resumo'))
    content = models.TextField(verbose_name=_('Conteúdo'))
    
    # MODIFICAÇÃO: author agora permite NULL e usa SET_NULL em caso de exclusão
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name=_('Autor')
    )
    
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name=_('Categoria'))
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_('Tags'))
    published_date = models.DateTimeField(default=timezone.now, verbose_name=_('Data de publicação'))
    read_time = models.CharField(max_length=20, default='5 min', verbose_name=_('Tempo de leitura'))
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name=_('Imagem'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('Visualizações'))
    likes = models.PositiveIntegerField(default=0, verbose_name=_('Curtidas'))
    featured = models.BooleanField(default=False, verbose_name=_('Destaque'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name=_('Status'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Post do Blog')
        verbose_name_plural = _('Posts do Blog')
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_tags_list(self):
        return list(self.tags.values_list('name', flat=True))


class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', _('Próximo')),
        ('ongoing', _('Em andamento')),
        ('completed', _('Finalizado')),
        ('cancelled', _('Cancelado')),
    ]

    TYPE_CHOICES = [
        ('presencial', _('Presencial')),
        ('online', _('Online')),
        ('hibrido', _('Híbrido')),
    ]

    title = models.CharField(max_length=200, verbose_name=_('Título'))
    slug = models.SlugField(unique=True, verbose_name=_('URL'), blank=True)
    description = models.TextField(verbose_name=_('Descrição'))
    date = models.DateField(verbose_name=_('Data'))
    start_time = models.TimeField(verbose_name=_('Hora de início'))
    end_time = models.TimeField(verbose_name=_('Hora de término'))
    location = models.CharField(max_length=200, verbose_name=_('Local'))

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Categoria'),
    )

    event_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='presencial',
        verbose_name=_('Tipo de evento')
    )

    capacity = models.PositiveIntegerField(verbose_name=_('Capacidade'))
    registered = models.PositiveIntegerField(default=0, verbose_name=_('Inscritos'))
    organizer = models.CharField(max_length=200, verbose_name=_('Organizador'))
    speakers = models.TextField(
        blank=True,
        help_text=_("Lista de palestrantes separados por vírgula"),
        verbose_name=_('Palestrantes')
    )
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_('Tags'))
    image = models.ImageField(
        upload_to='event_images/',
        blank=True,
        null=True,
        verbose_name=_('Imagem')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        verbose_name=_('Status')
    )
    featured = models.BooleanField(default=False, verbose_name=_('Destaque'))
    registration_required = models.BooleanField(default=True, verbose_name=_('Inscrição obrigatória'))
    price = models.CharField(max_length=50, default="Gratuito", verbose_name=_('Preço'))
    registration_link = models.URLField(blank=True, null=True, verbose_name=_("Link de inscrição"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Criado em'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Atualizado em'))

    class Meta:
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventos')
        ordering = ['date', 'start_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})

    def get_speakers_list(self):
        if self.speakers:
            return [speaker.strip() for speaker in self.speakers.split(',') if speaker.strip()]
        return []

    def is_full(self):
        return self.registered >= self.capacity

    def spots_remaining(self):
        return max(0, self.capacity - self.registered)

class ContactMessage(models.Model):
    """Contact form messages"""
    name = models.CharField(max_length=100, verbose_name=_('Nome'))
    email = models.EmailField(verbose_name=_('Email'))
    subject = models.CharField(max_length=200, verbose_name=_('Assunto'))
    message = models.TextField(verbose_name=_('Mensagem'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Enviado em'))
    is_read = models.BooleanField(default=False, verbose_name=_('Lida'))

    class Meta:
        verbose_name = _('Mensagem de Contato')
        verbose_name_plural = _('Mensagens de Contato')
        ordering = ['-created_at']

    def __str__(self):
        # Apenas mostra nome e assunto; não mostra status
        return f"{self.name} - {self.subject}"
    
    
class GalleryGroup(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class GalleryImage(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Título da Imagem"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    image = models.ImageField(upload_to='gallery/', verbose_name=_("Arquivo da Imagem"))
    event = models.ForeignKey(
        'Event', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("Evento Relacionado")
    )
    published = models.BooleanField(default=True, verbose_name=_("Publicado"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data de Upload"))

    class Meta:
        verbose_name = _("Imagem da Galeria")
        verbose_name_plural = _("Imagens da Galeria")
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

class Project(models.Model):

    title = models.CharField( max_length=200, verbose_name=_("Título"))
    description = models.TextField(verbose_name=_("Descrição"))
    image = models.ImageField(upload_to='projects/', blank=True, null=True, verbose_name=_("Imagem")) 
    category = models.ForeignKey('Category',on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Categoria"))

    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name=_("Tags")
    )

    link_to_join = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Link de Acesso"),
        help_text=_("Link externo para participação ou inscrição")
    )

    status = models.BooleanField(
        default=True,
        verbose_name=_("Ativo")
    )

    featured = models.BooleanField(
        default=False,
        verbose_name=_("Destaque")
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("Slug")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em")
    )

    def save(self, *args, **kwargs):
        """Gera slug único automaticamente para evitar conflitos."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title