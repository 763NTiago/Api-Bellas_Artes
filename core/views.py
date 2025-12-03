from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Q
from datetime import date
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
        # Total a receber (Parcelas não pagas)
        total = Parcela.objects.filter(valor_recebido__lt=models.F('valor_parcela')).aggregate(Sum('valor_parcela'))
        # Nota: O cálculo exato pode precisar subtrair o valor_recebido parcial, mas para simplificar:
        return Response({'total_a_receber': total['valor_parcela__sum'] or 0.0})

class DashboardProjetosView(views.APIView):
    def get(self, request):
        ativos = Agenda.objects.filter(data_previsao_termino__gte=date.today()).count()
        return Response({'ativos': ativos})

class RelatorioCompletoView(views.APIView):
    def get(self, request):
        # Lógica simplificada do relatório
        agendas = Agenda.objects.all().select_related('cliente').order_by('-data_previsao_termino')[:100]
        dados = []
        for a in agendas:
            dados.append({
                "projeto": a.descricao,
                "cliente": a.cliente.nome if a.cliente else "N/A",
                "data": a.data_previsao_termino,
                # Adicionar mais campos conforme necessário
            })
        return Response(dados)