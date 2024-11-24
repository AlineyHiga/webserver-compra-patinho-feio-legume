import requests


def get_produto(produto_id):
    """
    Fetch product details by ID from the API.
    """
    # Updated URL based on the working curl command
    url_pagamento = f'http://webserver-produto-patinho-feio-do-legume.vercel.app/produtos/disponiveis/{produto_id}/'
    
    try:
        # Send the GET request
        response = requests.get(url_pagamento)
        
        print(f"Response Status Code: {response.status_code}")  # Debugging status code
        
        # Check for successful response
        if response.status_code == 200:
            json_response = response.json()
            return json_response  # Return the full response for flexibility
        
        elif response.status_code == 404:
            print(f"Produto with ID {produto_id} not found at {url_pagamento}.")
        
        else:
            print(f"Unhandled HTTP error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Error fetching product details: {e}")
    
    # Return None explicitly if the call fails
    return None


def patch_quantidade_produto(item, comprar):
    """
    Update the quantity of a product based on the transaction type (purchase/return).
    """
    agricultor =item.get('id_agricultor')
    produto= item.get('produto_id')
    quantidade = float(item.get('quantidade'))
    url_pagamento = f'http://webserver-produto-patinho-feio-do-legume.vercel.app/produtos/atualizar/{agricultor}/{produto}/'
    
    # Fetch the product data
    produto = get_produto(produto)
    
    if produto is None:
        print(f"Invalid product data for produto_id={produto}. Operation aborted.")
        return False
    produto_quantidade= float(produto.get('quantidade'))
    # Calculate new quantity
    quantidade = produto_quantidade - quantidade if comprar else produto_quantidade + quantidade
    
    data = {
        'quantidade': quantidade
    }
    
    try:
        response = requests.patch(url_pagamento, json=data)
        if response.status_code == 200 :
            return True
    except requests.RequestException as e:
        print(f"Error updating product quantity: {e}")
    
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

