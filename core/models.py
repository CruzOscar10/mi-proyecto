from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
    ROLES = (
        ('cliente', 'Cliente'),
        ('personal', 'Personal'),
        ('admin', 'Administrador'),
    )
    
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.rol})"

class Restaurante(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    area_entrega = models.TextField(help_text="Zonas de entrega disponibles")
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=[('comida', 'Comida'), ('bebida', 'Bebida')])
    
    def __str__(self):
        return self.nombre

class Menu(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='menu/', blank=True, null=True)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'cliente'})
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    direccion_entrega = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)
        
        # Actualizar total del pedido
        total = sum(item.subtotal for item in self.pedido.items.all())
        self.pedido.total = total
        self.pedido.save()

class Reserva(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    )
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'cliente'})
    fecha_reserva = models.DateTimeField()
    numero_personas = models.PositiveIntegerField()
    mesa = models.CharField(max_length=10, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente.username}"

class Comentario(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'cliente'})
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, blank=True, null=True)
    texto = models.TextField()
    calificacion = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    fecha = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Comentario de {self.cliente.username} - {self.calificacion}★"

class Reporte(models.Model):
    TIPOS = (
        ('diario', 'Reporte Diario'),
        ('semanal', 'Reporte Semanal'),
        ('mensual', 'Reporte Mensual'),
    )
    
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    total_pedidos = models.PositiveIntegerField(default=0)
    total_ventas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pedidos_entregados = models.PositiveIntegerField(default=0)
    reservas_completadas = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fecha_inicio} a {self.fecha_fin}"