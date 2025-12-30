'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import ModelSelector from '@/components/ModelSelector';
import HistoryPanel from '@/components/HistoryPanel';
import { useSession } from '@/hooks/useSession';

export default function Home() {
  const [judul, setJudul] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(true);
  const [modelVersion, setModelVersion] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const resultRef = useRef<HTMLDivElement>(null);
  const sessionId = useSession();

  const teamMembers = [
    {
      role: 'Project Manager',
      name: 'Agel Deska Wisamulya (2311082002)',
      description: 'Bertanggung jawab dalam perencanaan, koordinasi tim, Mengelola Pembuatan Jurnal dan memastikan proyek berjalan sesuai timeline.',
      icon: '📋'
    },
    {
      role: 'Data Analyst',
      name: 'Delonic Ligia (2311081009)',
      description: 'Menganalisis dataset tugas akhir, melakukan preprocessing data, dan evaluasi performa model. Bertanggung jawab atas kualitas dan akurasi data training.',
      icon: '📊'
    },
    {
      role: 'Programmer',
      name: 'Anla Harpanda (2311083015)',
      description: 'Mengimplementasikan algoritma Naive Bayes, membangun API backend dengan Django, dan mengembangkan frontend dengan Next.js. Menangani deployment dan integrasi sistem.',
      icon: '💻'
    }
  ];

  const extendedMembers = [teamMembers[teamMembers.length - 1], ...teamMembers, teamMembers[0]];

  useEffect(() => {
    const interval = setInterval(() => {
      goToNext();
    }, 5000);
    return () => clearInterval(interval);
  }, [currentSlide]);

  const goToNext = () => {
    setIsTransitioning(true);
    setCurrentSlide(prev => prev + 1);
  };

  const goToPrev = () => {
    setIsTransitioning(true);
    setCurrentSlide(prev => prev - 1);
  };

  const handleTransitionEnd = () => {
    if (currentSlide === 0) {
      setIsTransitioning(false);
      setCurrentSlide(teamMembers.length);
    } else if (currentSlide === teamMembers.length + 1) {
      setIsTransitioning(false);
      setCurrentSlide(1);
    }
  };

  const handlePredict = async () => {
    if (!judul.trim()) return;
    
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/predict/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          judul,
          model_version: modelVersion,
          session_id: sessionId
        })
      });
      const data = await response.json();
      setResult(data);
      
      // Fetch analysis for selected model
      if (modelVersion) {
        fetchAnalysis(modelVersion);
      }
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const fetchAnalysis = async (version: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/analyze/?model_version=${version}`);
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    }
  };

  const handleHistorySelect = (item: any) => {
    setJudul(item.judul);
    setModelVersion(item.model_version);
    setResult(item);
  };

  useEffect(() => {
    if (result && resultRef.current) {
      setTimeout(() => {
        const element = resultRef.current;
        if (element) {
          const y = element.getBoundingClientRect().top + window.pageYOffset - 100;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }, 100);
    }
  }, [result]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handlePredict();
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: any = {
      'Software': 'from-orange-400 to-orange-500',
      'Jaringan': 'from-amber-400 to-amber-500',
      'AI / Machine Learning': 'from-orange-500 to-orange-600',
      'Animasi': 'from-yellow-400 to-orange-400'
    };
    return colors[category] || 'from-orange-400 to-orange-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      <HistoryPanel sessionId={sessionId} onSelectItem={handleHistorySelect} />
      
      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-12">
        {/* Hero Section with Team Slider */}
        <div className="mb-12">
          <div className="text-center mb-8">
            <div className="inline-block mb-4">
              <span className="px-4 py-2 bg-orange-100 text-orange-700 rounded-full text-sm font-semibold">
                🤖 Naive Bayes Classifier
              </span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Prediksi Kelompok Bidang Keahlian
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Masukkan judul tugas akhir Anda dan sistem akan memprediksi kategori KBK menggunakan algoritma Naive Bayes
            </p>
          </div>

          {/* Team Slider */}
          <div className="relative bg-white rounded-2xl shadow-xl border border-orange-100">
            <div className="px-16 overflow-hidden">
              <div 
                className="flex"
                style={{ 
                  transform: `translateX(-${currentSlide * 100}%)`,
                  transition: isTransitioning ? 'transform 0.5s ease-in-out' : 'none'
                }}
                onTransitionEnd={handleTransitionEnd}
              >
                {extendedMembers.map((member, index) => (
                      <div key={index} className="min-w-full flex flex-col md:flex-row items-center gap-8 py-8 px-16">
                        <div className="flex-shrink-0">
                          <div className="relative w-32 h-32 md:w-40 md:h-40">
                            <Image
                              src={member.role === 'Project Manager' ? '/agel.png' : member.role === 'Data Analyst' ? '/gia.png' : 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQvPh9hd-Nonod-jOedev2EWsldcuYjabXayQ&s'}
                              alt={member.role}
                              fill
                              className="rounded-full object-cover border-4 border-orange-200"
                            />
                            <div className="absolute -bottom-2 -right-2 bg-orange-500 text-white w-12 h-12 rounded-full flex items-center justify-center text-2xl shadow-lg">
                              {member.icon}
                            </div>
                          </div>
                        </div>
                        <div className="flex-1 text-center md:text-left">
                          <h3 className="text-2xl font-bold text-gray-900 mb-2">{member.role}</h3>
                          <p className="text-orange-600 font-semibold mb-3">{member.name}</p>
                          <p className="text-gray-600 leading-relaxed">{member.description}</p>
                        </div>
                      </div>
                ))}
              </div>
            </div>

            {/* Navigation Dots */}
            <div className="flex justify-center gap-2 pb-6">
              {teamMembers.map((_, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setIsTransitioning(true);
                    setCurrentSlide(index + 1);
                  }}
                  className={`w-2 h-2 rounded-full transition-all ${
                    currentSlide === index + 1 || (currentSlide === 0 && index === teamMembers.length - 1) || (currentSlide === teamMembers.length + 1 && index === 0) ? 'bg-orange-500 w-8' : 'bg-orange-200'
                  }`}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>

            {/* Navigation Arrows */}
            <button
              onClick={goToPrev}
              className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/90 text-orange-600/50 hover:text-orange-600 w-10 h-10 rounded-full backdrop-blur-sm hover:shadow-lg flex items-center justify-center transition-all"
              aria-label="Previous slide"
            >
              ←
            </button>
            <button
              onClick={goToNext}
              className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/30 hover:bg-white/90 text-orange-600/50 hover:text-orange-600 w-10 h-10 rounded-full backdrop-blur-sm hover:shadow-lg flex items-center justify-center transition-all"
              aria-label="Next slide"
            >
              →
            </button>
          </div>
        </div>

        {/* Input Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
          <ModelSelector value={modelVersion} onChange={setModelVersion} />
          
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            📝 Judul Tugas Akhir
          </label>
          <textarea
            value={judul}
            onChange={(e) => setJudul(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full p-4 border-2 border-orange-200 rounded-xl focus:ring-2 focus:ring-orange-400 focus:border-orange-400 transition-all resize-none text-gray-900 placeholder-gray-400"
            rows={5}
            placeholder="Contoh: Implementasi algoritma naive bayes untuk prediksi kelulusan mahasiswa..."
          />
          <p className="text-xs text-gray-500 mt-2">💡 Tekan Enter untuk prediksi, Shift+Enter untuk baris baru</p>
          <button
            onClick={handlePredict}
            disabled={loading || !judul.trim()}
            className="mt-4 w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white py-4 rounded-xl font-semibold hover:from-orange-600 hover:to-orange-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Memproses...
              </span>
            ) : (
              '🚀 Prediksi Sekarang'
            )}
          </button>
        </div>

        {/* Result Card */}
        {result && (
          <div ref={resultRef} className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <span className="text-2xl">✨</span>
                <h3 className="text-2xl font-bold text-gray-900">Hasil Prediksi</h3>
              </div>
              <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                v{result.model_version}
              </span>
            </div>
            
            {/* Predicted Category */}
            <div className={`bg-gradient-to-r ${getCategoryColor(result.predicted_kbk)} rounded-xl p-6 mb-6 text-white`}>
              <p className="text-sm font-medium opacity-90 mb-2">Kategori Terprediksi</p>
              <p className="text-3xl md:text-4xl font-bold">{result.predicted_kbk}</p>
            </div>

            {/* Probabilities */}
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-4">📊 Distribusi Probabilitas</p>
              <div className="space-y-4">
                {Object.entries(result.probabilities)
                  .sort(([, a]: any, [, b]: any) => b - a)
                  .map(([key, value]: [string, any]) => (
                    <div key={key} className="group">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900 transition-colors">{key}</span>
                        <span className="text-sm font-bold text-gray-900">{(value * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                        <div
                          className={`bg-gradient-to-r ${getCategoryColor(key)} h-3 rounded-full transition-all duration-500 ease-out`}
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
            
            {/* Model Analysis */}
            {analysis && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm font-semibold text-gray-700 mb-3">📈 Performa Model</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">Training Acc</p>
                    <p className="text-lg font-bold text-gray-900">
                      {(analysis.performance.train_accuracy * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">CV Acc</p>
                    <p className="text-lg font-bold text-gray-900">
                      {(analysis.performance.cv_mean_accuracy * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">Overfitting</p>
                    <p className="text-lg font-bold text-gray-900">
                      {(analysis.model_health.overfitting_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">Samples</p>
                    <p className="text-lg font-bold text-gray-900">
                      {analysis.total_samples}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Info Cards */}
        <div className="grid md:grid-cols-4 gap-4 mt-12">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-orange-200 hover:border-orange-300 transition-colors">
            <div className="text-2xl mb-2">💻</div>
            <p className="text-xs font-semibold text-orange-700">Software</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-orange-200 hover:border-orange-300 transition-colors">
            <div className="text-2xl mb-2">🌐</div>
            <p className="text-xs font-semibold text-orange-700">Jaringan</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-orange-200 hover:border-orange-300 transition-colors">
            <div className="text-2xl mb-2">🤖</div>
            <p className="text-xs font-semibold text-orange-700">AI / ML</p>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-orange-200 hover:border-orange-300 transition-colors">
            <div className="text-2xl mb-2">🎨</div>
            <p className="text-xs font-semibold text-orange-700">Animasi</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/90 backdrop-blur-sm border-t border-orange-100 mt-20">
        <div className="max-w-5xl mx-auto px-4 py-6 text-center">
          <p className="text-sm text-gray-600">
            © 2025 Kelompok 2 - Machine Learning | Politeknik Negeri Padang
          </p>
        </div>
      </footer>
    </div>
  );
}
