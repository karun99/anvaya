import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '../api/client';
import { ResearchResponse } from '../types';
import { BookOpen, ExternalLink, Bookmark } from 'lucide-react';

export default function Research() {
  const [question, setQuestion] = useState('');
  const [useMemory, setUseMemory] = useState(true);

  const researchMutation = useMutation({
    mutationFn: (data: { question: string; use_memory: boolean }) =>
      api.post('/research/', data).then((res) => res.data),
  });

  const handleResearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      researchMutation.mutate({ question, use_memory: useMemory });
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Research</h1>

      <form onSubmit={handleResearch} className="mb-6">
        <div className="bg-white shadow rounded-lg p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Research Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What would you like to research?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          <div className="mt-4 flex items-center gap-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={useMemory}
                onChange={(e) => setUseMemory(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">
                Use research memory for context
              </span>
            </label>
            <button
              type="submit"
              disabled={researchMutation.isPending}
              className="ml-auto px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {researchMutation.isPending ? 'Researching...' : 'Research'}
            </button>
          </div>
        </div>
      </form>

      {researchMutation.isError && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md">
          Research failed. Please try again.
        </div>
      )}

      {researchMutation.data && (
        <ResearchResult result={researchMutation.data} />
      )}
    </div>
  );
}

function ResearchResult({ result }: { result: ResearchResponse }) {
  const saveFinding = async (source: any) => {
    await api.post('/memory/', {
      type: 'insight',
      content: `${source.title}`,
      metadata: { url: source.url, question: result.question },
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Question: {result.question}
        </h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 whitespace-pre-wrap">{result.answer}</p>
        </div>
        <div className="mt-4 text-sm text-gray-500">
          Confidence: {Math.round(result.confidence * 100)}%
        </div>
      </div>

      {result.evidence && result.evidence.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Evidence</h3>
          <div className="space-y-3">
            {result.evidence.map((item: any, index: number) => (
              <div key={index} className="p-3 bg-gray-50 rounded-md">
                <p className="font-medium text-gray-700">{item.source}</p>
                <p className="text-sm text-gray-500">{item.content}</p>
                <p className="text-sm text-gray-500">
                  Relevance: {Math.round(item.relevance * 100)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.sources && result.sources.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sources</h3>
          <div className="space-y-3">
            {result.sources.map((source: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center gap-3">
                  <BookOpen className="h-5 w-5 text-indigo-600" />
                  <div>
                    <p className="font-medium text-gray-700">{source.title}</p>
                    {source.url && (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" /> View source
                      </a>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => saveFinding(source)}
                  className="p-2 text-gray-400 hover:text-green-600"
                  title="Save to memory"
                >
                  <Bookmark className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
