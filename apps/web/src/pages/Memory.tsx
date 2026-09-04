import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Memory } from '../types';
import { Brain, Plus, Trash2, Edit, Check } from 'lucide-react';

export default function Memory() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [newType, setNewType] = useState('note');
  const [newContent, setNewContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: memories, isLoading } = useQuery({
    queryKey: ['memories'],
    queryFn: () => api.get('/memory/').then((res) => res.data),
  });

  const addMemory = useMutation({
    mutationFn: (data: { type: string; content: string }) =>
      api.post('/memory/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
      setShowAdd(false);
      setNewContent('');
    },
  });

  const deleteMemory = useMutation({
    mutationFn: (id: string) => api.delete(`/memory/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
    },
  });

  const searchMemories = useQuery({
    queryKey: ['memories', 'search', searchQuery],
    queryFn: () =>
      api.post('/memory/search', null, { params: { query: searchQuery } }).then((res) => res.data),
    enabled: searchQuery.length > 0,
  });

  const memoryTypes = [
    'interest',
    'project',
    'question',
    'note',
    'source',
    'paper',
    'concept',
    'method',
    'dataset',
    'code',
    'decision',
    'insight',
    'feedback',
  ];

  const displayedMemories = searchQuery ? searchMemories.data?.memories : memories;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Research Memory</h1>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Memory
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      {showAdd && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex gap-4 mb-4">
            <select
              value={newType}
              onChange={(e) => setNewType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            >
              {memoryTypes.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Enter memory content..."
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              onClick={() => addMemory.mutate({ type: newType, content: newContent })}
              disabled={!newContent.trim()}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              Save
            </button>
            <button
              onClick={() => setShowAdd(false)}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-8">Loading memories...</div>
      ) : (
        <div className="space-y-4">
          {displayedMemories?.map((memory: Memory) => (
            <div
              key={memory.id}
              className="bg-white shadow rounded-lg p-4 flex items-start justify-between"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="h-4 w-4 text-purple-600" />
                  <span className="text-sm font-medium text-purple-600">
                    {memory.type}
                  </span>
                  <span className="text-sm text-gray-500">
                    • {new Date(memory.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-700">{memory.content}</p>
                <div className="mt-2 flex gap-4 text-sm text-gray-500">
                  <span>Confidence: {Math.round(memory.confidence * 100)}%</span>
                  <span>Importance: {Math.round(memory.importance * 100)}%</span>
                  {memory.user_verified && (
                    <span className="text-green-600 flex items-center gap-1">
                      <Check className="h-3 w-3" /> Verified
                    </span>
                  )}
                </div>
              </div>
              <div className="flex gap-2 ml-4">
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => deleteMemory.mutate(memory.id)}
                  className="p-2 text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {displayedMemories?.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No memories yet. Start adding research context!
            </div>
          )}
        </div>
      )}
    </div>
  );
}
