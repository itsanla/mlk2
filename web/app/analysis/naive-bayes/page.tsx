'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const VChart = dynamic(() => import('@visactor/react-vchart').then(mod => mod.VChart), { ssr: false });

interface AnalysisData {
  naive_bayes_specific: {
    class_priors: Record<string, number>;
    prediction_confidence_distribution: Record<string, number>;
    misclassification_patterns: Record<string, number>;
    zero_probability_features: Record<string, { count: number; percentage: number }>;
    class_separability_kl_divergence: Record<string, number>;
  };
}

export default function NaiveBayesPage() {
  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/analyze/`);
      const result = await response.json();
      setData(result);
    };
    fetchData();
  }, []);

  if (!data || !data.naive_bayes_specific) return <div className="p-8">Loading...</div>;

  const priorsData = Object.entries(data.naive_bayes_specific.class_priors).map(([name, value]) => ({
    class: name,
    prior: value
  }));

  const confidenceData = Object.entries(data.naive_bayes_specific.prediction_confidence_distribution).map(([range, count]) => ({
    range,
    count
  }));

  const misclassData = Object.entries(data.naive_bayes_specific.misclassification_patterns)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([pattern, count]) => ({ pattern: pattern.replace(/_/g, ' '), count }));

  const zeroFeaturesData = Object.entries(data.naive_bayes_specific.zero_probability_features).map(([cls, data]) => ({
    class: cls,
    percentage: data.percentage
  }));

  const klData = Object.entries(data.naive_bayes_specific.class_separability_kl_divergence).map(([pair, value]) => ({
    pair: pair.replace(/_vs_/g, ' vs '),
    divergence: value
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold mb-6">Naive Bayes Analysis</h1>
      
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Class Priors P(class)</h2>
              <VChart
                spec={{
                  type: 'pie',
                  data: [{ values: priorsData }],
                  outerRadius: 0.8,
                  innerRadius: 0.5,
                  categoryField: 'class',
                  valueField: 'prior',
                  legends: { visible: true, orient: 'bottom' },
                  label: { visible: true }
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Prediction Confidence Distribution</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: confidenceData }],
                  xField: 'range',
                  yField: 'count',
                  bar: { style: { fill: '#60C2FB' } },
                  axes: [
                    { orient: 'left', title: { text: 'Count' } },
                    { orient: 'bottom', label: { autoRotate: true } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Zero Probability Features (%)</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: zeroFeaturesData }],
                  xField: 'class',
                  yField: 'percentage',
                  bar: { style: { fill: '#f59e0b' } },
                  axes: [
                    { orient: 'left', title: { text: 'Percentage (%)' } },
                    { orient: 'bottom', label: { autoRotate: true } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Class Separability (KL Divergence)</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: klData }],
                  xField: 'pair',
                  yField: 'divergence',
                  bar: { style: { fill: '#8b5cf6' } },
                  axes: [
                    { orient: 'left', title: { text: 'KL Divergence' } },
                    { orient: 'bottom', label: { autoRotate: true, autoRotateAngle: [45] } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>
          </div>
        </div>

        {misclassData.length > 0 ? (
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Top 10 Misclassification Patterns</h2>
            <VChart
              spec={{
                type: 'bar',
                data: [{ values: misclassData }],
                yField: 'pattern',
                xField: 'count',
                direction: 'horizontal',
                bar: { style: { fill: '#ef4444' } },
                axes: [
                  { orient: 'bottom', title: { text: 'Count' } },
                  { orient: 'left' }
                ]
              }}
              style={{ height: '400px', width: '100%' }}
            />
          </div>
        ) : (
          <div className="bg-card rounded-lg border border-border p-6">
            <h2 className="text-xl font-semibold mb-4">Top 10 Misclassification Patterns</h2>
            <p className="text-center text-muted-foreground py-8">No misclassification data available</p>
          </div>
        )}
      </div>
      </div>
    </div>
  );
}
