from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import *
from .forms import *

def es_admin(user):
    return user.is_authenticated and user.rol == 'admin'

def es_personal(user):
    return user.is_authenticated and user.rol in ['personal', 'admin']

def es_cliente(user):
    return user.is_authenticated and user.rol == 'cliente'

def index(request):
    return render(request, 'core/index.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'cliente'  # Todos los registros son clientes por defecto
            user.save()
            
            # Autenticar y loguear al usuario automáticamente
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido a nuestro restaurante.')
                return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    print(f"Usuario: {user.username}, Rol: {user.rol}")
    
    if user.rol == 'admin' or user.is_superuser:
        return redirect('admin_dashboard')
    elif user.rol == 'personal':
        return redirect('personal_dashboard')
    else:
        return redirect('cliente_dashboard')


@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    # Estadísticas para el admin
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    total_ventas = Pedido.objects.filter(estado='entregado').aggregate(Sum('total'))['total__sum'] or 0
    total_clientes = Usuario.objects.filter(rol='cliente').count()
    total_personal = Usuario.objects.filter(rol='personal').count()
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.all().order_by('-fecha_pedido')[:5]
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'total_ventas': total_ventas,
        'total_clientes': total_clientes,
        'total_personal': total_personal,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(es_admin)
def gestionar_menu(request):
    """Vista para que el admin gestione el menú"""
    categorias = Categoria.objects.all()
    productos = Menu.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # AGREGAR PRODUCTO
        if action == 'agregar_producto':
            nombre = request.POST.get('nombre')
            precio = request.POST.get('precio')
            categoria_id = request.POST.get('categoria')
            descripcion = request.POST.get('descripcion')

            restaurante = Restaurante.objects.first()   # o request.user.restaurante

            Menu.objects.create(
            nombre=nombre,
            precio=precio,
            categoria_id=categoria_id,
            descripcion=descripcion,
            disponible=True,
             restaurante=restaurante
            )

            
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('gestionar_menu')

        # ACTIVAR / DESACTIVAR PRODUCTO
        elif action == 'toggle_disponible':
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Menu, id=producto_id)
            producto.disponible = not producto.disponible
            producto.save()
            messages.success(request, 'Estado de disponibilidad actualizado.')
            return redirect('gestionar_menu')

        # ELIMINAR PRODUCTO
        elif action == 'eliminar_producto':
            producto_id = request.POST.get('producto_id')
            producto = get_object_or_404(Menu, id=producto_id)
            producto_nombre = producto.nombre
            producto.delete()
            messages.success(request, f'Producto "{producto_nombre}" eliminado.')
            return redirect('gestionar_menu')

    context = {
        'categorias': categorias,
        'productos': productos,
    }
    return render(request, 'core/gestionar_menu.html', context)



@login_required
@user_passes_test(es_admin)
def ver_comentarios(request):
    """Vista para que el admin vea y gestione comentarios"""
    comentarios = Comentario.objects.all().order_by('-fecha')
    
    if request.method == 'POST':
        comentario_id = request.POST.get('comentario_id')
        action = request.POST.get('action')
        
        try:
            comentario = Comentario.objects.get(id=comentario_id)
            
            if action == 'aprobar':
                comentario.aprobado = True
                comentario.save()
                messages.success(request, 'Comentario aprobado.')
            elif action == 'eliminar':
                comentario.delete()
                messages.success(request, 'Comentario eliminado.')
                
        except Comentario.DoesNotExist:
            messages.error(request, 'Comentario no encontrado.')
    
    context = {
        'comentarios': comentarios,
    }
    return render(request, 'core/ver_comentarios.html', context)

@login_required
@user_passes_test(es_admin)
def generar_reporte(request):
    """Vista para que el admin genere reportes"""
    # Estadísticas básicas
    hoy = datetime.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)
    
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    pedidos_semana = Pedido.objects.filter(fecha_pedido__date__gte=semana_pasada).count()
    pedidos_mes = Pedido.objects.filter(fecha_pedido__date__gte=mes_pasado).count()
    
    ventas_hoy = Pedido.objects.filter(fecha_pedido__date=hoy, estado='entregado').aggregate(Sum('total'))['total__sum'] or 0
    ventas_semana = Pedido.objects.filter(fecha_pedido__date__gte=semana_pasada, estado='entregado').aggregate(Sum('total'))['total__sum'] or 0
    ventas_mes = Pedido.objects.filter(fecha_pedido__date__gte=mes_pasado, estado='entregado').aggregate(Sum('total'))['total__sum'] or 0
    
    # Productos más vendidos
    productos_populares = ItemPedido.objects.values(
        'producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'pedidos_hoy': pedidos_hoy,
        'pedidos_semana': pedidos_semana,
        'pedidos_mes': pedidos_mes,
        'ventas_hoy': ventas_hoy,
        'ventas_semana': ventas_semana,
        'ventas_mes': ventas_mes,
        'productos_populares': productos_populares,
    }
    return render(request, 'core/generar_reporte.html', context)

