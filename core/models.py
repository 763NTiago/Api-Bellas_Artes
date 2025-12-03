# Api-Bellas_Artes/core/models.py
from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    def __str__(self): return self.nome

class Material(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.TextField(blank=True, null=True)

class Arquiteto(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    data_pagamento = models.DateField(null=True, blank=True)

class Agenda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_previsao_termino = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True, null=True)

class Orcamento(models.Model):
    data_criacao = models.CharField(max_length=50, blank=True) # Mantido char para compatibilidade
    cliente_nome = models.CharField(max_length=255)
    cliente_endereco = models.TextField(blank=True)
    cliente_cpf = models.CharField(max_length=50, blank=True)
    cliente_email = models.CharField(max_length=255, blank=True)
    cliente_telefone = models.CharField(max_length=50, blank=True)
    itens_json = models.TextField(default="[]") # JSON guardado como texto
    valor_total_final = models.CharField(max_length=50, blank=True)
    observacoes = models.TextField(blank=True)
    condicoes_pagamento = models.TextField(blank=True)
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True)

class Recebimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    agenda = models.ForeignKey(Agenda, on_delete=models.SET_NULL, null=True)
    tipo_pagamento = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    num_parcelas = models.IntegerField(default=0)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_1_venc = models.CharField(max_length=50, blank=True)

class Parcela(models.Model):
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE)
    num_parcela = models.IntegerField()
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_vencimento = models.DateField(null=True, blank=True)
    data_recebimento = models.DateField(null=True, blank=True)
    valor_recebido = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

class Comissao(models.Model):
    data = models.DateField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    recebimento = models.ForeignKey(Recebimento, on_delete=models.SET_NULL, null=True)
    beneficiario = models.CharField(max_length=255, blank=True)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    porcentagem = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)