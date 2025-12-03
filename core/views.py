from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from datetime import date, timedelta
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao
from .serializers import *

# =============================================================================
#                               VIEWSETS (CRUD)
# =============================================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        nome = request.data.get('nome')
        if not nome: 
            return Response({'error': 'Nome obrigatório'}, status=400)
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

# =============================================================================
#                           DASHBOARDS & RELATÓRIOS
# =============================================================================

class DashboardFinanceiroView(views.APIView):
    def get(self, request):
        # Cálculo Seguro: Valor Restante = Parcela - Recebido (se recebido for Null, assume 0)
        valor_restante = F('valor_parcela') - Coalesce(F('valor_recebido'), Value(0, output_field=DecimalField()))
        
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
        
        # 4. Comissões Pagas (Até hoje)
        comissoes_pagas = Comissao.objects.filter(
            data__lte=date.today()
        ).aggregate(Sum('valor'))

        # 5. Comissões Pendentes (Futuras)
        comissoes_pendentes = Comissao.objects.filter(
            data__gt=date.today()
        ).aggregate(Sum('valor'))

        return Response({
            'total_a_receber': total_geral['restante__sum'] or 0.0,
            'total_a_receber_30d': total_30d['restante__sum'] or 0.0,
            'total_recebido_geral': total_recebido['valor_recebido__sum'] or 0.0,
            'total_comissoes_ja_pagas': comissoes_pagas['valor__sum'] or 0.0,
            'total_comissoes_pendentes': comissoes_pendentes['valor__sum'] or 0.0
        })

class DashboardEventosView(views.APIView):
    def get(self, request):
        hoje = date.today()
        # Busca o próximo início e a próxima entrega
        proximo_inicio = Agenda.objects.filter(data_inicio__gte=hoje).order_by('data_inicio').first()
        proximo_fim = Agenda.objects.filter(data_previsao_termino__gte=hoje).order_by('data_previsao_termino').first()
        
        candidatos = []
        
        # Adiciona candidato de INÍCIO se existir
        if proximo_inicio:
            # Proteção: Verifica se tem cliente, se não tiver usa "N/A"
            nome_cli = proximo_inicio.cliente.nome if proximo_inicio.cliente else "Cliente N/A"
            candidatos.append({
                'data_evento': proximo_inicio.data_inicio,
                'tipo': 'Início', 
                'descricao': proximo_inicio.descricao or "Sem Descrição",
                'cliente_nome': nome_cli
            })
            
        # Adiciona candidato de ENTREGA se existir
        if proximo_fim:
            nome_cli = proximo_fim.cliente.nome if proximo_fim.cliente else "Cliente N/A"
            candidatos.append({
                'data_evento': proximo_fim.data_previsao_termino,
                'tipo': 'Entrega',
                'descricao': proximo_fim.descricao or "Sem Descrição",
                'cliente_nome': nome_cli
            })
            
        if not candidatos: 
            return Response({}) # Retorna vazio se não houver eventos futuros
        
        # Ordena pela data para pegar o mais próximo
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
        # Limita a 50 para não pesar no carregamento inicial
        agendas = Agenda.objects.all().order_by('-data_previsao_termino')[:50]
        dados = []
        for a in agendas:
            nome_cli = a.cliente.nome if a.cliente else "Cliente N/A"
            dados.append({
                "projeto": a.descricao or "Sem Descrição",
                "cliente": nome_cli,
                "data": a.data_previsao_termino,
                "total_projeto": 0, # Placeholder para lógica futura
                "a_receber": 0      # Placeholder para lógica futura
            })
        return Response(dados)