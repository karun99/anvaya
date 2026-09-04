import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { Brain, FileText, BookOpen, Zap, Activity } from 'lucide-react';

export default function Dashboard() {
  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => api.get('/analytics/').then((res) => res.data),
  });

  const { data: energyStatus } = useQuery({
    queryKey: ['energy'],
    queryFn: () => api.get('/energy/status').then((res) => res.data),
  });

  const stats = [
    {
      name: 'Research Memory',
      value: analytics?.total_memories || 0,
      icon: Brain,
      color: 'bg-purple-500',
    },
    {
      name: 'Sources',
      value: analytics?.total_sources || 0,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'Documents',
      value: analytics?.total_documents || 0,
      icon: BookOpen,
      color: 'bg-green-500',
    },
    {
      name: 'Energy Mode',
      value: energyStatus?.mode || 'BALANCED',
      icon: Zap,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.name}
              className="bg-white overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 rounded-md p-3 ${stat.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-lg font-semibold text-gray-900">
                        {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <a
            href="/research"
            className="block p-4 border border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50"
          >
            <Activity className="h-6 w-6 text-indigo-600 mb-2" />
            <h3 className="font-medium text-gray-900">Start Research</h3>
            <p className="text-sm text-gray-500">Ask a research question</p>
          </a>
          <a
            href="/sources"
            className="block p-4 border border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50"
          >
            <FileText className="h-6 w-6 text-indigo-600 mb-2" />
            <h3 className="font-medium text-gray-900">Add Source</h3>
            <p className="text-sm text-gray-500">Import papers or URLs</p>
          </a>
          <a
            href="/memory"
            className="block p-4 border border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50"
          >
            <Brain className="h-6 w-6 text-indigo-600 mb-2" />
            <h3 className="font-medium text-gray-900">View Memory</h3>
            <p className="text-sm text-gray-500">Explore your research memory</p>
          </a>
        </div>
      </div>
    </div>
  );
}
