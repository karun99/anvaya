import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '../api/client';
import { SearchResult } from '../types';
import { Search as SearchIcon, ExternalLink, Bookmark } from 'lucide-react';

export default function Search() {
  const [query, setQuery] = useState('');
  const [limit, setLimit] = useState(10);

  const searchMutation = useMutation({
    mutationFn: (data: { query: string; limit: number }) =>
      api.post('/search/', data).then((res) => res.data),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchMutation.mutate({ query, limit });
    }
  };

  const saveAsMemory = async (result: SearchResult) => {
    await api.post('/memory/', {
      type: 'source',
      content: `${result.title} - ${result.snippet || ''}`,
      metadata: { url: result.url, source_type: result.source_type },
    });
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Search</h1>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search your research sources..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value={5}>5 results</option>
            <option value={10}>10 results</option>
            <option value={20}>20 results</option>
          </select>
          <button
            type="submit"
            disabled={searchMutation.isPending}
            className="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {searchMutation.isPending ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {searchMutation.isError && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md">
          Search failed. Please try again.
        </div>
      )}

      {searchMutation.data && (
        <div>
          <p className="text-sm text-gray-500 mb-4">
            Found {searchMutation.data.count} results
          </p>
          <div className="space-y-4">
            {searchMutation.data.sources.map((result: SearchResult, index: number) => (
              <div
                key={index}
                className="bg-white shadow rounded-lg p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{result.title}</h3>
                    {result.author && (
                      <p className="text-sm text-gray-500">by {result.author}</p>
                    )}
                    <p className="text-sm text-gray-500 capitalize">
                      {result.source_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      Relevance: {Math.round(result.score * 100)}%
                    </p>
                  </div>
                  <div className="flex gap-2 ml-4">
                    {result.url && (
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-400 hover:text-blue-600"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                    <button
                      onClick={() => saveAsMemory(result)}
                      className="p-2 text-gray-400 hover:text-green-600"
                      title="Save to memory"
                    >
                      <Bookmark className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
