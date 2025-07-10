# database.py
import psycopg2
from psycopg2.extras import RealDictCursor
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- NOVA CONFIGURAÇÃO DE CONEXÃO ---
DATABASE_URL = os.getenv("DB_CONNECTION_STRING")

# --- O DATACLASS E O ENUM NÃO MUDAM ---
@dataclass
class Tarefa:
    id: int
    titulo: str
    status: str
    ativo: bool

class StatusTarefa(Enum):
    PENDENTE = "pendente"
    FAZENDO = "fazendo"
    CONCLUIDA = "concluída"

# --- FUNÇÕES ADAPTADAS PARA POSTGRESQL ---

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Cria a tabela de tarefas se ela não existir."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Sintaxe do PostgreSQL: SERIAL PRIMARY KEY auto-incrementa o ID.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                status TEXT NOT NULL,
                ativo BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)
    conn.commit()
    conn.close()

def _map_row_to_tarefa(row):
    """Converte uma linha do banco (dicionário) em um objeto Tarefa."""
    if not row:
        return None
    # O status vem do DB como texto, convertemos para nosso Enum para consistência
    # O dataclass não precisa mais do campo 'status', pois já está no objeto
    return Tarefa(id=row['id'], titulo=row['titulo'], status=row['status'], ativo=row['ativo'])


def listar_tarefas() -> List[Tarefa]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Placeholders no psycopg2 são '%s' em vez de '?'
        cur.execute("SELECT * FROM tarefas WHERE ativo = TRUE ORDER BY id;")
        rows = cur.fetchall()
    conn.close()
    return [_map_row_to_tarefa(row) for row in rows]

def listar_tarefas_excluidas() -> List[Tarefa]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM tarefas WHERE ativo = FALSE ORDER BY id;")
        rows = cur.fetchall()
    conn.close()
    return [_map_row_to_tarefa(row) for row in rows]

def adicionar_tarefa(titulo: str) -> Tarefa:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # RETURNING id, titulo, status, ativo faz o DB retornar a linha recém-criada
        cur.execute(
            "INSERT INTO tarefas (titulo, status) VALUES (%s, %s) RETURNING *;",
            (titulo, StatusTarefa.PENDENTE.value)
        )
        nova_tarefa_row = cur.fetchone()
    conn.commit()
    conn.close()
    return _map_row_to_tarefa(nova_tarefa_row)

# ... (as outras funções: buscar_por_id, atualizar_status, desativar_tarefa, recuperar_tarefa)
# seguem o mesmo padrão de adaptação para psycopg2 e placeholders %s ...
def buscar_tarefa_por_id(id_tarefa: int) -> Optional[Tarefa]:
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM tarefas WHERE id = %s;", (id_tarefa,))
        row = cur.fetchone()
    conn.close()
    return _map_row_to_tarefa(row)

def atualizar_status(id_tarefa: int, novo_status: StatusTarefa) -> bool:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE tarefas SET status = %s WHERE id = %s AND ativo = TRUE;",
            (novo_status.value, id_tarefa)
        )
        updated_rows = cur.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0

def desativar_tarefa(id_tarefa: int) -> bool:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE tarefas SET ativo = FALSE WHERE id = %s;", (id_tarefa,))
        updated_rows = cur.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0

def recuperar_tarefa(id_tarefa: int) -> bool:
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE tarefas SET ativo = TRUE WHERE id = %s;", (id_tarefa,))
        updated_rows = cur.rowcount
    conn.commit()
    conn.close()
    return updated_rows > 0