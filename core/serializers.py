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
    # Mudança: SerializerMethodField garante que o campo existe sempre
    cliente_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Agenda
        fields = '__all__'

    def get_cliente_nome(self, obj):
        # Se tiver cliente, retorna o nome. Se não, retorna "Cliente N/A"
        return obj.cliente.nome if obj.cliente else "Cliente N/A"

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
    # Mudança: Também protegemos aqui
    cliente_nome = serializers.SerializerMethodField()
    projeto_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Comissao
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "N/A"

    def get_projeto_nome(self, obj):
        # Navegação segura: Comissao -> Recebimento -> Agenda -> Descricao
        try:
            return obj.recebimento.agenda.descricao
        except:
            return "Sem Projeto"