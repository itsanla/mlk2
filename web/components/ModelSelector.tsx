import { useEffect, useState } from 'react';
import { useModel } from '@/contexts/ModelContext';

interface Model {
  version: string;
  name: string;
  accuracy: number;
  cv_accuracy: number;
  created_at: string;
}

interface ModelSelectorProps {
  value: string;
  onChange: (version: string) => void;
}

export default function ModelSelector({ value, onChange }: ModelSelectorProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const { setSelectedModel } = useModel();

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/models/`);
      const data = await response.json();
      setModels(data.models || []);
      if (data.latest && !value) {
        onChange(data.latest);
        setSelectedModel(data.latest);
      }
    } catch (error) {
      console.error('Error fetching models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (version: string) => {
    onChange(version);
    setSelectedModel(version);
  };

  if (loading) {
    return (
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          🤖 Model Version
        </label>
        <div className="w-full p-3 border-2 border-gray-200 rounded-xl bg-gray-50 text-gray-400">
          Loading models...
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        🤖 Model Version
      </label>
      <select
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full p-3 border-2 border-orange-200 rounded-xl focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-all text-gray-900 bg-white"
      >
        {models.map((model) => (
          <option key={model.version} value={model.version}>
            v{model.version} - {model.name} (Acc: {(model.cv_accuracy * 100).toFixed(1)}%)
          </option>
        ))}
      </select>
    </div>
  );
}
