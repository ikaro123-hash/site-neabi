from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from crispy_forms.bootstrap import FormActions
from .models import User, BlogPost, Event, ContactMessage, Category, GalleryImage, Tag , Project



class NEABIAuthenticationForm(AuthenticationForm):
    """Custom login form with NEABI styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', placeholder='Email ou nome de usuário'),
            Field('password', placeholder='Senha'),
            FormActions(
                Submit('submit', 'Entrar', css_class='btn btn-primary w-100')
            )
        )
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']  # ou ['name'] se quiser esconder o slug
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nome da Categoria'}),
            'slug': forms.TextInput(attrs={'placeholder': 'Slug (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = False
        self.fields['slug'].label = False

class ContactForm(forms.ModelForm):
    """Contact form for the website"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Assunto da mensagem'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Escreva sua mensagem aqui...',
                'rows': 6
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col-md-6'),
                Div('email', css_class='col-md-6'),
                css_class='row'
            ),
            Field('subject'),
            Field('message'),
            FormActions(
                Submit('submit', 'Enviar Mensagem', css_class='btn btn-primary')
            )
        )


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'excerpt', 'content', 'category', 'tags', 
             'image', 'featured', 'status', 'author'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do post'}),
            'excerpt': forms.Textarea(attrs={
                'placeholder': 'Resumo do post (máximo 300 caracteres)',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Conteúdo completo do post',
                'rows': 15
            }),
            'read_time': forms.TextInput(attrs={'placeholder': '5 min'}),
            'tags': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h4>Informações Básicas</h4>'),
            Field('title'),
            Field('excerpt'),
            Field('content'),
            HTML('<hr><h4>Metadados</h4>'),
            Div(
                Div('category', css_class='col-md-6'),
                Div('read_time', css_class='col-md-6'),
                Div('author', css_class='col-md-6'), 
                css_class='row'
            ),
            Field('tags'),
            HTML('<hr><h4>Publicação</h4>'),
            Div(
                Div('status', css_class='col-md-6'),
                Div('featured', css_class='col-md-6'),
                css_class='row'
            ),
            Field('image'),
            FormActions(
                Submit('submit', 'Salvar Post', css_class='btn btn-primary'),
                HTML('<a href="{% url \'admin_posts\' %}" class="btn btn-secondary">Cancelar</a>')
            )
        )

class EventForm(forms.ModelForm):
    category_name = forms.CharField(
        required=False,
        label="Categoria",
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:ring-green-700 focus:border-green-700 sm:text-base p-3',
            'placeholder': 'Digite uma categoria'
        })
    )

    class Meta:
        model = Event
        # Removido 'price'
        fields = [
            'title', 'slug', 'description', 'date', 'start_time', 'end_time',
            'location', 'capacity', 'organizer', 'speakers', 'tags', 'image',
            'status', 'event_type', 'featured', 'registration_required',
            'registration_link'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'slug': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'location': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'capacity': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
            'registration_link': forms.URLInput(attrs={'class': 'mt-1 block w-full rounded-lg border-gray-300 shadow-sm p-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div('title', css_class='col-md-6'),
                Div('slug', css_class='col-md-6'),
                css_class='row'
            ),
            Div(
                Div('category_name', css_class='col-md-6'),
                Div('capacity', css_class='col-md-6'),
                css_class='row'
            ),
            Div('description'),
            Div(
                Div('date', css_class='col-md-4'),
                Div('start_time', css_class='col-md-4'),
                Div('end_time', css_class='col-md-4'),
                css_class='row'
            ),
            Div('location'),
            Div('organizer'),
            Div('speakers'),
            Div('tags'),
            Div('image'),
            Div(
                Div('status', css_class='col-md-4'),
                Div('event_type', css_class='col-md-4'),
                Div('featured', css_class='col-md-4'),
                css_class='row'
            ),
            Div('registration_required'),
            Div('registration_link'),
            Submit('submit', 'Salvar', css_class='btn btn-primary mt-3')
        )

    def clean_slug(self):
        """Garante que o slug seja único, mas permite atualizar o evento atual"""
        slug = self.cleaned_data['slug']
        qs = Event.objects.filter(slug=slug)
        if self.instance.pk:
            # Se for edição, exclui o próprio evento da verificação
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Evento com este URL já existe.")
        return slug

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]



class SearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Nenhuma",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Div(
                Div('search', css_class='col-md-8'),
                Div('category', css_class='col-md-4'),
                css_class='row align-items-end'
            ),
            FormActions(
                Submit('submit', 'Buscar', css_class='btn btn-primary')
            )
        )
class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['title', 'event', 'image', 'published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'event': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }    
class UserPermissionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        ]
        widgets = {
            "groups": forms.CheckboxSelectMultiple(),
            "user_permissions": forms.CheckboxSelectMultiple(),
        }

# core/forms.py
from django import forms
from .models import Tag

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class NEABICreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-600'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-600'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-600'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-amber-600'
            }),
        }

    # Permitir senhas menos rígidas
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 4:  # Senha mínima de 4 caracteres
            raise forms.ValidationError("A senha deve ter pelo menos 4 caracteres.")
        return password1
    
class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget=forms.TextInput(attrs={
            'placeholder': 'seu.email@exemplo.com',
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-amber-500 focus:border-amber-500 sm:text-sm'
        })
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'image',
            'category', 'tags',
            'link_to_join',
            'status',     
            'featured',     
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple(),
        }
