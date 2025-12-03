from django.db import models

class ClienteApp(models.Model):
    # Espelho da tabela 'clientes_app' do Desktop
    nome = models.CharField(max_length=255, unique=True)
    def __str__(self): return self.nome

class Agenda(models.Model):
    # Espelho da tabela 'agenda'
    cliente = models.ForeignKey(ClienteApp, on_delete=models.SET_NULL, null=True, related_name='agendas')
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_previsao_termino = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.descricao} - {self.cliente}"

class Orcamento(models.Model):
    # Espelho da tabela 'orcamentos'
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    data_criacao = models.CharField(max_length=50) 
    cliente_nome = models.CharField(max_length=255)
    cliente_endereco = models.CharField(max_length=255, blank=True, null=True)
    cliente_cpf = models.CharField(max_length=50, blank=True, null=True)
    cliente_email = models.CharField(max_length=255, blank=True, null=True)
    cliente_telefone = models.CharField(max_length=50, blank=True, null=True)
    itens_json = models.TextField() 
    valor_total_final = models.CharField(max_length=50)
    observacoes = models.TextField(blank=True, null=True)
    condicoes_pagamento = models.TextField(blank=True, null=True)
    def __str__(self): return f"Orçamento {self.id} - {self.cliente_nome}"

class Material(models.Model):
    # Espelho da tabela 'materiais'
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.TextField(blank=True, null=True)
    def __str__(self): return self.nome

class Recebimento(models.Model):
    # Espelho da tabela 'recebimentos_pagamentos'
    cliente = models.ForeignKey(ClienteApp, on_delete=models.SET_NULL, null=True)
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True)
    tipo_pagamento = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    num_parcelas = models.IntegerField(default=0)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_1_venc = models.DateField(null=True, blank=True)

class Parcela(models.Model):
    # Espelho da tabela 'parcelas'
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE, related_name='parcelas')
    num_parcela = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField(null=True, blank=True)
    data_recebimento = models.DateField(null=True, blank=True)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Comissao(models.Model):
    # Espelho da tabela 'comissoes'
    data = models.DateField()
    cliente = models.ForeignKey(ClienteApp, on_delete=models.SET_NULL, null=True)
    recebimento = models.ForeignKey(Recebimento, on_delete=models.SET_NULL, null=True)
    beneficiario = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    porcentagem = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Arquiteto(models.Model):
    # Espelho da tabela 'arquitetos'
    nome = models.CharField(max_length=255, unique=True)
    data_pagamento = models.DateField(null=True, blank=True)