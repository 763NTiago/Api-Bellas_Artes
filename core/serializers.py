from rest_framework import serializers
from .models import *

class ClienteAppSerializer(serializers.ModelSerializer):
    class Meta: model = ClienteApp; fields = '__all__'

class AgendaSerializer(serializers.ModelSerializer):
    class Meta: model = Agenda; fields = '__all__'

class OrcamentoSerializer(serializers.ModelSerializer):
    class Meta: model = Orcamento; fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta: model = Material; fields = '__all__'

class ParcelaSerializer(serializers.ModelSerializer):
    class Meta: model = Parcela; fields = '__all__'

class RecebimentoSerializer(serializers.ModelSerializer):
    parcelas = ParcelaSerializer(many=True, read_only=True)
    class Meta: model = Recebimento; fields = '__all__'

class ComissaoSerializer(serializers.ModelSerializer):
    class Meta: model = Comissao; fields = '__all__'

class ArquitetoSerializer(serializers.ModelSerializer):
    class Meta: model = Arquiteto; fields = '__all__'