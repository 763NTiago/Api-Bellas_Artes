# Api-Bellas_Artes/core/management/commands/importar_sqlite.py
import sqlite3
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from core.models import Cliente, Material, Arquiteto, Agenda, Orcamento, Recebimento, Parcela, Comissao

class Command(BaseCommand):
    help = 'Importa dados do SQLite antigo para o PostgreSQL'

    def handle(self, *args, **options):
        # Caminho do banco antigo (na pasta data/ dentro do container)
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
        rows = cursor.fetchall()
        map_clientes = {} # Para ligar ID antigo -> ID novo
        for row in rows:
            obj, created = Cliente.objects.get_or_create(nome=row['nome'])
            map_clientes[row['id']] = obj
        self.stdout.write(f"Clientes importados: {len(rows)}")

        # 2. MATERIAIS
        cursor.execute("SELECT * FROM materiais")
        for row in rows:
            Material.objects.get_or_create(nome=row['nome'], defaults={'descricao': row['descricao']})

        # 3. ARQUITETOS
        cursor.execute("SELECT * FROM arquitetos")
        for row in rows:
            # Tratamento de data simples
            data_pag = row['data_pagamento'] if row['data_pagamento'] else None
            Arquiteto.objects.get_or_create(nome=row['nome'], defaults={'data_pagamento': data_pag})

        # 4. AGENDA
        cursor.execute("SELECT * FROM agenda")
        rows = cursor.fetchall()
        map_agenda = {}
        for row in rows:
            cliente_obj = map_clientes.get(row['cliente_id'])
            obj = Agenda.objects.create(
                cliente=cliente_obj,
                data_inicio=row['data_inicio'],
                data_previsao_termino=row['data_previsao_termino'],
                descricao=row['descricao']
            )
            map_agenda[row['id']] = obj
        self.stdout.write(f"Agenda importada: {len(rows)}")

        # 5. ORÇAMENTOS
        cursor.execute("SELECT * FROM orcamentos")
        for row in cursor.fetchall():
            agenda_obj = map_agenda.get(row['agenda_id'])
            Orcamento.objects.create(
                data_criacao=row['data_criacao'],
                cliente_nome=row['cliente_nome'],
                cliente_endereco=row['cliente_endereco'],
                cliente_cpf=row['cliente_cpf'],
                cliente_email=row['cliente_email'],
                cliente_telefone=row['cliente_telefone'],
                itens_json=row['itens_json'],
                valor_total_final=row['valor_total_final'],
                observacoes=row['observacoes'],
                condicoes_pagamento=row['condicoes_pagamento'],
                agenda=agenda_obj
            )

        # 6. RECEBIMENTOS
        cursor.execute("SELECT * FROM recebimentos_pagamentos")
        rows = cursor.fetchall()
        map_recebimentos = {}
        for row in rows:
            cliente_obj = map_clientes.get(row['cliente_id'])
            agenda_obj = map_agenda.get(row['agenda_id'])
            obj = Recebimento.objects.create(
                cliente=cliente_obj,
                agenda=agenda_obj,
                tipo_pagamento=row['tipo_pagamento'],
                valor_total=row['valor_total'] or 0,
                valor_entrada=row['valor_entrada'] or 0,
                num_parcelas=row['num_parcelas'] or 0,
                valor_parcela=row['valor_parcela'] or 0,
                data_1_venc=row['data_1_venc'] or ""
            )
            map_recebimentos[row['id']] = obj

        # 7. PARCELAS
        cursor.execute("SELECT * FROM parcelas")
        for row in cursor.fetchall():
            recebimento_obj = map_recebimentos.get(row['recebimento_id'])
            if recebimento_obj:
                Parcela.objects.create(
                    recebimento=recebimento_obj,
                    num_parcela=row['num_parcela'],
                    valor_parcela=row['valor_parcela'] or 0,
                    data_vencimento=row['data_vencimento'],
                    data_recebimento=row['data_recebimento'],
                    valor_recebido=row['valor_recebido']
                )

        # 8. COMISSÕES
        cursor.execute("SELECT * FROM comissoes")
        for row in cursor.fetchall():
            cliente_obj = map_clientes.get(row['cliente_id'])
            recebimento_obj = map_recebimentos.get(row['recebimento_id'])
            Comissao.objects.create(
                data=row['data'],
                cliente=cliente_obj,
                recebimento=recebimento_obj,
                beneficiario=row['beneficiario'],
                descricao=row['descricao'],
                valor=row['valor'] or 0,
                porcentagem=row['porcentagem'] or 0,
                valor_base=row['valor_base'] or 0
            )

        conn.close()
        self.stdout.write(self.style.SUCCESS('DADOS IMPORTADOS COM SUCESSO!'))