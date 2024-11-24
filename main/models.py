from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
# Modelo de Cliente referenciado via get_user_model
Cliente = get_user_model()

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Pago', 'Pago'),
        ('Enviado', 'Enviado'),
        ('Entregue', 'Entregue'),
    ]

    # ForeignKey matches the `cliente_id` field in the database
    cliente_id = models.CharField(max_length=255)

    # Maps directly to `data_criacao`
    data_criacao = models.DateTimeField(auto_now_add=True)

    # Maps to `status` with predefined choices
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendente')

    # Maps to `total`
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Maps to `pagamento_id`
    pagamento_id = models.CharField(max_length=255)  # Ensure payment IDs are managed securely

    def __str__(self):
        return f"Pedido {self.id} - Cliente {self.cliente.username}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto_id = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)  # Valor unitário
    agricultor_id = models.IntegerField()  # ID do agricultor associado ao produto

    def __str__(self):
        return f"Item {self.produto_id} do Pedido {self.pedido.id}"