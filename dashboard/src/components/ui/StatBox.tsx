import React from 'react';
import { SensorMeta } from '../../configs/sensors';

interface StatBoxProps {
  sensor: SensorMeta;
  value: number;
  prevValue?: number;
  isAnomaly?: boolean;
}

export const StatBox: React.FC<StatBoxProps> = ({
  sensor,
  value,
  prevValue,
  isAnomaly = false,
}) => {
  // Check if value is outside safe range
  const isOutOfRange = value < sensor.safeMin || value > sensor.safeMax;

  // Percentage for the bar
  const range = sensor.max - sensor.min || 1;
  const clampedVal = Math.max(sensor.min, Math.min(sensor.max, value));
  const percent = Math.round(((clampedVal - sensor.min) / range) * 100);

  // Safe range percentage span
  const safeLeft = Math.round(((sensor.safeMin - sensor.min) / range) * 100);
  const safeWidth = Math.round(((sensor.safeMax - sensor.safeMin) / range) * 100);

  // Delta comparison
  const delta = prevValue !== undefined ? Number((value - prevValue).toFixed(2)) : 0;

  return (
    <div
      className={`relative overflow-hidden rounded-2xl bg-white border p-4.5 transition-all duration-200 ${
        isAnomaly
          ? 'border-red-300 ring-2 ring-red-100 shadow-md'
          : isOutOfRange
          ? 'border-amber-300 shadow-xs'
          : 'border-slate-200 hover:border-slate-300 shadow-xs'
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{sensor.key}</span>
          <h4 className="text-sm font-semibold text-slate-800 mt-0.5">{sensor.nameVi}</h4>
        </div>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${
            isAnomaly
              ? 'bg-red-50 text-red-700 border border-red-200 animate-pulse'
              : isOutOfRange
              ? 'bg-amber-50 text-amber-700 border border-amber-200'
              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
          }`}
        >
          {isAnomaly ? 'Bất thường' : isOutOfRange ? 'Cảnh báo' : 'An toàn'}
        </span>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-bold tracking-tight text-slate-900">
          {typeof value === 'number' ? value.toFixed(2) : '--'}
        </span>
        <span className="text-sm font-medium text-slate-500">{sensor.unit}</span>

        {delta !== 0 && (
          <span className={`text-xs ml-auto font-medium ${delta > 0 ? 'text-teal-600' : 'text-slate-500'}`}>
            {delta > 0 ? `+${delta}` : delta}
          </span>
        )}
      </div>

      {/* Range Progress Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-[11px] text-slate-400 mb-1">
          <span>{sensor.min} {sensor.unit}</span>
          <span className="text-slate-500 font-medium">Chuẩn: {sensor.safeMin} - {sensor.safeMax}</span>
          <span>{sensor.max} {sensor.unit}</span>
        </div>

        <div className="relative h-2 w-full rounded-full bg-slate-100 overflow-hidden">
          {/* Safe zone highlight */}
          <div
            className="absolute top-0 bottom-0 bg-emerald-100"
            style={{ left: `${safeLeft}%`, width: `${safeWidth}%` }}
          />
          {/* Current value bar */}
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.max(4, percent)}%`,
              backgroundColor: isAnomaly ? '#EF4444' : isOutOfRange ? '#F59E0B' : sensor.color,
            }}
          />
        </div>
      </div>
    </div>
  );
};
