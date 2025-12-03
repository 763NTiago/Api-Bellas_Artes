import sqlite3
import os
from django.core.management.base import BaseCommand
from core.models import ClienteApp, Orcamento, Agenda, Material, Arquiteto

class Command(BaseCommand):
    help = 'Importa dados do SQLite legado'

    def add_arguments(self, parser):
        parser.add_argument('db_path', type=str)

    def handle(self, *args, **options):
        db_path = options['db_path']
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"Arquivo não encontrado: {db_path}"))
            return

        self.stdout.write(f"Lendo banco: {db_path}...")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Importar Clientes
        try:
            cursor.execute("SELECT * FROM clientes_app")
            for row in cursor.fetchall():
                ClienteApp.objects.get_or_create(id=row['id'], defaults={'nome': row['nome']})
            self.stdout.write("Clientes OK.")
        except Exception as e: self.stdout.write(f"Nota Clientes: {e}")

        # Importar Materiais
        try:
            cursor.execute("SELECT * FROM materiais")
            for row in cursor.fetchall():
                Material.objects.get_or_create(id=row['id'], defaults={'nome': row['nome'], 'descricao': row['descricao']})
            self.stdout.write("Materiais OK.")
        except Exception as e: self.stdout.write(f"Nota Materiais: {e}")

        # Importar Agenda
        try:
            cursor.execute("SELECT * FROM agenda")
            for row in cursor.fetchall():
                dt_ini = row['data_inicio'] if row['data_inicio'] else None
                dt_fim = row['data_previsao_termino'] if row['data_previsao_termino'] else None
                Agenda.objects.get_or_create(
                    id=row['id'], 
                    defaults={
                        'cliente_id': row['cliente_id'], 
                        'descricao': row['descricao'], 
                        'data_inicio': dt_ini, 
                        'data_previsao_termino': dt_fim
                    }
                )
            self.stdout.write("Agenda OK.")
        except Exception as e: self.stdout.write(f"Nota Agenda: {e}")

        # Importar Orçamentos
        try:
            cursor.execute("SELECT * FROM orcamentos")
            for row in cursor.fetchall():
                Orcamento.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'agenda_id': row['agenda_id'],
                        'cliente_nome': row['cliente_nome'],
                        'data_criacao': row['data_criacao'],
                        'itens_json': row['itens_json'],
                        'valor_total_final': row['valor_total_final'],
                        'observacoes': row['observacoes'],
                        'condicoes_pagamento': row['condicoes_pagamento'],
                        'cliente_endereco': row['cliente_endereco'],
                        'cliente_cpf': row['cliente_cpf'],
                        'cliente_email': row['cliente_email'],
                        'cliente_telefone': row['cliente_telefone']
                    }
                )
            self.stdout.write("Orçamentos OK.")
        except Exception as e: self.stdout.write(f"Nota Orcamentos: {e}")

        self.stdout.write(self.style.SUCCESS('Importação finalizada!'))