# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import database as db
from database import StatusTarefa

app = Flask(__name__)
CORS(app) # Permite a comunicação com o frontend

# --- Endpoints da API REST ---

@app.route('/tarefas', methods=['GET'])
def get_tarefas_ativas():
    tarefas = db.listar_tarefas()
    return jsonify([task.__dict__ for task in tarefas])

@app.route('/tarefas/excluidas', methods=['GET'])
def get_tarefas_excluidas():
    """NOVO ENDPOINT: para a lixeira."""
    tarefas = db.listar_tarefas_excluidas()
    return jsonify([task.__dict__ for task in tarefas])

@app.route('/tarefas', methods=['POST'])
def add_tarefa():
    dados = request.get_json()
    if not dados or not dados.get('text'):
        return jsonify({'erro': 'O texto da tarefa é obrigatório'}), 400
    nova_tarefa = db.adicionar_tarefa(dados['text'])
    return jsonify(nova_tarefa.__dict__), 201

@app.route('/tarefas/<int:id>/status', methods=['PUT'])
def update_tarefa_status(id):
    dados = request.get_json()
    novo_status_str = dados.get('status')
    try:
        novo_status_enum = StatusTarefa(novo_status_str)
    except ValueError:
        return jsonify({'erro': 'Status inválido'}), 400
    if db.atualizar_status(id, novo_status_enum):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Tarefa não encontrada'}), 404

@app.route('/tarefas/<int:id>', methods=['DELETE'])
def mover_para_lixeira(id):
    """Este endpoint agora faz a exclusão LÓGICA."""
    if db.desativar_tarefa(id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Tarefa não encontrada'}), 404

@app.route('/tarefas/<int:id>/recuperar', methods=['PUT'])
def recuperar_tarefa_da_lixeira(id):
    """NOVO ENDPOINT: para restaurar uma tarefa."""
    if db.recuperar_tarefa(id):
        return jsonify({'sucesso': True})
    return jsonify({'erro': 'Tarefa não encontrada na lixeira'}), 404

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True)