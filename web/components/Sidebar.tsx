'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { Home, BarChart3, Brain, FileText, Menu, X } from 'lucide-react';

const navItems = [
  { href: '/', icon: Home, label: 'Home' },
  { href: '/analysis/overview', icon: BarChart3, label: 'Overview' },
  { href: '/analysis/performance', icon: BarChart3, label: 'Performance' },
  { href: '/analysis/naive-bayes', icon: Brain, label: 'Naive Bayes' },
  { href: '/analysis/features', icon: FileText, label: 'Features' },
];

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const pathname = usePathname();

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 lg:hidden p-2 bg-white rounded-lg shadow-lg"
      >
        <Menu className="w-6 h-6" />
      </button>

      <aside
        className={`fixed inset-y-0 left-0 z-40 bg-white border-r border-gray-200 shadow-lg transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        } ${isOpen ? 'w-64' : 'lg:w-20'}`}
      >
        <div className="h-full flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <Image
                src="https://www.pnp.ac.id/wp-content/uploads/2025/01/LOGO-PNP.png"
                alt="Logo PNP"
                width={40}
                height={40}
                className="object-contain"
              />
              {isOpen && (
                <div>
                  <h1 className="text-sm font-bold text-gray-900">Prediksi KBK</h1>
                  <p className="text-xs text-gray-600">Machine Learning</p>
                </div>
              )}
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-orange-500 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {isOpen && <span className="text-sm font-medium">{item.label}</span>}
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-gray-200">
            {isOpen && (
              <div className="text-center">
                <p className="text-sm font-semibold text-orange-600">Kelompok 2</p>
                <p className="text-xs text-gray-500">Politeknik Negeri Padang</p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
