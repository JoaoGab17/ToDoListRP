// src/ListaDeTarefas.jsx (Versão Final com Lixeira)
import React, { useState, useEffect } from 'react';

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
      <input type="text" placeholder="O que precisa ser feito?" value={inputValue} onChange={(e) => setInputValue(e.target.value)} className="task-input" />
      <button type="submit" className="add-button">Adicionar</button>
    </form>
  );
};

const TaskItem = ({ task, onUpdateStatus, onMoveToTrash }) => {
  const itemClassName = `task-item ${task.status === 'concluída' ? 'completed' : ''}`;
  return (
    <li className={itemClassName}>
      <span className="task-item-text">{`[${task.id}] ${task.titulo}`}</span>
      <div className="task-item-actions">
        <select className="status-select" value={task.status} onChange={(e) => onUpdateStatus(task.id, e.target.value)}>
          <option value="pendente">Pendente</option>
          <option value="fazendo">Fazendo</option>
          <option value="concluída">Concluída</option>
        </select>
        <button onClick={() => onMoveToTrash(task.id)} className="remove-button" title="Mover para Lixeira">🗑️</button>
      </div>
    </li>
  );
};

// NOVO COMPONENTE para itens na lixeira
const TrashedTaskItem = ({ task, onRestoreTask }) => {
  return (
    <li className="task-item">
      <span className="task-item-text completed">{`[${task.id}] ${task.titulo}`}</span>
      <div className="task-item-actions">
        <button onClick={() => onRestoreTask(task.id)} className="toggle-button" title="Restaurar Tarefa">♻️</button>
      </div>
    </li>
  );
};

// --- Componente Principal ---
const ListaDeTarefasContainer = () => {
  // MUDANÇA 1: Agora temos 3 estados principais
  const [tasks, setTasks] = useState([]);
  const [trashedTasks, setTrashedTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('active'); // 'active' ou 'trashed'
  const [loading, setLoading] = useState(true);

  // MUDANÇA 2: Função de busca agora pega TUDO da API
  const fetchAllData = async () => {
    setLoading(true);
    try {
      // Usamos Promise.all para fazer as duas requisições em paralelo
      const [activeRes, trashedRes] = await Promise.all([
        fetch(`${API_URL}/tarefas`),
        fetch(`${API_URL}/tarefas/excluidas`)
      ]);
      if (!activeRes.ok || !trashedRes.ok) throw new Error("Falha em uma das requisições de API.");
      
      const activeData = await activeRes.json();
      const trashedData = await trashedRes.json();
      
      setTasks(activeData);
      setTrashedTasks(trashedData);
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      alert("Não foi possível carregar os dados. Verifique a conexão com a API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // MUDANÇA 3: Todas as ações agora chamam fetchAllData para garantir a sincronia
  const addTask = async (text) => {
    await fetch(`${API_URL}/tarefas`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
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
    await fetch(`${API_URL}/tarefas/${id}/status`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: newStatus }) });
    fetchAllData();
  };
  
  return (
    <div className="app-container">
      <h1>To-Do List Full-Stack</h1>
      <TaskForm onAddTask={addTask} />

      {/* MUDANÇA 4: Adicionado o container das abas */}
      <div className="tabs-container">
        <button className={`tab-button ${activeTab === 'active' ? 'active' : ''}`} onClick={() => setActiveTab('active')}>
          Tarefas Ativas ({tasks.length})
        </button>
        <button className={`tab-button ${activeTab === 'trashed' ? 'active' : ''}`} onClick={() => setActiveTab('trashed')}>
          Lixeira ({trashedTasks.length})
        </button>
      </div>

      <div className="tab-content">
        {loading ? <p style={{textAlign: 'center'}}>Carregando...</p> : (
          // MUDANÇA 5: Renderização condicional baseada na aba ativa
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
