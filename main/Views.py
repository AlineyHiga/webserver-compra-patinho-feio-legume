from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Pedido, ItemPedido
from django.contrib.auth import get_user_model
from paypalrestsdk import Payment
import logging
from django.db import transaction

Cliente = get_user_model()


class AcompanharPedidoAPIView(APIView):
    def get(self, request, pedido_id):
        try:
            # Busca o pedido pelo ID e valida o cliente
            pedido = Pedido.objects.get(id=pedido_id, cliente=request.user)
            
            # Recupera os itens do pedido
            itens = ItemPedido.objects.filter(pedido=pedido)
            produtos = [
                {
                    "nome": item.produto.nome,
                    "quantidade": item.quantidade,
                    "preco": item.preco,
                }
                for item in itens
            ]
            
            # Retorna os detalhes do pedido junto com o status
            return Response(
                {
                    "pedido_id": pedido.id,
                    "cliente": pedido.cliente.username,
                    "status": pedido.status,
                    "total": pedido.total,
                    "produtos": produtos,
                },
                status=status.HTTP_200_OK,
            )
        except Pedido.DoesNotExist:
            return Response(
                {"error": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

class EfetuarCompraAPIView(APIView):
    def post(self, request):
        produtos = request.data.get('produtos', [])
        cliente_id = request.data.get('cliente', {}).get('id')

        if not produtos:
            return Response({"error": "Nenhum produto fornecido."}, status=400)
        if not cliente_id:
            return Response({"error": "ID do cliente não fornecido."}, status=400)

        try:
            # Begin a database transaction
            with transaction.atomic():
                # Criar o pedido no banco de dados
                pedido = Pedido.objects.create(cliente_id=cliente_id)

                total = 0  # Para somar o total do pedido
                itens_paypal = []  # Para a integração PayPal

                for item in produtos:
                    produto_id = item.get('produto_id')
                    quantidade = item.get('quantidade')
                    valor = item.get('valor')
                    agricultor_id = item.get('id_agricultor')
                    nome = item.get('nome')

                    if not produto_id or not quantidade or not valor or not agricultor_id:
                        return Response({"error": f"Dados do item incompletos: {item}."}, status=400)

                    preco_total = valor * quantidade
                    total += preco_total

                    # Adicionar item ao banco de dados
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        valor=valor,
                        agricultor_id=agricultor_id
                    )

                    # Preparar item para o PayPal
                    itens_paypal.append({
                        "name": nome,
                        "sku": str(produto_id),
                        "price": f"{valor:.2f}",
                        "currency": "USD",
                        "quantity": quantidade
                    })

                # Atualiza o total do pedido
                pedido.total = total
                pedido.save()

                # Criar pagamento no PayPal
                pagamento = Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri('/paypal/execute/'),
                        "cancel_url": request.build_absolute_uri('/paypal/cancelled/')
                    },
                    "transactions": [{
                        "item_list": {
                            "items": itens_paypal
                        },
                        "amount": {
                            "total": f"{total:.2f}",
                            "currency": "USD"
                        },
                        "description": f"Compra no sistema, Pedido ID: {pedido.id}"
                    }]
                })

                if pagamento.create():
                    # Salvar o ID do pagamento no pedido
                    pedido.pagamento_id = pagamento.id
                    pedido.status = 'Pago'
                    pedido.save()

                    # Redirecionar o cliente para aprovação no PayPal
                    for link in pagamento.links:
                        if link.rel == "approval_url":
                            return Response({"approval_url": link.href}, status=status.HTTP_200_OK)
                else:
                    logging.error(f"Erro ao criar pagamento no PayPal: {pagamento.error}")
                    raise ValueError("Falha ao criar pagamento no PayPal.")

        except ValueError as e:
            logging.error(f"Erro de valor: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logging.error(f"Exceção ao processar pagamento: {str(e)}")
            return Response({"error": "Erro no processamento do pagamento."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)