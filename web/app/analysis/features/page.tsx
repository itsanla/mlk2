'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

const VChart = dynamic(() => import('@visactor/react-vchart').then(mod => mod.VChart), { ssr: false });

interface AnalysisData {
  top_features_per_class: Record<string, string[]>;
  naive_bayes_specific: {
    tfidf_vectorizer_stats: {
      vocabulary_size: number;
      avg_document_length: number;
      sparsity: number;
      max_features: number;
      ngram_range: number[];
      min_df: number;
      max_df: number;
    };
    feature_log_probabilities: Record<string, { mean: number; std: number; min: number; max: number }>;
    feature_counts_per_class: Record<string, number>;
  };
}

export default function FeaturesPage() {
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

  const featureCountsData = Object.entries(data.naive_bayes_specific.feature_counts_per_class).map(([cls, count]) => ({
    class: cls,
    count
  }));

  const logProbData = Object.entries(data.naive_bayes_specific.feature_log_probabilities).flatMap(([cls, stats]) => [
    { class: cls, stat: 'Mean', value: stats.mean },
    { class: cls, stat: 'Std', value: stats.std }
  ]);

  const tfidfStats = data.naive_bayes_specific.tfidf_vectorizer_stats;

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-6">
        <h1 className="text-3xl font-bold mb-6">Features Analysis</h1>
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Vocabulary Size</div>
              <div className="text-3xl font-bold text-gray-900">{tfidfStats.vocabulary_size}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Avg Document Length</div>
              <div className="text-3xl font-bold text-gray-900">{tfidfStats.avg_document_length.toFixed(2)}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-2">Sparsity</div>
              <div className="text-3xl font-bold text-gray-900">{(tfidfStats.sparsity * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Feature Counts per Class</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: featureCountsData }],
                  xField: 'class',
                  yField: 'count',
                  bar: { style: { fill: '#10b981' } },
                  axes: [
                    { orient: 'left', title: { text: 'Count' } },
                    { orient: 'bottom', label: { autoRotate: true } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">Feature Log Probabilities</h2>
              <VChart
                spec={{
                  type: 'bar',
                  data: [{ values: logProbData }],
                  xField: 'class',
                  yField: 'value',
                  seriesField: 'stat',
                  legends: { visible: true, orient: 'bottom' },
                  axes: [
                    { orient: 'left', title: { text: 'Value' } },
                    { orient: 'bottom', label: { autoRotate: true } }
                  ]
                }}
                style={{ height: '250px', width: '100%' }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Top 5 Features per Class</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(data.top_features_per_class).map(([cls, features]) => (
              <div key={cls} className="bg-muted rounded-lg p-4">
                <h3 className="font-semibold mb-2 text-sm">{cls}</h3>
                <ol className="text-xs space-y-1">
                  {features.slice(0, 5).map((feature, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-muted-foreground">{i + 1}.</span>
                      <span className="font-mono">{feature}</span>
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}
