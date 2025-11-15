from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rol', 'telefono', 'direccion')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('rol', 'telefono', 'direccion')}),
    )

class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible', 'restaurante')
    list_filter = ('categoria', 'disponible', 'restaurante')
    search_fields = ('nombre', 'descripcion')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_pedido', 'estado', 'total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('cliente__username', 'cliente__email')

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_reserva', 'numero_personas', 'estado')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('cliente__username', 'cliente__email')

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'calificacion', 'fecha', 'aprobado')
    list_filter = ('calificacion', 'aprobado', 'fecha')
    search_fields = ('cliente__username', 'texto')

# Registrar modelos en el admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Restaurante)
admin.site.register(Categoria)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemPedido)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Reporte)