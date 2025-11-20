from django.urls import path, include
from .views import (
    # Vistas Públicas
    home_view,
    sobre_view,
    projetos_view,
    semana_consciencia_negra_view,
    BlogListView,
    BlogDetailView,
    EventListView,
    EventDetailView,
    contact_view,
    GalleryListView,
    event_register,
    
    # Vistas de Autenticação/Admin (Funções)
    admin_login_view,
    admin_logout_view,
    admin_dashboard_view,
    admin_dashboard, # Embora duplicada, mantida se estiver em uso
    admin_users_view,
    admin_settings_view,
    admin_messages_view,
    mark_message_read,
    admin_tags_view,

    # Vistas Admin (Classes) - AS VISTAS CORRIGIDAS ESTÃO AQUI
    AdminPostListView,
    AdminPostCreateView,
    AdminPostUpdateView,
    AdminPostDeleteView,
    AdminEventListView,
    AdminEventCreateView,
    AdminEventUpdateView,
    AdminEventDeleteView,
    AdminCategoryListView,
)


urlpatterns = [
    # Rotas Públicas
    path('', home_view, name='home'),
    path('sobre/', sobre_view, name='sobre'),
    path('projetos/', projetos_view, name='projetos'),
    path('consciencia-negra/', semana_consciencia_negra_view, name='semana_consciencia_negra'),
    path('blog/', BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='post_detail'),
    path('eventos/', EventListView.as_view(), name='eventos'),
    path('eventos/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('contato/', contact_view, name='contato'),
    path('galeria/', GalleryListView.as_view(), name='galeria'),
    path('eventos/<slug:slug>/register/', event_register, name='event_register'),
    
    # Rotas de Autenticação
    path('admin/login/', admin_login_view, name='admin_login'),
    path('admin/logout/', admin_logout_view, name='admin_logout'),

    # Rotas Admin (Dashboard e Gerais)
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('admin/users/', admin_users_view, name='admin_users'),
    path('admin/settings/', admin_settings_view, name='admin_settings'),
    path('admin/messages/', admin_messages_view, name='admin_messages'),
    path('admin/messages/read/<int:message_id>/', mark_message_read, name='mark_message_read'),
    path('admin/tags/', admin_tags_view, name='admin_tags'),


    # 🚨 Rotas Admin de Posts (CORRIGIDAS)
    path('admin/posts/', AdminPostListView.as_view(), name='admin_posts'),
    path('admin/posts/new/', AdminPostCreateView.as_view(), name='admin_post_create'),
    path('admin/posts/edit/<slug:slug>/', AdminPostUpdateView.as_view(), name='admin_post_update'),
    path('admin/posts/delete/<slug:slug>/', AdminPostDeleteView.as_view(), name='admin_post_delete'),

    # 🚨 Rotas Admin de Eventos (USAM AS CLASSES VIEW)
    # Nota: O AdminEventListView no seu views.py parece ser um CRUD completo (Listar + Criar)
    path('admin/events/', AdminEventListView.as_view(), name='admin_events'),
    path('admin/events/create/', AdminEventCreateView.as_view(), name='admin_event_create'), # Alternativa mais limpa
    path('admin/events/edit/<slug:slug>/', AdminEventUpdateView.as_view(), name='admin_event_update'),
    path('admin/events/delete/<slug:slug>/', AdminEventDeleteView.as_view(), name='admin_event_delete'),
    
    # 🚨 Rotas Admin de Categorias
    path('admin/categories/', AdminCategoryListView.as_view(), name='admin_categories'),
]
