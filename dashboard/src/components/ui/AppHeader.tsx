import React from 'react';
import { Droplet, Radio, Clock, Cpu, Server, HardDrive } from 'lucide-react';
import { WaterMetric } from '../../types';

interface AppHeaderProps {
  current: WaterMetric | null;
  connectionStatus: 'connected' | 'connecting' | 'disconnected';
  connectionType: 'MQTT' | 'WebSocket' | 'REST';
  countdown: number;
  refreshIntervalSec: number;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  current,
  connectionStatus,
  connectionType,
  countdown,
  refreshIntervalSec,
}) => {
  const isDevice = current?.source === 'mqtt' || current?.source === 'http' || current?.source === 'serial';

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 text-white shadow-md shadow-teal-500/20">
              <Droplet className="h-5 w-5 fill-current" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 tracking-tight text-base sm:text-lg">
                  WaterQA <span className="text-teal-600 font-semibold">Edge</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Hệ thống Giám sát & Phát hiện Bất thường Chất lượng Nước Biên (Edge AI)
              </p>
            </div>
          </div>

          {/* Right Header Status Bar */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Active Source Badge */}
            <div
              className={`hidden sm:flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold border ${
                isDevice
                  ? 'bg-purple-50 text-purple-700 border-purple-200'
                  : 'bg-blue-50 text-blue-700 border-blue-200'
              }`}
            >
              {isDevice ? <Server className="h-3 w-3" /> : <HardDrive className="h-3 w-3" />}
              <span>{isDevice ? `Thiết bị: ${current?.device_id || 'IoT'}` : 'Nguồn: CSV (Mock)'}</span>
            </div>

            {/* 6s Countdown Timer Badge */}
            <div className="flex items-center gap-1.5 rounded-full bg-slate-100/90 px-3 py-1 text-xs text-slate-600 border border-slate-200/60">
              <Clock className="h-3.5 w-3.5 text-teal-600 animate-spin-slow" />
              <span className="hidden md:inline text-slate-500 font-medium">Nhịp:</span>
              <span className="font-bold text-teal-700">{countdown}s</span>
              <span className="text-[10px] text-slate-400">/ {refreshIntervalSec}s</span>
            </div>

            {/* Connection Status Badge */}
            <div
              className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium border ${
                connectionStatus === 'connected'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : connectionStatus === 'connecting'
                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                  : 'bg-red-50 text-red-700 border-red-200'
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  connectionStatus === 'connected'
                    ? 'bg-emerald-500 animate-pulse'
                    : connectionStatus === 'connecting'
                    ? 'bg-amber-500'
                    : 'bg-red-500'
                }`}
              />
              <span className="capitalize">
                {connectionStatus === 'connected'
                  ? `${connectionType}`
                  : connectionStatus === 'connecting'
                  ? 'Đang kết nối...'
                  : 'Mất kết nối'}
              </span>
            </div>

            {/* Sample seq count */}
            {current?.seq !== undefined && (
              <div className="hidden lg:flex items-center gap-1.5 rounded-xl bg-slate-50 px-2.5 py-1 text-xs border border-slate-200 text-slate-700 font-mono">
                <span className="text-slate-400">#</span>
                <span className="font-bold">{current.seq}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
