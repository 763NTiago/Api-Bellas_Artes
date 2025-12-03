from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.db.models import Sum, F, Q
from django.db.models.functions import Coalesce
from datetime import date, timedelta
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao
from .serializers import *

# --- ViewSets CRUD (Padrão) ---
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        nome = request.data.get('nome')
        if not nome: return Response({'error': 'Nome obrigatório'}, status=400)
        cliente, created = Cliente.objects.get_or_create(nome=nome)
        return Response({'id': cliente.id, 'nome': cliente.nome})

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
    queryset = Comissao.objects.all().order_by('-data')
    serializer_class = ComissaoSerializer

# --- Dashboards e Relatórios ---

class DashboardFinanceiroView(views.APIView):
    def get(self, request):
        # Valor Restante = Valor da Parcela - O que já foi pago (tratando nulos como 0)
        valor_restante = F('valor_parcela') - Coalesce(F('valor_recebido'), 0)
        
        # 1. Total Geral a Receber
        total_geral = Parcela.objects.annotate(restante=valor_restante).filter(
            restante__gt=0.01
        ).aggregate(Sum('restante'))

        # 2. Total a Receber (Próximos 30 dias)
        limite = date.today() + timedelta(days=30)
        total_30d = Parcela.objects.annotate(restante=valor_restante).filter(
            restante__gt=0.01,
            data_vencimento__range=[date.today(), limite]
        ).aggregate(Sum('restante'))

        # 3. Total Já Recebido (Global)
        total_recebido = Parcela.objects.aggregate(Sum('valor_recebido'))

        return Response({
            'total_a_receber': total_geral['restante__sum'] or 0.0,
            'total_a_receber_30d': total_30d['restante__sum'] or 0.0,
            'total_recebido_geral': total_recebido['valor_recebido__sum'] or 0.0
        })

class DashboardEventosView(views.APIView):
    def get(self, request):
        # Lógica para encontrar o "Próximo Evento Unificado"
        hoje = date.today()
        proximo_inicio = Agenda.objects.filter(data_inicio__gte=hoje).order_by('data_inicio').first()
        proximo_fim = Agenda.objects.filter(data_previsao_termino__gte=hoje).order_by('data_previsao_termino').first()
        
        candidatos = []
        if proximo_inicio:
            candidatos.append({
                'data_evento': proximo_inicio.data_inicio,
                'tipo': 'Início', 
                'descricao': proximo_inicio.descricao,
                'cliente_nome': proximo_inicio.cliente.nome if proximo_inicio.cliente else "N/A"
            })
        if proximo_fim:
            candidatos.append({
                'data_evento': proximo_fim.data_previsao_termino,
                'tipo': 'Entrega',
                'descricao': proximo_fim.descricao,
                'cliente_nome': proximo_fim.cliente.nome if proximo_fim.cliente else "N/A"
            })
            
        if not candidatos: return Response({})
        
        # Pega o mais próximo (menor data)
        candidatos.sort(key=lambda x: x['data_evento'])
        evento = candidatos[0]
        
        # Calcula dias restantes
        evento['dias'] = (evento['data_evento'] - hoje).days
        return Response(evento)

class DashboardProjetosView(views.APIView):
    def get(self, request):
        ativos = Agenda.objects.filter(data_previsao_termino__gte=date.today()).count()
        return Response({'ativos': ativos})

class RelatorioCompletoView(views.APIView):
    def get(self, request):
        # Simplificado para evitar erros complexos agora
        agendas = Agenda.objects.all().order_by('-data_previsao_termino')[:50]
        dados = []
        for a in agendas:
            dados.append({
                "projeto": a.descricao,
                "cliente": a.cliente.nome if a.cliente else "N/A",
                "data": a.data_previsao_termino,
                "total_projeto": 0, # Placeholder
                "a_receber": 0      # Placeholder
            })
        return Response(dados)