import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Source } from '../types';
import { FileText, Upload, Trash2, ExternalLink } from 'lucide-react';

export default function Sources() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [filter, setFilter] = useState('');

  const { data: sources, isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: () => api.get('/sources/').then((res) => res.data),
  });

  const deleteSource = useMutation({
    mutationFn: (id: string) => api.delete(`/sources/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
  });

  const uploadFile = async (file: File) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
  };

  const filteredSources = sources?.filter(
    (s: Source) =>
      !filter || s.source_type === filter
  );

  const sourceTypes = [
    'research_paper',
    'journal',
    'conference_paper',
    'preprint',
    'book',
    'dataset',
    'github_repository',
    'documentation',
    'web_page',
    'institutional_report',
    'patent',
    'researcher_note',
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Sources</h1>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          <Upload className="h-4 w-4 mr-2" />
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt,.md,.html"
          className="hidden"
        />
      </div>

      <div className="mb-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md"
        >
          <option value="">All types</option>
          {sourceTypes.map((type) => (
            <option key={type} value={type}>
              {type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading sources...</div>
      ) : (
        <div className="space-y-4">
          {filteredSources?.map((source: Source) => (
            <div
              key={source.id}
              className="bg-white shadow rounded-lg p-4 flex items-start justify-between"
            >
              <div className="flex items-start gap-3 flex-1">
                <FileText className="h-5 w-5 text-blue-600 mt-1" />
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{source.title}</h3>
                  {source.author && (
                    <p className="text-sm text-gray-500">by {source.author}</p>
                  )}
                  <div className="flex gap-4 mt-1 text-sm text-gray-500">
                    <span className="capitalize">{source.source_type.replace(/_/g, ' ')}</span>
                    {source.doi && <span>DOI: {source.doi}</span>}
                    <span>Quality: {Math.round(source.quality_score * 100)}%</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 ml-4">
                {source.url && (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-gray-400 hover:text-blue-600"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
                <button
                  onClick={() => deleteSource.mutate(source.id)}
                  className="p-2 text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {filteredSources?.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No sources yet. Upload a document or add a source!
            </div>
          )}
        </div>
      )}
    </div>
  );
}
