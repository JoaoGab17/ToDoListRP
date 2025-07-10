import React, { useState, useEffect } from 'react';

// Em vez de: const API_URL = 'http://127.0.0.1:5000';
// Use:
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

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
  return (
    <li className={`task-item ${task.status === 'concluída' ? 'completed' : ''}`}>
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

const TrashedTaskItem = ({ task, onRestoreTask }) => {
  return (
    <li className="task-item">
      <span className="task-item-text completed">{task.titulo}</span>
      <div className="task-item-actions">
        <button onClick={() => onRestoreTask(task.id)} className="toggle-button" title="Restaurar Tarefa">
          ♻️
        </button>
      </div>
    </li>
  );
};

// --- Componente Principal ---
const ListaDeTarefasContainer = () => {
  const [tasks, setTasks] = useState([]);
  const [trashedTasks, setTrashedTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('active');
  const [loading, setLoading] = useState(true);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [activeRes, trashedRes] = await Promise.all([
        fetch(`${API_URL}/tarefas`),
        fetch(`${API_URL}/tarefas/excluidas`)
      ]);
      const activeData = await activeRes.json();
      const trashedData = await trashedRes.json();
      setTasks(activeData);
      setTrashedTasks(trashedData);
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      alert("Não foi possível conectar ao servidor da API. Verifique se o backend (api.py) está rodando.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const addTask = async (text) => {
    await fetch(`${API_URL}/tarefas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    fetchAllData();
  };

  const moveToTrash = async (id) => {
    await fetch(`${API_URL}/tarefas/${id}`, { method: 'DELETE' });
    fetchAllData();
  };
  
  const restoreTask = async (id) => {
    await fetch(`${API_URL}/tarefas/${id}/recuperar`, { method: 'PUT' });
    fetchAllData();
  };

  const updateStatus = async (id, newStatus) => {
    await fetch(`${API_URL}/tarefas/${id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    fetchAllData();
  };
  
  return (
    <div className="app-container">
      <h1>To-Do List Full-Stack</h1>

      {/* A LINHA QUE FALTAVA ESTÁ AQUI */}
      <TaskForm onAddTask={addTask} />

      <div className="tabs-container">
        <button className={`tab ${activeTab === 'active' ? 'active' : ''}`} onClick={() => setActiveTab('active')}>
          Tarefas Ativas ({tasks.length})
        </button>
        <button className={`tab ${activeTab === 'trashed' ? 'active' : ''}`} onClick={() => setActiveTab('trashed')}>
          Lixeira ({trashedTasks.length})
        </button>
      </div>

      <div className="tab-content">
        {loading ? <p style={{textAlign: 'center'}}>Carregando...</p> : (
          activeTab === 'active' ? (
            <ul className="task-list">
              {tasks.map(task => (
                <TaskItem key={task.id} task={task} onUpdateStatus={updateStatus} onMoveToTrash={moveToTrash} />
              ))}
            </ul>
          ) : (
            <ul className="task-list">
              {trashedTasks.map(task => (
                <TrashedTaskItem key={task.id} task={task} onRestoreTask={restoreTask} />
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  );
};

export default ListaDeTarefasContainer;
