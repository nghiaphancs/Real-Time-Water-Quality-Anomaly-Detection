import React, { useState } from 'react';
import { AlertTriangle, X, BellRing, ArrowRight } from 'lucide-react';
import { WaterMetric } from '../../types';

interface AlertBannerProps {
  current: WaterMetric | null;
  onViewDetails?: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ current, onViewDetails }) => {
  const [dismissed, setDismissed] = useState(false);

  if (!current || current.prediction !== 'ANOMALY' || dismissed) {
    return null;
  }

  return (
    <div className="relative mb-6 overflow-hidden rounded-2xl bg-gradient-to-r from-red-500 via-rose-500 to-amber-500 p-0.5 shadow-lg shadow-red-500/10 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-[14px] bg-white p-4.5">
        <div className="flex items-center gap-3.5">
          <div className="relative flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-red-100 text-red-600">
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
            <AlertTriangle className="h-6 w-6" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-slate-900 text-sm sm:text-base">
                🚨 Cảnh báo: Phát hiện bất thường chất lượng nước!
              </h4>
              <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                Score: {current.anomaly_score.toFixed(4)}
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-0.5">
              Trạm <span className="font-medium text-slate-800">{current.station} ({current.city})</span> • Điểm lệch vượt ngưỡng {current.threshold} lúc {current.sensor_timestamp}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
          {onViewDetails && (
            <button
              onClick={onViewDetails}
              className="inline-flex items-center gap-1.5 rounded-xl bg-red-50 px-3.5 py-2 text-xs font-semibold text-red-700 hover:bg-red-100 transition-colors"
            >
              <span>Chi tiết</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          )}
          <button
            onClick={() => setDismissed(true)}
            className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            title="Đóng thông báo"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
