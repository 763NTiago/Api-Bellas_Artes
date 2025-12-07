from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'usuarios', UserViewSet) # <--- Nova rota para Perfil
router.register(r'clientes', ClienteViewSet)
router.register(r'materiais', MaterialViewSet)
router.register(r'arquitetos', ArquitetoViewSet)
router.register(r'agenda', AgendaViewSet)
router.register(r'orcamentos', OrcamentoViewSet)
router.register(r'recebimentos', RecebimentoViewSet)
router.register(r'parcelas', ParcelaViewSet)
router.register(r'comissoes', ComissaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()), # <--- Nova rota para Login
    path('dashboard/financeiro/', DashboardFinanceiroView.as_view()),
    path('dashboard/projetos/', DashboardProjetosView.as_view()),
    path('dashboard/eventos/', DashboardEventosView.as_view()),
    path('relatorios/completo/', RelatorioCompletoView.as_view()),
]