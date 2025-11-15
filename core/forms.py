from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Pedido, Reserva, Comentario, ItemPedido

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono', 'direccion', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases Bootstrap a todos los campos
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion_entrega', 'notas']
        widgets = {
            'direccion_entrega': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ReservaForm(forms.ModelForm):
    fecha_reserva = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Reserva
        fields = ['fecha_reserva', 'numero_personas', 'notas']
        widgets = {
            'numero_personas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto', 'calificacion', 'pedido']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'calificacion': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'pedido': forms.Select(attrs={'class': 'form-control'}),
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }