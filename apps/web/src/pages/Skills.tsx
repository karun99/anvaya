import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { Skill } from '../types';
import { Zap, Play, Settings } from 'lucide-react';

export default function Skills() {
  const { data: skills, isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: () => api.get('/skills/').then((res) => res.data),
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Skills</h1>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          Create Skill
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading skills...</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {skills?.map((skill: Skill) => (
            <div
              key={skill.id}
              className="bg-white shadow rounded-lg p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`p-2 rounded-lg ${skill.is_builtin ? 'bg-indigo-100' : 'bg-gray-100'}`}>
                  <Zap className={`h-5 w-5 ${skill.is_builtin ? 'text-indigo-600' : 'text-gray-600'}`} />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{skill.name}</h3>
                  <p className="text-xs text-gray-500">
                    {skill.is_builtin ? 'Built-in' : 'Custom'}
                  </p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">{skill.description}</p>
              <div className="flex gap-2">
                <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                  <Play className="h-3 w-3" /> Run
                </button>
                {!skill.is_builtin && (
                  <button className="flex items-center gap-1 px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                    <Settings className="h-3 w-3" /> Edit
                  </button>
                )}
              </div>
            </div>
          ))}
          {skills?.length === 0 && (
            <div className="col-span-full text-center py-8 text-gray-500">
              No skills available.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
