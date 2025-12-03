from rest_framework import serializers
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class ArquitetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arquiteto
        fields = '__all__'

class AgendaSerializer(serializers.ModelSerializer):
    # Trazemos o nome do cliente para facilitar a leitura no frontend
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    
    class Meta:
        model = Agenda
        fields = '__all__'

class OrcamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orcamento
        fields = '__all__'

class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
        fields = '__all__'

class RecebimentoSerializer(serializers.ModelSerializer):
    parcelas = ParcelaSerializer(many=True, read_only=True, source='parcela_set')
    
    class Meta:
        model = Recebimento
        fields = '__all__'

class ComissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comissao
        fields = '__all__'