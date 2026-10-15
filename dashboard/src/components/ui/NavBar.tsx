import React from 'react';
import { Activity, History, Bell, Cpu, Settings } from 'lucide-react';
import { ActiveTab } from '../../types';

interface NavBarProps {
  activeTab: ActiveTab;
  onChangeTab: (tab: ActiveTab) => void;
  alertCount?: number;
}

export const NavBar: React.FC<NavBarProps> = ({ activeTab, onChangeTab, alertCount = 0 }) => {
  const tabs = [
    { id: 'live' as ActiveTab, label: 'Trực tiếp', icon: Activity },
    { id: 'history' as ActiveTab, label: 'Lịch sử đo', icon: History },
    { id: 'alerts' as ActiveTab, label: 'Cảnh báo', icon: Bell, badge: alertCount },
    { id: 'performance' as ActiveTab, label: 'Hiệu năng Edge', icon: Cpu },
    { id: 'settings' as ActiveTab, label: 'Cấu hình', icon: Settings },
  ];

  return (
    <div className="border-b border-slate-200/80 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-2 sm:space-x-8 overflow-x-auto py-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onChangeTab(tab.id)}
                className={`flex items-center gap-2 py-2.5 px-3 rounded-xl text-xs sm:text-sm font-medium transition-all whitespace-nowrap cursor-pointer ${
                  isActive
                    ? 'bg-teal-50 text-teal-700 shadow-2xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? 'text-teal-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {Boolean(tab.badge && tab.badge > 0) && (
                  <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};
