from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Páginas públicas
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('menu/', views.menu, name='menu'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Cambiado a vista personalizada
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dashboards específicos
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('personal/dashboard/', views.personal_dashboard, name='personal_dashboard'),
    path('cliente/dashboard/', views.cliente_dashboard, name='cliente_dashboard'),
    
    # Funcionalidades personal
    path('personal/editar-perfil/', views.editar_perfil_personal, name='editar_perfil_personal'),
    
    # Funcionalidades cliente
    path('cliente/hacer-pedido/', views.hacer_pedido, name='hacer_pedido'),
    path('cliente/reservar-mesa/', views.reservar_mesa, name='reservar_mesa'),
    path('cliente/pedidos/', views.ver_pedidos, name='ver_pedidos'),
    path('cliente/reservas/', views.ver_reservas, name='ver_reservas'),
    path('cliente/comentarios/', views.hacer_comentario, name='hacer_comentario'),
    path('cliente/editar-perfil/', views.editar_perfil_cliente, name='editar_perfil_cliente'),
    
    # Funcionalidades admin
    path('administrador/gestionar-menu/', views.gestionar_menu, name='gestionar_menu'),
    path('administrador/gestionar-personal/', views.gestionar_personal, name='gestionar_personal'),
    path('administrador/comentarios/', views.ver_comentarios, name='ver_comentarios'),
    path('administrador/reportes/', views.generar_reporte, name='generar_reporte'),
    path('admin/gestionar-reservas/', views.gestionar_reservas, name='gestionar_reservas'),
    
]