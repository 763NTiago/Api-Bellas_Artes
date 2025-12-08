from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

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
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Agenda
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Cliente N/A"

    def get_nome(self, obj):
        return self.get_cliente_nome(obj)

class OrcamentoSerializer(serializers.ModelSerializer):
    projeto_nome = serializers.SerializerMethodField()

    class Meta:
        model = Orcamento
        fields = '__all__'

    def get_projeto_nome(self, obj):
        return obj.agenda.descricao if obj.agenda else "Sem Projeto"

class RecebimentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    projeto_nome = serializers.SerializerMethodField()
    projeto = serializers.SerializerMethodField()

    class Meta:
        model = Recebimento
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "Cliente N/A"
    
    def get_nome(self, obj):
        return self.get_cliente_nome(obj)
    
    def get_projeto_nome(self, obj):
        return obj.agenda.descricao if obj.agenda else "Geral"

    def get_projeto(self, obj):
        return self.get_projeto_nome(obj)

class ParcelaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField() 
    projeto_nome = serializers.SerializerMethodField()
    projeto = serializers.SerializerMethodField()
    nome_parcela = serializers.SerializerMethodField()

    class Meta:
        model = Parcela
        fields = '__all__'

    def get_cliente_nome(self, obj):
        try: return obj.recebimento.cliente.nome
        except: return "Cliente N/A"

    def get_nome(self, obj): 
        return self.get_cliente_nome(obj)

    def get_projeto_nome(self, obj):
        try: return obj.recebimento.agenda.descricao
        except: return "Geral"

    def get_projeto(self, obj):
        return self.get_projeto_nome(obj)

    def get_nome_parcela(self, obj):
        if obj.num_parcela == 0: return "Entrada"
        return f"Parcela {obj.num_parcela}"

class ComissaoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()
    projeto_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = Comissao
        fields = '__all__'

    def get_cliente_nome(self, obj):
        return obj.cliente.nome if obj.cliente else "N/A"

    def get_nome(self, obj):
        return self.get_cliente_nome(obj)

    def get_projeto_nome(self, obj):
        try: return obj.recebimento.agenda.descricao
        except: return "Sem Projeto"