@login_required
@user_passes_test(es_admin)
def gestionar_personal(request):
    """Vista para que el admin gestione el personal"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefono = request.POST.get('telefono')
        
        try:
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                email=email,
                rol='personal',
                first_name=first_name,
                last_name=last_name,
                telefono=telefono
            )
            messages.success(request, f'Personal {username} creado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al crear personal: {str(e)}')
    
    personal = Usuario.objects.filter(rol='personal')
    context = {
        'personal': personal,
    }
    return render(request, 'core/gestionar_personal.html', context)


@login_required
@user_passes_test(es_admin)
def gestionar_reservas(request):
    """Vista para que el admin gestione las reservas"""
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    
    # Filtros
    estado_filter = request.GET.get('estado', '')
    fecha_filter = request.GET.get('fecha', '')
    
    if estado_filter:
        reservas = reservas.filter(estado=estado_filter)
    
    if fecha_filter:
        reservas = reservas.filter(fecha_reserva__date=fecha_filter)
    
    # Estadísticas
    total_reservas = reservas.count()
    reservas_pendientes = reservas.filter(estado='pendiente').count()
    reservas_confirmadas = reservas.filter(estado='confirmada').count()
    reservas_hoy = Reserva.objects.filter(fecha_reserva__date=datetime.now().date()).count()
    
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        nuevo_estado = request.POST.get('estado')
        mesa_asignada = request.POST.get('mesa', '')
        
        try:
            reserva = Reserva.objects.get(id=reserva_id)
            reserva.estado = nuevo_estado
            if mesa_asignada:
                reserva.mesa = mesa_asignada
            reserva.save()
            
            messages.success(request, f'Reserva #{reserva_id} actualizada a {nuevo_estado}')
            return redirect('gestionar_reservas')
        except Reserva.DoesNotExist:
            messages.error(request, 'Reserva no encontrada')
    
    context = {
        'reservas': reservas,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_hoy': reservas_hoy,
        'estado_filter': estado_filter,
        'fecha_filter': fecha_filter,
    }
    return render(request, 'core/gestionar_reservas.html', context)

@login_required
@user_passes_test(es_personal)
def personal_dashboard(request):
    # Estadísticas para el personal
    pedidos_pendientes = Pedido.objects.exclude(estado__in=['entregado', 'cancelado']).count()
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=datetime.now().date()).count()
    
    # Pedidos asignados al personal (excluir entregados y cancelados)
    pedidos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado']).order_by('fecha_pedido')
    
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.estado = nuevo_estado
        pedido.save()
        messages.success(request, f'Pedido #{pedido_id} actualizado a {nuevo_estado}')
        return redirect('personal_dashboard')
    
    context = {
        'pedidos': pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_hoy': pedidos_hoy,
    }
    return render(request, 'core/personal_dashboard.html', context)

@login_required
@user_passes_test(es_personal)
def editar_perfil_personal(request):
    """Vista para que el personal edite su perfil"""
    if request.method == 'POST':
        # Actualizar campos básicos
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telefono = request.POST.get('telefono', '')
        user.save()
        
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('personal_dashboard')
    
    return render(request, 'core/editar_perfil_personal.html')

@login_required
@user_passes_test(es_cliente)
def cliente_dashboard(request):
    # Información del cliente
    pedidos_cliente = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')[:5]
    reservas_cliente = Reserva.objects.filter(cliente=request.user).order_by('-fecha_creacion')[:5]
    pedidos_pendientes = Pedido.objects.filter(cliente=request.user).exclude(estado__in=['entregado', 'cancelado']).count()
    comentarios_count = Comentario.objects.filter(cliente=request.user).count()
    
    context = {
        'pedidos': pedidos_cliente,
        'reservas': reservas_cliente,
        'pedidos_pendientes': pedidos_pendientes,
        'comentarios_count': comentarios_count,
    }
    
    return render(request, 'core/cliente_dashboard.html', context)

def menu(request):
    categorias = Categoria.objects.all()
    productos_por_categoria = {}
    
    for categoria in categorias:
        productos = Menu.objects.filter(categoria=categoria, disponible=True)
        if productos.exists():
            productos_por_categoria[categoria] = productos
    
    context = {
        'productos_por_categoria': productos_por_categoria,
    }
    return render(request, 'core/menu.html', context)

@login_required
@user_passes_test(es_cliente)
def hacer_pedido(request):
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        if pedido_form.is_valid():
            # Crear el pedido
            pedido = pedido_form.save(commit=False)
            pedido.cliente = request.user
            pedido.total = 0  # Se calculará con los items
            pedido.save()
            
            # Procesar el carrito
            carrito_data = request.POST.get('carrito_data')
            items_procesados = 0
            
            if carrito_data:
                try:
                    import json
                    items = json.loads(carrito_data)
                    for item in items:
                        producto = Menu.objects.get(id=item['id'])
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=item['cantidad'],
                            subtotal=item['subtotal']
                        )
                        items_procesados += 1
                except Exception as e:
                    # En caso de error, eliminar el pedido creado
                    pedido.delete()
                    messages.error(request, f'Error al procesar el pedido: {str(e)}')
                    return redirect('hacer_pedido')
            
            if items_procesados > 0:
                messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente! Total: ${pedido.total}. Pronto nos contactaremos contigo.')
            else:
                messages.warning(request, f'Pedido #{pedido.id} creado pero sin productos. Por favor contacta al restaurante.')
            
            return redirect('cliente_dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        pedido_form = PedidoForm()
    
    # Obtener productos del menú organizados por categoría
    categorias = Categoria.objects.all()
    productos_por_categoria = {}
    
    for categoria in categorias:
        productos = Menu.objects.filter(categoria=categoria, disponible=True)
        if productos.exists():
            productos_por_categoria[categoria] = productos
    
    context = {
        'pedido_form': pedido_form,
        'productos_por_categoria': productos_por_categoria,
    }
    return render(request, 'core/hacer_pedido.html', context)

@login_required
@user_passes_test(es_cliente)
def reservar_mesa(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = request.user
            reserva.save()
            messages.success(request, 'Reserva creada exitosamente. Te esperamos!')
            return redirect('cliente_dashboard')
    else:
        form = ReservaForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/reservar_mesa.html', context)

@login_required
@user_passes_test(es_cliente)
def ver_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'core/ver_pedidos.html', context)

@login_required
@user_passes_test(es_cliente)
def ver_reservas(request):
    reservas = Reserva.objects.filter(cliente=request.user).order_by('-fecha_creacion')
    context = {
        'reservas': reservas,
    }
    return render(request, 'core/ver_reservas.html', context)

@login_required
@user_passes_test(es_cliente)
def hacer_comentario(request):
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.cliente = request.user
            comentario.save()
            messages.success(request, '¡Gracias por tu comentario!')
            return redirect('cliente_dashboard')
    else:
        form = ComentarioForm()
    
    context = {
        'form': form,
    }
    return render(request, 'core/hacer_comentario.html', context)

@login_required
@user_passes_test(es_admin)
def ver_comentarios(request):
    comentarios = Comentario.objects.all().order_by('-fecha')
    context = {
        'comentarios': comentarios,
    }
    return render(request, 'core/ver_comentarios.html', context)

@login_required
@user_passes_test(es_admin)
def generar_reporte(request):
    if request.method == 'POST':
        # Lógica para generar reportes
        pass
    
    # Estadísticas para mostrar
    hoy = datetime.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)
    
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    pedidos_semana = Pedido.objects.filter(fecha_pedido__date__gte=semana_pasada).count()
    pedidos_mes = Pedido.objects.filter(fecha_pedido__date__gte=mes_pasado).count()
    
    context = {
        'pedidos_hoy': pedidos_hoy,
        'pedidos_semana': pedidos_semana,
        'pedidos_mes': pedidos_mes,
    }
    return render(request, 'core/generar_reporte.html', context)

def custom_logout(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')

# =============================================
# VISTAS DEL ADMINISTRADOR
# =============================================

@login_required
@user_passes_test(es_admin)
def gestionar_personal(request):
    """Vista para que el admin gestione el personal"""
    personal = Usuario.objects.filter(rol='personal')
    
    context = {
        'personal': personal,
    }
    return render(request, 'core/gestionar_personal.html', context)

@login_required
@user_passes_test(es_admin)
def ver_comentarios(request):
    """Vista para que el admin vea los comentarios"""
    comentarios = Comentario.objects.all().order_by('-fecha')
    
    context = {
        'comentarios': comentarios,
    }
    return render(request, 'core/ver_comentarios.html', context)

@login_required
@user_passes_test(es_admin)
def generar_reporte(request):
    """Vista para que el admin genere reportes"""
    # Estadísticas básicas
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    pedidos_semana = Pedido.objects.filter(fecha_pedido__date__gte=hoy - timedelta(days=7)).count()
    pedidos_mes = Pedido.objects.filter(fecha_pedido__date__gte=hoy - timedelta(days=30)).count()

    context = {
        'pedidos_hoy': pedidos_hoy,
        'pedidos_semana': pedidos_semana,
        'pedidos_mes': pedidos_mes,
    }
    return render(request, 'core/generar_reporte.html', context)

@login_required
def editar_perfil_cliente(request):
    """Vista para que el cliente edite su perfil"""
    if request.method == 'POST':
        # Actualizar campos del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.telefono = request.POST.get('telefono', '')
        user.direccion = request.POST.get('direccion', '')
        user.save()
        
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('cliente_dashboard')
    
    return render(request, 'core/editar_perfil_cliente.html')