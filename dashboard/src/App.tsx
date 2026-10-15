import React, { useState } from 'react';
import { useWaterStream } from './hooks/useWaterStream';
import { AppHeader } from './components/ui/AppHeader';
import { NavBar } from './components/ui/NavBar';
import { LiveDashboard } from './views/LiveDashboard';
import { HistoryView } from './views/HistoryView';
import { AlertsView } from './views/AlertsView';
import { EdgePerformanceView } from './views/EdgePerformanceView';
import { SettingsView } from './views/SettingsView';
import { ActiveTab } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('live');
  const {
    current,
    history,
    alerts,
    connectionStatus,
    connectionType,
    countdown,
    refreshIntervalSec,
    clearAlerts,
  } = useWaterStream();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased selection:bg-teal-500 selection:text-white">
      {/* Top Header */}
      <AppHeader
        current={current}
        connectionStatus={connectionStatus}
        connectionType={connectionType}
        countdown={countdown}
        refreshIntervalSec={refreshIntervalSec}
      />

      {/* Tab Navigation */}
      <NavBar
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        alertCount={alerts.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'live' && (
          <LiveDashboard
            current={current}
            history={history}
            onViewAlerts={() => setActiveTab('alerts')}
          />
        )}

        {activeTab === 'history' && <HistoryView liveHistory={history} />}

        {activeTab === 'alerts' && (
          <AlertsView alerts={alerts} onClearAlerts={clearAlerts} />
        )}

        {activeTab === 'performance' && (
          <EdgePerformanceView current={current} history={history} />
        )}

        {activeTab === 'settings' && (
          <SettingsView currentThreshold={current?.threshold || 0.35} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>WaterQA Edge System • Mô hình Quan trắc Chất lượng Nước Biên</span>
          <span>Chu kỳ làm tươi: 6.0 giây/mẫu • MQTT ws://localhost:9001</span>
        </div>
      </footer>
    </div>
  );
}
