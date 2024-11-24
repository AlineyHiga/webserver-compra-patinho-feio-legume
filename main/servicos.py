import requests
import paypalrestsdk


def Get_pedido(pedido):
    url_pagamento = 'https://webserver-cliente-patinho-feio.vercel.app/'
    data = {
        'pedido_id': pedido.id,
        'valor': float(pedido.total),
        'cliente_id': pedido.cliente.id,
        'cliente_celular': pedido.cliente.celular
    }
    response = requests.get(url_pagamento, json=data)
    if response.status_code == 200 and response.json().get('status') == 'sucesso':
        pedido.status = 'Pago'
        pedido.save()
        return True
    return False

def notificar_transportadora(pedido):
    url_transportadora = 'https://api.transportadora.com/notificar'
    data = {
        'pedido_id': pedido.id,
        'endereco': pedido.cliente.endereco,
        'cliente_celular': pedido.cliente.celular,
        'valor': float(pedido.total),
    }
    response = requests.post(url_transportadora, json=data)
    if response.status_code == 200 and response.json().get('status') == 'notificado':
        pedido.status = 'Enviado'
        pedido.save()
        return True
    return False

