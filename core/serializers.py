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
    # Compatibilidade: Envia 'cliente_nome' E 'nome' (como o SQL antigo fazia)
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
    
    def get_nome(self, obj): # O SQLite retornava 'c.nome'
        return self.get_cliente_nome(obj)
    
    def get_projeto_nome(self, obj):
        return obj.agenda.descricao if obj.agenda else "Geral"

    def get_projeto(self, obj): # Alias para compatibilidade
        return self.get_projeto_nome(obj)

class ParcelaSerializer(serializers.ModelSerializer):
    # AQUI ESTAVA O ERRO: O Desktop busca 'nome' e 'projeto'
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
        # Esta é a "Cola" que conserta o erro KeyError: 'nome'
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