import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { EnergyStatus } from '../types';
import { Settings as SettingsIcon, Cpu, Zap, Shield, Database } from 'lucide-react';

export default function Settings() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('energy');

  const { data: energyStatus } = useQuery({
    queryKey: ['energy'],
    queryFn: () => api.get('/energy/status').then((res) => res.data),
  });

  const updateEnergyMode = useMutation({
    mutationFn: (mode: string) => api.put('/energy/mode', { mode }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['energy'] });
    },
  });

  const { data: systemConfig } = useQuery({
    queryKey: ['system'],
    queryFn: () => api.get('/system/config').then((res) => res.data),
  });

  const tabs = [
    { id: 'energy', name: 'Energy', icon: Zap },
    { id: 'models', name: 'Models', icon: Cpu },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'data', name: 'Data', icon: Database },
  ];

  const energyModes = [
    { id: 'PERFORMANCE', name: 'Performance', description: 'Maximum speed and quality' },
    { id: 'BALANCED', name: 'Balanced', description: 'Good balance of speed and quality' },
    { id: 'ENERGY_SAVER', name: 'Energy Saver', description: 'Reduced compute, reuse cached results' },
    { id: 'LOCAL_FIRST', name: 'Local First', description: 'Prefer local inference' },
    { id: 'OFFLINE', name: 'Offline', description: 'No external network operations' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      <div className="flex gap-6">
        <nav className="w-48">
          <div className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === tab.id
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.name}
                </button>
              );
            })}
          </div>
        </nav>

        <div className="flex-1">
          {activeTab === 'energy' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Energy Mode</h2>
              <div className="space-y-3">
                {energyModes.map((mode) => (
                  <label
                    key={mode.id}
                    className={`block p-4 border rounded-lg cursor-pointer ${
                      energyStatus?.mode === mode.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="energy-mode"
                        checked={energyStatus?.mode === mode.id}
                        onChange={() => updateEnergyMode.mutate(mode.id)}
                        className="h-4 w-4 text-indigo-600"
                      />
                      <div className="ml-3">
                        <p className="font-medium text-gray-900">{mode.name}</p>
                        <p className="text-sm text-gray-500">{mode.description}</p>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
              {energyStatus && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-700 mb-2">Usage Statistics</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">LLM Requests</p>
                      <p className="font-medium">{energyStatus.llm_requests}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Cache Hits</p>
                      <p className="font-medium">{energyStatus.cache_hits}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Estimated Footprint</p>
                      <p className="font-medium">{energyStatus.estimated_footprint}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'models' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Model Configuration</h2>
              <p className="text-gray-500">Configure AI models for different tasks.</p>
              <div className="mt-4 space-y-4">
                {['Chat', 'Embedding', 'Summarization', 'Analysis'].map((task) => (
                  <div key={task} className="flex items-center gap-4 p-3 bg-gray-50 rounded-md">
                    <span className="w-32 font-medium text-gray-700">{task}</span>
                    <select className="flex-1 px-3 py-2 border border-gray-300 rounded-md">
                      <option>Select model...</option>
                      <option>GPT-4</option>
                      <option>GPT-3.5 Turbo</option>
                      <option>Claude 3</option>
                      <option>Local Model</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h2>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-700">Data Encryption</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Sensitive research data is encrypted at rest.
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-700">API Access</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Manage API keys and access tokens.
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-700">Audit Logs</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    View system activity and access logs.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Data Management</h2>
              <div className="space-y-4">
                <button className="w-full text-left p-4 bg-gray-50 rounded-lg hover:bg-gray-100">
                  <h3 className="font-medium text-gray-700">Export Research Memory</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Export your memories, sources, and profile as JSON.
                  </p>
                </button>
                <button className="w-full text-left p-4 bg-gray-50 rounded-lg hover:bg-gray-100">
                  <h3 className="font-medium text-gray-700">Import Data</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Import from Markdown, JSON, CSV, or URLs.
                  </p>
                </button>
                <button className="w-full text-left p-4 bg-red-50 rounded-lg hover:bg-red-100 border border-red-200">
                  <h3 className="font-medium text-red-700">Delete All Data</h3>
                  <p className="text-sm text-red-500 mt-1">
                    Permanently delete all research data. This cannot be undone.
                  </p>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
