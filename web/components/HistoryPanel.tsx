'use client';

import { useEffect, useState } from 'react';

interface HistoryItem {
  id: string;
  timestamp: string;
  judul: string;
  predicted_kbk: string;
  probabilities: Record<string, number>;
  model_version: string;
}

interface HistoryPanelProps {
  sessionId: string;
  onSelectItem: (item: HistoryItem) => void;
}

export default function HistoryPanel({ sessionId, onSelectItem }: HistoryPanelProps) {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (sessionId && isOpen) {
      fetchHistory();
    }
  }, [sessionId, isOpen]);

  const fetchHistory = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/history/?session_id=${sessionId}`);
      const data = await response.json();
      setHistory(data.history || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!sessionId || !confirm('Clear all history?')) return;
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/history/clear/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      setHistory([]);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const deleteItem = async (historyId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/history/${historyId}/?session_id=${sessionId}`, {
        method: 'DELETE'
      });
      setHistory(history.filter(item => item.id !== historyId));
    } catch (error) {
      console.error('Error deleting history:', error);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('id-ID', { 
      day: '2-digit', 
      month: 'short', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed right-4 top-4 bg-orange-500 text-white px-4 py-2 rounded-xl shadow-lg hover:bg-orange-600 transition-all z-50 flex items-center gap-2"
      >
        📜 History {history.length > 0 && `(${history.length})`}
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">📜 Riwayat Prediksi</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading...</div>
              ) : history.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Belum ada riwayat prediksi
                </div>
              ) : (
                <div className="space-y-3">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="border border-gray-200 rounded-xl p-4 hover:border-orange-300 transition-all cursor-pointer group"
                      onClick={() => {
                        onSelectItem(item);
                        setIsOpen(false);
                      }}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex-1">
                          <p className="text-sm text-gray-500 mb-1">
                            {formatDate(item.timestamp)} • v{item.model_version}
                          </p>
                          <p className="text-gray-900 font-medium line-clamp-2">
                            {item.judul}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteItem(item.id);
                          }}
                          className="text-red-400 hover:text-red-600 ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          🗑️
                        </button>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-semibold">
                          {item.predicted_kbk}
                        </span>
                        <span className="text-sm text-gray-500">
                          {(Object.values(item.probabilities).reduce((a, b) => Math.max(a, b), 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {history.length > 0 && (
              <div className="p-6 border-t border-gray-200">
                <button
                  onClick={clearHistory}
                  className="w-full bg-red-500 text-white py-3 rounded-xl font-semibold hover:bg-red-600 transition-all"
                >
                  🗑️ Hapus Semua Riwayat
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
