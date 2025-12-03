import sqlite3
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from core.models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao

class Command(BaseCommand):
    help = 'Importa dados do SQLite antigo para o PostgreSQL'

    def handle(self, *args, **options):
        db_path = os.path.join(settings.BASE_DIR, 'data', 'orcamentos.db')
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Banco não encontrado em: {db_path}'))
            return

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        self.stdout.write("Iniciando importação...")

        # 1. CLIENTES
        cursor.execute("SELECT * FROM clientes_app")
        rows_clientes = cursor.fetchall()
        map_clientes = {} 
        for row in rows_clientes:
            obj, created = Cliente.objects.get_or_create(nome=row['nome'])
            map_clientes[row['id']] = obj
        self.stdout.write(f"Clientes importados: {len(rows_clientes)}")

        # 2. MATERIAIS (CORRIGIDO: adicionei o fetchall)
        cursor.execute("SELECT * FROM materiais")
        rows_materiais = cursor.fetchall()
        for row in rows_materiais:
            # Proteção caso a coluna descricao não exista no banco antigo
            desc = row['descricao'] if 'descricao' in row.keys() else ""
            Material.objects.get_or_create(nome=row['nome'], defaults={'descricao': desc})
        self.stdout.write(f"Materiais importados: {len(rows_materiais)}")

        # 3. ARQUITETOS (CORRIGIDO: adicionei o fetchall)
        cursor.execute("SELECT * FROM arquitetos")
        rows_arquitetos = cursor.fetchall()
        for row in rows_arquitetos:
            data_pag = row['data_pagamento'] if row['data_pagamento'] else None
            Arquiteto.objects.get_or_create(nome=row['nome'], defaults={'data_pagamento': data_pag})
        self.stdout.write(f"Arquitetos importados: {len(rows_arquitetos)}")

        # 4. AGENDA
        cursor.execute("SELECT * FROM agenda")
        rows_agenda = cursor.fetchall()
        map_agenda = {}
        for row in rows_agenda:
            cliente_obj = map_clientes.get(row['cliente_id'])
            # Usamos get_or_create para evitar duplicação se rodares o script 2 vezes
            obj, created = Agenda.objects.get_or_create(
                descricao=row['descricao'],
                cliente=cliente_obj,
                defaults={
                    'data_inicio': row['data_inicio'],
                    'data_previsao_termino': row['data_previsao_termino']
                }
            )
            map_agenda[row['id']] = obj
        self.stdout.write(f"Agenda importada: {len(rows_agenda)}")

        # 5. ORÇAMENTOS
        cursor.execute("SELECT * FROM orcamentos")
        rows_orcamentos = cursor.fetchall()
        for row in rows_orcamentos:
            agenda_obj = map_agenda.get(row['agenda_id'])
            Orcamento.objects.get_or_create(
                data_criacao=row['data_criacao'],
                cliente_nome=row['cliente_nome'],
                defaults={
                    'cliente_endereco': row['cliente_endereco'],
                    'cliente_cpf': row['cliente_cpf'],
                    'cliente_email': row['cliente_email'],
                    'cliente_telefone': row['cliente_telefone'],
                    'itens_json': row['itens_json'],
                    'valor_total_final': row['valor_total_final'],
                    'observacoes': row['observacoes'],
                    'condicoes_pagamento': row['condicoes_pagamento'],
                    'agenda': agenda_obj
                }
            )

        # 6. RECEBIMENTOS
        cursor.execute("SELECT * FROM recebimentos_pagamentos")
        rows_recebimentos = cursor.fetchall()
        map_recebimentos = {}
        for row in rows_recebimentos:
            cliente_obj = map_clientes.get(row['cliente_id'])
            agenda_obj = map_agenda.get(row['agenda_id'])
            obj, created = Recebimento.objects.get_or_create(
                cliente=cliente_obj,
                agenda=agenda_obj,
                tipo_pagamento=row['tipo_pagamento'],
                valor_total=row['valor_total'] or 0,
                defaults={
                    'valor_entrada': row['valor_entrada'] or 0,
                    'num_parcelas': row['num_parcelas'] or 0,
                    'valor_parcela': row['valor_parcela'] or 0,
                    'data_1_venc': row['data_1_venc'] or ""
                }
            )
            map_recebimentos[row['id']] = obj

        # 7. PARCELAS
        cursor.execute("SELECT * FROM parcelas")
        rows_parcelas = cursor.fetchall()
        for row in rows_parcelas:
            recebimento_obj = map_recebimentos.get(row['recebimento_id'])
            if recebimento_obj:
                Parcela.objects.get_or_create(
                    recebimento=recebimento_obj,
                    num_parcela=row['num_parcela'],
                    defaults={
                        'valor_parcela': row['valor_parcela'] or 0,
                        'data_vencimento': row['data_vencimento'],
                        'data_recebimento': row['data_recebimento'],
                        'valor_recebido': row['valor_recebido']
                    }
                )

        # 8. COMISSÕES
        cursor.execute("SELECT * FROM comissoes")
        rows_comissoes = cursor.fetchall()
        for row in rows_comissoes:
            cliente_obj = map_clientes.get(row['cliente_id'])
            recebimento_obj = map_recebimentos.get(row['recebimento_id'])
            Comissao.objects.get_or_create(
                data=row['data'],
                recebimento=recebimento_obj,
                beneficiario=row['beneficiario'],
                defaults={
                    'cliente': cliente_obj,
                    'descricao': row['descricao'],
                    'valor': row['valor'] or 0,
                    'porcentagem': row['porcentagem'] or 0,
                    'valor_base': row['valor_base'] or 0
                }
            )

        conn.close()
        self.stdout.write(self.style.SUCCESS('DADOS IMPORTADOS COM SUCESSO!'))