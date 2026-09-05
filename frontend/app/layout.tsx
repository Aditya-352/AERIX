import type { Metadata } from 'next';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'AEROVA — India Airfare Price Intelligence Platform',
  description: 'Tracking India’s Airfare Movement in Real Time. Airfare Price Index (APIx), Lead-Time Elasticity, and Multi-Provider Price Comparison.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="light">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <p className="font-semibold text-slate-800">AEROVA — India Airfare Price Intelligence Platform</p>
              <p className="text-slate-500 mt-1">Prototype / Experimental Airfare Price Index (APIx) to support CPI transportation measurement research.</p>
            </div>
            <div className="flex items-center gap-4 text-slate-600">
              <span className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-[11px] font-mono text-slate-700 font-semibold">
                Mode: Synthetic Demo Dataset
              </span>
              <span className="font-medium">v1.0.0</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
