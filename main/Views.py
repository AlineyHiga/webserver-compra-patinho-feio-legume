from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main.servicos import patch_quantidade_produto
from .models import Pedido, ItemPedido
from django.contrib.auth import get_user_model
from paypalrestsdk import Payment
import logging
from django.db import transaction

Cliente = get_user_model()

class AcompanharPedidosAgricultorAPIView(APIView):
    def get(self, request, agricultor_id):
        try:

            # Recupera os itens do pedido
            itens = ItemPedido.objects.filter(agricultor_id= agricultor_id)
            response_data = []
            for item in itens:
                response_data.append({
                    "nome": item.nome,
                    "produto_id": item.produto_id,
                    "quantidade": item.quantidade,
                    "valor": item.valor,
                    "id_agricultor": item.agricultor_id
                }) 
                    
                
            
            # Retorna os detalhes do pedido junto com o status
            return Response( response_data, status=status.HTTP_200_OK)
        except Pedido.DoesNotExist:
            return Response(
                {"error": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

class AcompanharPedidosClienteAPIView(APIView):
    def get(self, request, cliente_id):
        try:
            # Fetch all Pedidos
            pedidos = Pedido.objects.filter(cliente_id=cliente_id)
            
            # Build response data
            response_data = []
            for pedido in pedidos:
                # Fetch associated ItemPedido objects
                itens = ItemPedido.objects.filter(pedido=pedido.id)
                
                # Build the list of products
                produtos = [
                    {
                        "nome": item.nome,
                        "produto_id": item.produto_id,
                        "quantidade": item.quantidade,
                        "valor": item.valor,
                        "id_agricultor": item.agricultor_id
                    }
                    for item in itens
                ]
                
                # Calculate the total value of the pedido
                valor_total = sum(item.valor * item.quantidade for item in itens)
                
                # Append pedido data to response
                response_data.append({
                    "pedido_id":pedido.id,
                    "produtos": produtos,
                    "valor_total": valor_total,
                    "status": pedido.status
                })
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcompanharPedidoAPIView(APIView):
    def get(self, request, pedido_id):
        try:
            # Busca o pedido pelo ID e valida o cliente
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Recupera os itens do pedido
            itens = ItemPedido.objects.filter(pedido=pedido.id)
            produtos = [
                {
                    "nome": item.nome,
                    "produto_id": item.produto_id,
                    "quantidade": item.quantidade,
                    "valor": item.valor,
                    "id_agricultor": item.agricultor_id
                }
                for item in itens
            ]
            
            # Retorna os detalhes do pedido junto com o status
            return Response(
                {
                    "pedido_id": pedido.id,
                    "cliente_id": pedido.cliente_id,
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
                # Create the order (Pedido)
                pedido = Pedido.objects.create(cliente_id=cliente_id)

                total = 0  # For summing up the total order amount
                itens_paypal = []  # For PayPal integration
                updated_items = []  # Keep track of updated inventory for rollback

                for item in produtos:
                    produto_id = item.get('produto_id')
                    quantidade = item.get('quantidade')
                    valor = item.get('valor')
                    agricultor_id = item.get('id_agricultor')
                    nome = item.get('nome')

                    if not produto_id or not quantidade or not valor or not agricultor_id:
                        raise ValueError(f"Dados do item incompletos: {item}.")

                    preco_total = valor * quantidade
                    total += preco_total

                    # Create the order item (ItemPedido)
                    item_pedido = ItemPedido.objects.create(
                        pedido=pedido,
                        produto_id=produto_id,
                        quantidade=quantidade,
                        valor=valor,
                        agricultor_id=agricultor_id
                    )

                    # Add to PayPal item list
                    itens_paypal.append({
                        "name": nome,
                        "sku": str(produto_id),
                        "price": f"{valor:.2f}",
                        "currency": "USD",
                        "quantity": quantidade
                    })

                    # Deduct from inventory
                    if patch_quantidade_produto(item, True):
                        updated_items.append(item)  # Track successfully updated items
                    else:
                        raise ValueError(f"Falha ao atualizar o inventário para o produto {produto_id}.")

                # Update the order total
                pedido.total = total
                pedido.save()

                # Create payment in PayPal
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
                    # Save the payment ID in the order
                    pedido.pagamento_id = pagamento.id
                    pedido.status = 'Pago'
                    pedido.save()

                    # Redirect customer to PayPal approval
                    for link in pagamento.links:
                        if link.rel == "approval_url":
                            return Response({"approval_url": link.href}, status=status.HTTP_200_OK)
                else:
                    logging.error(f"Erro ao criar pagamento no PayPal: {pagamento.error}")
                    raise ValueError("Falha ao criar pagamento no PayPal.")

        except ValueError as e:
            logging.error(f"Erro de valor: {str(e)}")
            self.rollback_inventory(updated_items)  # Rollback inventory
            self.delete_order_and_items(pedido)  # Delete the order and associated items
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logging.error(f"Exceção ao processar pagamento: {str(e)}")
            self.rollback_inventory(updated_items)  # Rollback inventory
            self.delete_order_and_items(pedido)  # Delete the order and associated items
            return Response({"error": "Erro no processamento do pagamento."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def rollback_inventory(updated_items):
        """
        Rollback the inventory for all items updated so far.
        """
        for item in updated_items:
            try:
                patch_quantidade_produto(item, False)  # Add back the quantity
            except Exception as e:
                logging.error(f"Falha ao reverter o inventário para o item {item.get('produto_id')}: {str(e)}")

    @staticmethod
    def delete_order_and_items(pedido):
        """
        Delete the order and its associated items from the database.
        """
        try:
            if pedido:
                ItemPedido.objects.filter(pedido=pedido).delete()  # Delete all items
                pedido.delete()  # Delete the order itself
                logging.info(f"Pedido ID {pedido.id} e seus itens foram excluídos.")
        except Exception as e:
            logging.error(f"Falha ao excluir o pedido ID {pedido.id}: {str(e)}")
