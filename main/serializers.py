from rest_framework import serializers
from .models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
    foto = serializers.CharField()  # Directly use as CharField since it's already a URL

    class Meta:
        model = Produto
        fields = ['id_produto', 'nome', 'descricao', 'foto', 'quantidade', 'id_agricultor', 'classificacao', 'tipo_produto', 'tipo_medida', 'valor']
