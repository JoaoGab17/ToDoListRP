// src/ListaDeTarefas.jsx (Versão Full-Stack Final)
import React, { useState, useEffect } from 'react';

// Endereço da sua API na nuvem (Render)
const API_URL = import.meta.env.VITE_API_URL || 'https://todolistrp.onrender.com';

// --- Componentes Filhos ---
const TaskForm = ({ onAddTask }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!inputValue.trim()) return;
    onAddTask(inputValue);
    setInputValue('');
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <input
        type="text"
        placeholder="O que precisa ser feito?"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        className="task-input"
      />
      <button type="submit" className="add-button">
        Adicionar
      </button>
    </form>
  );
};

const TaskItem = ({ task, onUpdateStatus, onMoveToTrash }) => {
  const itemClassName = `task-item ${task.status === 'concluída' ? 'completed' : ''}`;

  return (
    <li className={itemClassName}>
      <span className="task-item-text">{task.titulo}</span>
      <div className="task-item-actions">
        <select 
          className="status-select" 
          value={task.status} 
          onChange={(e) => onUpdateStatus(task.id, e.target.value)}
        >
          <option value="pendente">Pendente</option>
          <option value="fazendo">Fazendo</option>
          <option value="concluída">Concluída</option>
        </select>
        <button onClick={() => onMoveToTrash(task.id)} className="remove-button" title="Mover para Lixeira">
          🗑️
        </button>
      </div>
    </li>
  );
};

// --- Componente Principal ---
const ListaDeTarefasContainer = () => {
  // O estado agora começa vazio e será preenchido pela API
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Função para buscar os dados da API
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/tarefas`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error("Erro ao buscar tarefas:", error);
      alert("Não foi possível conectar ao servidor da API. Verifique se a URL da API está correta e se o servidor no Render está no ar.");
    } finally {
      setLoading(false);
    }
  };

  // useEffect com [] no final roda UMA VEZ quando o componente é montado
  useEffect(() => {
    fetchTasks();
  }, []);

  // Funções que fazem chamadas de API para manipular os dados
  const addTask = async (text) => {
    await fetch(`${API_URL}/tarefas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    fetchTasks(); // Re-busca os dados para atualizar a lista
  };
  
  const moveToTrash = async (id) => {
    await fetch(`${API_URL}/tarefas/${id}`, { method: 'DELETE' });
    fetchTasks();
  };

  const updateStatus = async (id, newStatus) => {
    await fetch(`${API_URL}/tarefas/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    fetchTasks();
  };
  
  return (
    <div className="app-container">
      <h1>To-Do List Full-Stack</h1>
      <TaskForm onAddTask={addTask} />

      {/* Mostra uma mensagem de 'Carregando...' enquanto os dados não chegam */}
      {loading ? (
        <p style={{textAlign: 'center'}}>Carregando tarefas do banco de dados na nuvem...</p>
      ) : (
        <ul className="task-list">
          {tasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onUpdateStatus={updateStatus}
              onMoveToTrash={moveToTrash}
            />
          ))}
        </ul>
      )}
    </div>
  );
};

export default ListaDeTarefasContainer;
