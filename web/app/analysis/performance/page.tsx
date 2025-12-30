'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useModel } from '@/contexts/ModelContext';

const VChart = dynamic(() => import('@visactor/react-vchart').then(mod => mod.VChart), { ssr: false });

interface AnalysisData {
  performance: {
    train_accuracy: number;
    cv_mean_accuracy: number;
    cv_scores: number[];
  };
  per_class_metrics: Record<string, { precision: number; recall: number; f1_score: number; support: number }>;
  confusion_matrix: {
    cross_validation: number[][];
    labels: string[];
  };
}

export default function PerformancePage() {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const { selectedModel } = useModel();

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedModel) {
        setLoading(false);
        return;
      }
      
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/analyze/?model_version=${selectedModel}`);
        const result = await response.json();
        
        if (!result.error && result.performance) {
          setData(result);
        }
      } catch (error) {
        console.error('Error:', error);
      }
      setLoading(false);
    };
    fetchData();
  }, [selectedModel]);

  if (loading) return <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50"><div className="max-w-5xl mx-auto px-4 py-12"><div className="text-center py-20">Loading performance data...</div></div></div>;
  
  if (!selectedModel) return <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50"><div className="max-w-5xl mx-auto px-4 py-12"><div className="text-center py-20 text-gray-500">Please select a model version from the home page</div></div></div>;
  
  if (!data || !data.performance) return <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50"><div className="max-w-5xl mx-auto px-4 py-12"><div className="text-center py-20 text-gray-500">Performance analysis not available for v{selectedModel}</div></div></div>;

  const cvScoresData = data.performance.cv_scores.map((score, i) => ({
    fold: `Fold ${i + 1}`,
    accuracy: score
  }));

  const perClassData = Object.entries(data.per_class_metrics).flatMap(([name, metrics]) => [
    { class: name, metric: 'Precision', value: metrics.precision },
    { class: name, metric: 'Recall', value: metrics.recall },
    { class: name, metric: 'F1-Score', value: metrics.f1_score }
  ]);

  const confusionData = data.confusion_matrix.cross_validation.flatMap((row, i) =>
    row.map((value, j) => ({
      true: data.confusion_matrix.labels[i],
      predicted: data.confusion_matrix.labels[j],
      value
    }))
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold mb-6">Performance Analysis</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Cross-Validation Scores</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: cvScoresData }],
                  xField: 'fold',
                  yField: 'accuracy',
                  axes: [
                    { orient: 'left', title: { text: 'Accuracy' }, min: 0, max: 1 },
                    { orient: 'bottom', title: { text: 'Fold' } }
                  ],
                  bar: { style: { fill: '#3161F8' } }
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Per-Class Metrics</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: perClassData }],
                  xField: 'class',
                  yField: 'value',
                  seriesField: 'metric',
                  legends: { visible: true, orient: 'bottom' },
                  axes: [
                    { orient: 'left', title: { text: 'Score' }, min: 0, max: 1 },
                    { orient: 'bottom', label: { autoRotate: true } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Confusion Matrix (Cross-Validation)</h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="border p-2 bg-muted"></th>
                  {data.confusion_matrix.labels.map(label => (
                    <th key={label} className="border p-2 bg-muted text-sm">{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.confusion_matrix.cross_validation.map((row, i) => (
                  <tr key={i}>
                    <th className="border p-2 bg-muted text-sm">{data.confusion_matrix.labels[i]}</th>
                    {row.map((value, j) => {
                      const maxVal = Math.max(...data.confusion_matrix.cross_validation.flat());
                      const intensity = value / maxVal;
                      return (
                        <td
                          key={j}
                          className="border p-4 text-center font-bold"
                          style={{
                            backgroundColor: `rgba(30, 64, 175, ${intensity})`,
                            color: intensity > 0.5 ? 'white' : 'black'
                          }}
                        >
                          {value}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-sm text-muted-foreground">
            <p>Rows: True Label | Columns: Predicted Label</p>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
