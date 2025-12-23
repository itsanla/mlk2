'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

interface AnalysisData {
  model_type: string;
  total_samples: number;
  classes: string[];
  class_distribution: Record<string, number>;
  performance: {
    train_accuracy: number;
    cv_mean_accuracy: number;
    cv_std_accuracy: number;
  };
  model_health: {
    overfitting_status: string;
    overfitting_score: number;
    underfitting_status: string;
    bias: number;
    variance: number;
  };
  model_parameters: {
    n_features: number;
    alpha: number;
  };
  naive_bayes_specific: {
    conditional_independence: {
      status: string;
      violation_ratio: number;
    };
    class_overlap: {
      avg_confidence: number;
      low_confidence_samples: number;
    };
  };
  class_overlap: {
    avg_confidence: number;
    avg_confidence_gap: number;
    low_confidence_samples: number;
    high_overlap_samples: number;
  };
  learning_curve?: Array<{
    complexity: number;
    training: number;
    validation: number;
  }>;
}

export default function OverviewPage() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/analyze/`);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error:', error);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading) return <div className="text-center py-20">Loading...</div>;
  if (!data || !data.performance) return <div className="text-center py-20 text-red-600">Failed to load data</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-6">
        {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard title="Total Samples" value={data.total_samples} icon="📝" />
        <MetricCard title="Train Accuracy" value={`${(data.performance.train_accuracy * 100).toFixed(1)}%`} icon="🎯" status={data.model_health.overfitting_status} />
        <MetricCard title="CV Accuracy" value={`${(data.performance.cv_mean_accuracy * 100).toFixed(1)}%`} icon="✅" />
        <MetricCard title="Features" value={data.model_parameters.n_features} icon="🔤" />
      </div>

      {/* Model Health */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">🏥 Model Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <HealthCard 
            title="Overfitting" 
            value={data.model_health.overfitting_status}
            score={`${(data.model_health.overfitting_score * 100).toFixed(1)}%`}
            color={data.model_health.overfitting_status === 'High' ? 'red' : data.model_health.overfitting_status === 'Moderate' ? 'yellow' : 'green'}
          />
          <HealthCard 
            title="Underfitting" 
            value={data.model_health.underfitting_status}
            score={`Bias: ${(data.model_health.bias * 100).toFixed(1)}%`}
            color={data.model_health.underfitting_status === 'High' ? 'red' : data.model_health.underfitting_status === 'Moderate' ? 'yellow' : 'green'}
          />
          <HealthCard 
            title="Independence Violation" 
            value={data.naive_bayes_specific.conditional_independence.status}
            score={`${(data.naive_bayes_specific.conditional_independence.violation_ratio * 100).toFixed(2)}%`}
            color={data.naive_bayes_specific.conditional_independence.status.includes('High') ? 'red' : data.naive_bayes_specific.conditional_independence.status === 'Moderate' ? 'yellow' : 'green'}
          />
        </div>
        
        {/* Line Chart */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">📈 Learning Curve: Training vs Validation</h3>
          {data.learning_curve && data.learning_curve.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={data.learning_curve}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="complexity" 
                  label={{ value: 'Model Complexity (Features)', position: 'insideBottom', offset: -5 }} 
                />
                <YAxis 
                  label={{ value: 'Performance (%)', angle: -90, position: 'insideLeft' }} 
                  domain={[0, 100]}
                />
                <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="training" 
                  stroke="#ef4444" 
                  strokeWidth={3} 
                  name="Training Accuracy" 
                  dot={{ r: 5 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="validation" 
                  stroke="#3b82f6" 
                  strokeWidth={3} 
                  name="Validation Accuracy" 
                  dot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500">Loading learning curve...</p>
          )}
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span>Training: Higher = Overfitting risk</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span>Validation: Higher = Better generalization</span>
            </div>
          </div>
        </div>
      </div>

      {/* Class Distribution */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">📊 Class Distribution</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(data.class_distribution).map(([cls, count]) => (
            <div key={cls} className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-lg p-4 border-2 border-orange-200">
              <p className="text-sm text-gray-600 mb-1">{cls}</p>
              <p className="text-3xl font-bold text-orange-600">{count}</p>
              <p className="text-xs text-gray-500 mt-1">{((count / data.total_samples) * 100).toFixed(1)}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Model Parameters */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">⚙️ Model Parameters</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <ParamCard label="Alpha (Smoothing)" value={data.model_parameters.alpha} />
          <ParamCard label="Features" value={data.model_parameters.n_features} />
          <ParamCard label="Classes" value={data.classes.length} />
          <ParamCard label="Variance" value={data.model_health.variance.toFixed(4)} />
          <ParamCard label="Avg Confidence" value={`${(data.class_overlap.avg_confidence * 100).toFixed(1)}%`} />
          <ParamCard label="Low Confidence" value={data.class_overlap.low_confidence_samples} />
        </div>
      </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, status }: { title: string; value: string | number; icon: string; status?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
        {status && (
          <span className={`text-xs px-2 py-1 rounded-full ${
            status === 'High' ? 'bg-red-100 text-red-700' : 
            status === 'Moderate' ? 'bg-yellow-100 text-yellow-700' : 
            'bg-green-100 text-green-700'
          }`}>
            {status}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600">{title}</p>
      <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function HealthCard({ title, value, score, color }: { title: string; value: string; score: string; color: 'red' | 'yellow' | 'green' }) {
  const colors = {
    red: 'bg-red-50 border-red-300 text-red-700',
    yellow: 'bg-yellow-50 border-yellow-300 text-yellow-700',
    green: 'bg-green-50 border-green-300 text-green-700'
  };
  
  return (
    <div className={`rounded-xl p-6 border-2 ${colors[color]}`}>
      <p className="text-sm font-semibold mb-2">{title}</p>
      <p className="text-2xl font-bold mb-1">{value}</p>
      <p className="text-sm">{score}</p>
    </div>
  );
}

function ParamCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
