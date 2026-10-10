import os
from secrets import compare_digest

from flask import Flask, jsonify, request
from banco import (
    criar_tabela,
    listar_chamados,
    inserir_chamado,
    atualizar_status,
    buscar_chamado,
    excluir_chamado
)

app = Flask(__name__)

CHAVE_API = os.environ.get("CHAVE_API")

if not CHAVE_API:
    raise RuntimeError("Configure a variavel CHAVE_API antes de iniciar.")


@app.before_request
def verificar_chave():
    if request.endpoint == "inicio":
        return None

    chave_recebida = request.headers.get("X-API-Key", "")

    if not compare_digest(
        chave_recebida.encode("utf-8"),
        CHAVE_API.encode("utf-8")
    ):
        return jsonify({
            "erro": "Chave de acesso ausente ou invalida."
        }), 401


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API de chamados funcionando!"})


@app.route("/chamados", methods=["GET"])
def consultar_chamados():
    status = request.args.get("status")
    permitidos = ("aberto", "em andamento", "concluido")

    if status is not None and status not in permitidos:
        return jsonify({
            "erro": "Status permitido: aberto, em andamento ou concluido."
        }), 400

    return jsonify(listar_chamados(status))


@app.route("/chamados", methods=["POST"])
def cadastrar_chamado():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um objeto JSON valido."}), 400

    limites = {"titulo": 100, "descricao": 1000, "local": 100}
    campos = {}

    for campo, limite in limites.items():
        valor = dados.get(campo)

        if not isinstance(valor, str) or not valor.strip():
            return jsonify({
                "erro": f"O campo '{campo}' deve ser um texto preenchido."
            }), 400

        valor = valor.strip()

        if len(valor) > limite:
            return jsonify({
                "erro": f"O campo '{campo}' aceita ate {limite} caracteres."
            }), 400

        campos[campo] = valor

    identificador = inserir_chamado(
        campos["titulo"],
        campos["descricao"],
        campos["local"]
    )

    return jsonify({
        "mensagem": "Chamado cadastrado com sucesso!",
        "id": identificador
    }), 201


@app.route("/chamados/<int:identificador>", methods=["PATCH"])
def alterar_status(identificador):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um objeto JSON valido."}), 400

    status = dados.get("status")
    permitidos = ("aberto", "em andamento", "concluido")

    if not isinstance(status, str) or status not in permitidos:
        return jsonify({
            "erro": "Status permitido: aberto, em andamento ou concluido."
        }), 400

    if not atualizar_status(identificador, status):
        return jsonify({"erro": "Chamado nao encontrado."}), 404

    return jsonify({
        "mensagem": "Status atualizado com sucesso!",
        "id": identificador,
        "status": status
    }), 200


@app.route("/chamados/<int:identificador>", methods=["GET"])
def consultar_chamado(identificador):
    chamado = buscar_chamado(identificador)

    if chamado is None:
        return jsonify({"erro": "Chamado nao encontrado."}), 404

    return jsonify(chamado), 200


@app.route("/chamados/<int:identificador>", methods=["DELETE"])
def remover_chamado(identificador):
    if not excluir_chamado(identificador):
        return jsonify({"erro": "Chamado nao encontrado."}), 404

    return jsonify({
        "mensagem": "Chamado excluido com sucesso!",
        "id": identificador
    }), 200


if __name__ == "__main__":
    criar_tabela()
    app.run(host="127.0.0.1", port=5000)