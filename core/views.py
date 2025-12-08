from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F, Value, DecimalField, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from datetime import date, timedelta, datetime
from .models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao
from .serializers import *

class LoginView(views.APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            return Response({
                'id': user.id,
                'token': 'sessao_valida_bellas_artes',
                'first_name': user.first_name or user.username,
                'email': user.email,
                'username': user.username
            }, status=200)
        else:
            return Response({'error': 'Credenciais inválidas'}, status=401)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('nome')
    serializer_class = ClienteSerializer
    
    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        nome = request.data.get('nome')
        if not nome: 
            return Response({'error': 'Nome obrigatório'}, status=400)
        cliente, created = Cliente.objects.get_or_create(nome=nome)
        return Response({'id': cliente.id, 'nome': cliente.nome})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        term = request.query_params.get('q', '')
        clientes = self.queryset.filter(nome__icontains=term)[:10]
        return Response([{'id': c.id, 'nome': c.nome} for c in clientes])

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('nome')
    serializer_class = MaterialSerializer

class ArquitetoViewSet(viewsets.ModelViewSet):
    queryset = Arquiteto.objects.all().order_by('nome')
    serializer_class = ArquitetoSerializer

class AgendaViewSet(viewsets.ModelViewSet):
    queryset = Agenda.objects.all().order_by('-data_previsao_termino')
    serializer_class = AgendaSerializer

    @action(detail=False, methods=['get'])
    def datas_calendario(self, request):
        agendas = Agenda.objects.all().values('data_inicio', 'data_previsao_termino')
        datas = set()
        for a in agendas:
            if a['data_inicio']: datas.add(a['data_inicio'])
            if a['data_previsao_termino']: datas.add(a['data_previsao_termino'])
        return Response(list(datas))

class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.all().order_by('-id')
    serializer_class = OrcamentoSerializer

class RecebimentoViewSet(viewsets.ModelViewSet):
    queryset = Recebimento.objects.all()
    serializer_class = RecebimentoSerializer

class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.all().order_by('data_vencimento')
    serializer_class = ParcelaSerializer

    @action(detail=False, methods=['get'])
    def datas_vencimento(self, request):
        pendentes = Parcela.objects.annotate(
            saldo=F('valor_parcela') - Coalesce('valor_recebido', Value(0, output_field=DecimalField()))
        ).filter(saldo__gt=0.01, num_parcela__gt=0).values_list('data_vencimento', flat=True).distinct()
        return Response(list(pendentes))
    
    @action(detail=False, methods=['get'])
    def proximas_pendentes(self, request):
        hoje = date.today()
        parcelas = Parcela.objects.annotate(
            saldo=F('valor_parcela') - Coalesce('valor_recebido', Value(0, output_field=DecimalField()))
        ).filter(
            num_parcela__gt=0,
            saldo__gt=0.01,
            data_vencimento__gte=hoje
        ).order_by('data_vencimento')[:10]
        serializer = self.get_serializer(parcelas, many=True)
        return Response(serializer.data)

class ComissaoViewSet(viewsets.ModelViewSet):
    queryset = Comissao.objects.all().order_by('-data')
    serializer_class = ComissaoSerializer

class DashboardFinanceiroView(views.APIView):
    def get(self, request):
        valor_restante = F('valor_parcela') - Coalesce(F('valor_recebido'), Value(0, output_field=DecimalField()))
        
        total_geral = Parcela.objects.filter(num_parcela__gt=0).annotate(restante=valor_restante).filter(
            restante__gt=0.01
        ).aggregate(Sum('restante'))

        limite = date.today() + timedelta(days=30)
        total_30d = Parcela.objects.filter(num_parcela__gt=0).annotate(restante=valor_restante).filter(
            restante__gt=0.01,
            data_vencimento__range=[date.today(), limite]
        ).aggregate(Sum('restante'))

        total_recebido = Parcela.objects.aggregate(Sum('valor_recebido'))
        
        comissoes_pagas = Comissao.objects.filter(data__lte=date.today()).aggregate(Sum('valor'))
        comissoes_pendentes = Comissao.objects.filter(data__gt=date.today()).aggregate(Sum('valor'))

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
        filtro_data = request.query_params.get('data')
        
        if filtro_data:
            try:
                data_alvo = datetime.strptime(filtro_data, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de data inválido'}, status=400)
                
            eventos = []
            agendas = Agenda.objects.filter(Q(data_inicio=data_alvo) | Q(data_previsao_termino=data_alvo))
            for a in agendas:
                cli = a.cliente.nome if a.cliente else "Cliente N/A"
                if a.data_inicio == data_alvo:
                    eventos.append({'tipo': 'Início', 'descricao': f"Início: {a.descricao}", 'cliente': cli})
                if a.data_previsao_termino == data_alvo:
                    eventos.append({'tipo': 'Entrega', 'descricao': f"Entrega: {a.descricao}", 'cliente': cli})
            
            parcelas = Parcela.objects.filter(data_vencimento=data_alvo, num_parcela__gt=0).annotate(
                saldo=F('valor_parcela') - Coalesce('valor_recebido', Value(0, output_field=DecimalField()))
            ).filter(saldo__gt=0.01)
            
            for p in parcelas:
                cli_nome = "Cliente N/A"
                proj_desc = "Geral"
                if p.recebimento:
                    if p.recebimento.cliente: cli_nome = p.recebimento.cliente.nome
                    if p.recebimento.agenda: proj_desc = p.recebimento.agenda.descricao
                
                eventos.append({
                    'tipo': 'Vencimento',
                    'descricao': f"Parc. {p.num_parcela} - {proj_desc}",
                    'cliente': cli_nome,
                    'valor': p.saldo
                })
            
            return Response(eventos)

        else:
            proximo_inicio = Agenda.objects.filter(data_inicio__gte=hoje).order_by('data_inicio').first()
            proximo_fim = Agenda.objects.filter(data_previsao_termino__gte=hoje).order_by('data_previsao_termino').first()
            
            candidatos = []
            if proximo_inicio:
                candidatos.append({
                    'data_evento': proximo_inicio.data_inicio,
                    'tipo': 'Início', 
                    'descricao': proximo_inicio.descricao or "Sem Descrição",
                    'cliente_nome': proximo_inicio.cliente.nome if proximo_inicio.cliente else "N/A"
                })
            if proximo_fim:
                candidatos.append({
                    'data_evento': proximo_fim.data_previsao_termino,
                    'tipo': 'Entrega',
                    'descricao': proximo_fim.descricao or "Sem Descrição",
                    'cliente_nome': proximo_fim.cliente.nome if proximo_fim.cliente else "N/A"
                })
                
            if not candidatos: return Response({})
            
            candidatos.sort(key=lambda x: x['data_evento'])
            evento = candidatos[0]
            evento['dias'] = (evento['data_evento'] - hoje).days
            return Response(evento)

class DashboardProjetosView(views.APIView):
    def get(self, request):
        ativos = Agenda.objects.filter(data_previsao_termino__gte=date.today()).count()
        return Response({'ativos': ativos})

class RelatorioCompletoView(views.APIView):
    def get(self, request):
        agendas = Agenda.objects.all().select_related('cliente').order_by('-data_previsao_termino')
        
        dados = []
        for a in agendas:
            orcamento = Orcamento.objects.filter(agenda=a).first()
            recebimento = Recebimento.objects.filter(agenda=a).first()
            
            valor_projeto = 0.0
            tipo_pagamento = "N/D"
            num_parcelas = 0
            
            if recebimento:
                valor_projeto = float(recebimento.valor_total)
                tipo_pagamento = recebimento.tipo_pagamento
                num_parcelas = recebimento.num_parcelas
            elif orcamento:
                val_str = str(orcamento.valor_total_final or "0")
                val_str = val_str.replace("R$", "").strip()
                try:
                    if "," in val_str and "." in val_str:
                        val_str = val_str.replace(".", "").replace(",", ".")
                    elif "," in val_str:
                        val_str = val_str.replace(",", ".")
                    valor_projeto = float(val_str)
                except ValueError: 
                    valor_projeto = 0.0
            
            total_recebido = 0.0
            if recebimento:
                soma = Parcela.objects.filter(recebimento=recebimento).aggregate(Sum('valor_recebido'))
                total_recebido = float(soma['valor_recebido__sum'] or 0.0)

            total_comissao = 0.0
            arquiteto_nome = ""
            if recebimento:
                comissoes = Comissao.objects.filter(recebimento=recebimento)
                soma_com = comissoes.aggregate(Sum('valor'))
                total_comissao = float(soma_com['valor__sum'] or 0.0)
                primeira = comissoes.first()
                if primeira: arquiteto_nome = primeira.beneficiario
            
            if not arquiteto_nome and hasattr(a, 'arquiteto') and a.arquiteto:
                 arquiteto_nome = a.arquiteto.nome

            saldo_a_receber = max(0.0, valor_projeto - total_recebido)

            dados.append({
                "agenda_id": a.id,
                "data_inicio": a.data_inicio,
                "data": a.data_previsao_termino,
                "cliente": a.cliente.nome if a.cliente else "Cliente N/A",
                "projeto": a.descricao or "Sem Descrição",
                "tipo_pagamento": tipo_pagamento,
                "num_parcelas": num_parcelas,
                "arquiteto": arquiteto_nome,
                "total_projeto": valor_projeto,
                "total_comissao": total_comissao,
                "sobrou_liquido": valor_projeto - total_comissao,
                "valor_pago_cliente": total_recebido,
                "a_receber": saldo_a_receber
            })
            
        return Response(dados)