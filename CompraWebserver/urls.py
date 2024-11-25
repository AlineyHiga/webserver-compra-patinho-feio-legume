# main/urls.py
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from main.Views import AcompanharPedidoAPIView, EfetuarCompraAPIView, AcompanharPedidosClienteAPIView,AcompanharPedidosAgricultorAPIView, ExecutarPaymentAPIView

urlpatterns = [
    path('comprar/', EfetuarCompraAPIView.as_view(), name='efetuar_compra'),  # URL para efetuar a compra
    path('pedido/<int:pedido_id>/', AcompanharPedidoAPIView.as_view(), name='acompanhar_pedido'),  # URL para acompanhar o pedido
    path('pedido/cliente/<int:cliente_id>/',AcompanharPedidosClienteAPIView.as_view(), name='pedidos_cliente'),
    path('pedido/agricultor/<int:agricultor_id>/',AcompanharPedidosAgricultorAPIView.as_view(), name='pedidos_agricultor'),
    path('comprar/executar/',ExecutarPaymentAPIView.as_view(),name='executar_pagamento')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)