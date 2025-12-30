'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface ModelContextType {
  selectedModel: string;
  setSelectedModel: (version: string) => void;
}

const ModelContext = createContext<ModelContextType | undefined>(undefined);

export function ModelProvider({ children }: { children: ReactNode }) {
  const [selectedModel, setSelectedModel] = useState('');

  // Persist to localStorage
  useEffect(() => {
    const saved = localStorage.getItem('mlk2_selected_model');
    if (saved) {
      setSelectedModel(saved);
    }
  }, []);

  const handleSetModel = (version: string) => {
    setSelectedModel(version);
    localStorage.setItem('mlk2_selected_model', version);
  };

  return (
    <ModelContext.Provider value={{
      selectedModel,
      setSelectedModel: handleSetModel
    }}>
      {children}
    </ModelContext.Provider>
  );
}

export function useModel() {
  const context = useContext(ModelContext);
  if (!context) {
    throw new Error('useModel must be used within ModelProvider');
  }
  return context;
}