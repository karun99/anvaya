import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { ResearcherProfile } from '../types';

export default function Profile() {
  const queryClient = useQueryClient();
  const [interests, setInterests] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);
  const [researchGoals, setResearchGoals] = useState<string[]>([]);
  const [newInterest, setNewInterest] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [newGoal, setNewGoal] = useState('');

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/researcher/profile').then((res) => res.data),
  });

  useEffect(() => {
    if (profile) {
      setInterests(profile.interests || []);
      setSkills(profile.skills || []);
      setResearchGoals(profile.research_goals || []);
    }
  }, [profile]);

  const updateProfile = useMutation({
    mutationFn: (data: Partial<ResearcherProfile>) =>
      api.put('/researcher/profile', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  const addItem = (
    type: 'interests' | 'skills' | 'research_goals',
    value: string,
    setter: (items: string[]) => void,
    items: string[]
  ) => {
    if (value.trim() && !items.includes(value.trim())) {
      const newItems = [...items, value.trim()];
      setter(newItems);
      updateProfile.mutate({ [type]: newItems });
    }
  };

  const removeItem = (
    type: 'interests' | 'skills' | 'research_goals',
    index: number,
    setter: (items: string[]) => void,
    items: string[]
  ) => {
    const newItems = items.filter((_, i) => i !== index);
    setter(newItems);
    updateProfile.mutate({ [type]: newItems });
  };

  const renderList = (
    title: string,
    items: string[],
    setter: (items: string[]) => void,
    type: 'interests' | 'skills' | 'research_goals',
    newItem: string,
    setNewItem: (value: string) => void
  ) => (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              addItem(type, newItem, setter, items);
              setNewItem('');
            }
          }}
          placeholder={`Add ${title.toLowerCase().slice(0, -1)}...`}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
        <button
          onClick={() => {
            addItem(type, newItem, setter, items);
            setNewItem('');
          }}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Add
        </button>
      </div>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
          >
            <span className="text-gray-700">{item}</span>
            <button
              onClick={() => removeItem(type, index, setter, items)}
              className="text-red-600 hover:text-red-800"
            >
              Remove
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-gray-500 text-sm">No items added yet.</p>
        )}
      </div>
    </div>
  );

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Researcher Profile</h1>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {renderList(
          'Research Interests',
          interests,
          setInterests,
          'interests',
          newInterest,
          setNewInterest
        )}
        {renderList(
          'Skills',
          skills,
          setSkills,
          'skills',
          newSkill,
          setNewSkill
        )}
        {renderList(
          'Research Goals',
          researchGoals,
          setResearchGoals,
          'research_goals',
          newGoal,
          setNewGoal
        )}
      </div>
    </div>
  );
}
