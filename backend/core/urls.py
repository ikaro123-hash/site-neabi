from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import (
    # Vistas Públicas
    home_view,
    sobre_view,
    projetos_view, # Mantida para a rota sem slug
    semana_consciencia_negra_view,
    BlogListView,
    BlogDetailView,
    EventListView,
    EventDetailView,
    contact_view,
    GalleryListView,
    event_register,
    criar_conta,

    # Vistas Admin (Funções)
    admin_logout_view,
    admin_dashboard_view,
    admin_settings_view,
    admin_messages_view,
    mark_message_read,
    register, 
    login_view,

    # Tags
    tag_list,
    tag_create,
    tag_edit,
    tag_delete,

    # USERS CRUD  
    user_list_view,         
    user_edit,               
    admin_delete_user,      
    admin_edit_user_permissions, 

    # Vistas Admin (Classes)
    AdminPostListView,
    AdminPostCreateView,
    AdminPostUpdateView,
    AdminPostDeleteView,
    AdminEventListView,
    AdminEventCreateView,
    AdminEventUpdateView,
    AdminEventDeleteView,
    AdminCategoryListView,
    AdminCategoryCreateView,
    AdminCategoryUpdateView,
    AdminCategoryDeleteView,
    AdminGalleryListView,
    AdminGalleryCreateView,
    AdminGalleryUpdateView,
    AdminGalleryDeleteView,
    AdminProjectListView,
    admin_project_create,
    admin_project_edit,
    admin_project_delete,
    ProjectListView,
    ProjectDetailView,
)

urlpatterns = [
    # --------------------
    # ROTAS PÚBLICAS
    # --------------------
    path('', home_view, name='home'),
    path('sobre/', sobre_view, name='sobre'),
    path('consciencia-negra/', semana_consciencia_negra_view, name='semana_consciencia_negra'),

    # Blog
    path('blog/', BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),

    # Eventos
    path('eventos/', EventListView.as_view(), name='eventos'),
    path('eventos/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('eventos/<slug:slug>/register/', event_register, name='event_register'),

    # Contato e Galeria
    path('contato/', contact_view, name='contato'),
    path('galeria/', GalleryListView.as_view(), name='galeria'),

    # Projetos Públicos
    path('projetos/', ProjectListView.as_view(), name='project_list'),
    path('projetos/<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
    

    # --------------------
    # AUTENTICAÇÃO
    # --------------------
    path('admin/logout/', admin_logout_view, name='admin_logout'),
    path('register/', register, name='register'), 
    path('criar-conta/', criar_conta, name='criar_conta'), 
    
    # Login para a área administrativa
    path('admin/login/', login_view, name='admin_login'),
    
    # ROTAS DE RECUPERAÇÃO DE SENHA (Usando auth_views)
    path('password-reset/', 
          auth_views.PasswordResetView.as_view(template_name='admin_area/password_reset.html'), 
          name='password_reset'),
    path('password-reset/done/', 
          auth_views.PasswordResetDoneView.as_view(template_name='admin_area/password_reset_done.html'), 
          name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
          auth_views.PasswordResetConfirmView.as_view(template_name='admin_area/password_reset_confirm.html'), 
          name='password_reset_confirm'),
    path('reset/done/', 
          auth_views.PasswordResetCompleteView.as_view(template_name='admin_area/password_reset_complete.html'), 
          name='password_reset_complete'),

    # --------------------
    # ADMIN GERAL
    # --------------------
    path('admin-area/dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('admin-area/settings/', admin_settings_view, name='admin_settings'),
   


      # Lista de mensagens (Admin)
     path('admin-area/messages/', admin_messages_view, name='admin_messages_list'),

     # urls.py
     path('admin-area/messages/mark-read/<int:pk>/', mark_message_read, name='mark_message_read'),


    # --------------------
    # CRUD USUÁRIOS
    # --------------------
    path('admin-area/users/', user_list_view, name='admin_user_list'), 
    path('admin-area/users/edit/<int:user_id>/', user_edit, name='admin_user_edit'), 
    path('admin-area/users/<int:user_id>/permissions/', admin_edit_user_permissions, name='admin_edit_user_permissions'),
    path('admin-area/users/delete/<int:user_id>/', admin_delete_user, name='admin_delete_user'),

    # --------------------
    # CRUD POSTS
    # --------------------
    path('admin-area/posts/', AdminPostListView.as_view(), name='admin_post_list'),
    path('admin-area/posts/create/', AdminPostCreateView.as_view(), name='admin_post_create'),
    path('admin-area/posts/edit/<slug:slug>/', AdminPostUpdateView.as_view(), name='admin_post_update'),
    path('admin-area/posts/delete/<slug:slug>/', AdminPostDeleteView.as_view(), name='admin_post_delete'),

    # --------------------
    # CRUD EVENTOS
    # --------------------
    path('admin-area/events/', AdminEventListView.as_view(), name='admin_event_list'),
    path('admin-area/events/create/', AdminEventCreateView.as_view(), name='admin_event_create'),
    path('admin-area/events/<slug:slug>/edit/', AdminEventUpdateView.as_view(), name='admin_event_update'),
    path('admin-area/events/<slug:slug>/delete/', AdminEventDeleteView.as_view(), name='admin_event_delete'),
    # --------------------
    # CRUD CATEGORIAS
    # --------------------
    path('admin-area/categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('admin-area/categories/create/', AdminCategoryCreateView.as_view(), name='admin_category_create'),
    path('admin-area/categories/edit/<int:pk>/', AdminCategoryUpdateView.as_view(), name='admin_category_edit'),
    path('admin-area/categories/delete/<int:pk>/', AdminCategoryDeleteView.as_view(), name='admin_category_delete'),
        
    # --------------------
    # CRUD GALERIA
    # --------------------
    path('admin-area/gallery/', AdminGalleryListView.as_view(), name='admin_gallery_list'),
    path('admin-area/gallery/create/', AdminGalleryCreateView.as_view(), name='admin_gallery_create'),
    path('admin-area/gallery/edit/<int:pk>/', AdminGalleryUpdateView.as_view(), name='admin_gallery_update'),
    path('admin-area/gallery/delete/<int:pk>/', AdminGalleryDeleteView.as_view(), name='admin_gallery_delete'),

    # --------------------
    # CRUD TAGS
    # --------------------
    path('admin-area/tags/', tag_list, name='admin_tag_list'),
    path('admin-area/tags/create/', tag_create, name='admin_tag_create'), 
    path('admin-area/tags/<int:pk>/edit/', tag_edit, name='admin_tag_edit'),
    path('admin-area/tags/<int:pk>/delete/', tag_delete, name='admin_tag_delete'),


    # --------------------
    # CRUD PROJETOS (ADMIN)
    # --------------------
    path('admin-area/projects/', AdminProjectListView.as_view(), name='admin_project_list'), 
    path('admin-area/projects/create/', admin_project_create, name='admin_project_create'),
    path('admin-area/projects/<int:pk>/edit/', admin_project_edit, name='admin_project_edit'),
    path('admin-area/projects/<int:pk>/delete/', admin_project_delete, name='admin_project_delete'),


]