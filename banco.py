import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent / "chamados.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = conectar()

    try:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                local TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'aberto',
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conexao.commit()
    finally:
        conexao.close()


def listar_chamados(status=None):
    conexao = conectar()

    try:
        if status is None:
            registros = conexao.execute(
                "SELECT * FROM chamados ORDER BY id DESC"
            ).fetchall()
        else:
            registros = conexao.execute(
                "SELECT * FROM chamados WHERE status = ? ORDER BY id DESC",
                (status,)
            ).fetchall()

        return [dict(registro) for registro in registros]
    finally:
        conexao.close()


def inserir_chamado(titulo, descricao, local):
    conexao = conectar()

    try:
        cursor = conexao.execute("""
            INSERT INTO chamados (titulo, descricao, local)
            VALUES (?, ?, ?)
        """, (titulo, descricao, local))

        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def atualizar_status(identificador, status):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            "UPDATE chamados SET status = ? WHERE id = ?",
            (status, identificador)
        )

        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def buscar_chamado(identificador):
    conexao = conectar()

    try:
        registro = conexao.execute(
            "SELECT * FROM chamados WHERE id = ?",
            (identificador,)
        ).fetchone()

        return dict(registro) if registro is not None else None
    finally:
        conexao.close()


def excluir_chamado(identificador):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            "DELETE FROM chamados WHERE id = ?",
            (identificador,)
        )

        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()