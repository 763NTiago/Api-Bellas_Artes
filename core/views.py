from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models  # <--- FALTAVA ISTO
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from datetime import date, timedelta
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao
from .serializers import *

# --- ViewSets Principais (CRUD) ---

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        nome = request.data.get('nome')
        if not nome:
            return Response({'error': 'Nome obrigatório'}, status=400)
        cliente, created = Cliente.objects.get_or_create(nome=nome)
        return Response({'id': cliente.id, 'nome': cliente.nome, 'created': created})

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class ArquitetoViewSet(viewsets.ModelViewSet):
    queryset = Arquiteto.objects.all()
    serializer_class = ArquitetoSerializer

class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all().order_by('-data_previsao_termino')
    serializer_class = AgendaSerializer

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.all().order_by('-id')
    serializer_class = OrcamentoSerializer

class RecebimentoViewSet(viewsets.ModelViewSet):
    queryset = Recebimento.objects.all()
    serializer_class = RecebimentoSerializer

class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.all()
    serializer_class = ParcelaSerializer

class ComissaoViewSet(viewsets.ModelViewSet):
    queryset = Comissao.objects.all()
    serializer_class = ComissaoSerializer

# --- Views Personalizadas (Dashboards) ---

class DashboardFinanceiroView(views.APIView):
    def get(self, request):
        # Define o campo de valor restante (Parcela - Pago)
        # Usamos Coalesce para garantir que nulos virem 0
        valor_restante = F('valor_parcela') - Coalesce(F('valor_recebido'), 0)
        
        # 1. Total Geral a Receber
        total_geral = Parcela.objects.annotate(restante=valor_restante).filter(
            restante__gt=0.01 # Filtra apenas o que falta pagar
        ).aggregate(Sum('restante'))

        # 2. Total a Receber (Próximos 30 dias)
        data_limite = date.today() + timedelta(days=30)
        total_30d = Parcela.objects.annotate(restante=valor_restante).filter(
            restante__gt=0.01,
            data_vencimento__range=[date.today(), data_limite]
        ).aggregate(Sum('restante'))

        return Response({
            'total_a_receber': total_geral['restante__sum'] or 0.0,
            'total_a_receber_30d': total_30d['restante__sum'] or 0.0
        })

class DashboardProjetosView(views.APIView):
    def get(self, request):
        ativos = Agenda.objects.filter(data_previsao_termino__gte=date.today()).count()
        return Response({'ativos': ativos})

class RelatorioCompletoView(views.APIView):
    def get(self, request):
        agendas = Agenda.objects.all().select_related('cliente').order_by('-data_previsao_termino')[:100]
        dados = []
        for a in agendas:
            # Tenta pegar info básica para preencher a lista
            dados.append({
                "projeto": a.descricao,
                "cliente": a.cliente.nome if a.cliente else "N/A",
                "data": a.data_previsao_termino,
                "data_inicio": a.data_inicio,
            })
        return Response(dados)