import React from 'react';

interface GaugeChartProps {
  score: number;
  threshold?: number;
  size?: number;
  strokeWidth?: number;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  score = 0,
  threshold = 0.35,
  size = 200,
  strokeWidth = 16,
}) => {
  const clampedScore = Math.max(0, Math.min(1, score));
  const isAnomaly = clampedScore > threshold;

  // Semi-circle coordinates
  const radius = (size - strokeWidth) / 2;
  const center = size / 2;
  const circumference = Math.PI * radius; // Half-circle perimeter
  const strokeDashoffset = circumference - clampedScore * circumference;

  // Threshold marker angle in radians
  const thresholdAngle = Math.PI * (1 - threshold);
  const thresholdX = center + radius * Math.cos(thresholdAngle);
  const thresholdY = center - radius * Math.sin(thresholdAngle);

  // Status color
  const statusColor = isAnomaly ? '#EF4444' : clampedScore > threshold * 0.7 ? '#F59E0B' : '#10B981';

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size / 2 + 30 }}>
        <svg width={size} height={size / 2 + 25} className="overflow-visible">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="35%" stopColor="#34D399" />
              <stop offset="60%" stopColor="#FBBF24" />
              <stop offset="100%" stopColor="#EF4444" />
            </linearGradient>
          </defs>

          {/* Background Track */}
          <path
            d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Progress Path */}
          <path
            d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />

          {/* Threshold marker dot */}
          <circle
            cx={thresholdX}
            cy={thresholdY}
            r={5}
            fill="#EF4444"
            stroke="#FFFFFF"
            strokeWidth={2}
          />
        </svg>

        {/* Center Text */}
        <div
          className="absolute inset-x-0 bottom-0 flex flex-col items-center justify-center text-center"
          style={{ height: size / 2 }}
        >
          <span
            className="text-3xl font-extrabold tracking-tight transition-colors duration-300"
            style={{ color: statusColor }}
          >
            {clampedScore.toFixed(4)}
          </span>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 mt-0.5">
            Điểm bất thường (Score)
          </span>
        </div>
      </div>

      {/* Threshold legend */}
      <div className="flex items-center gap-4 text-xs mt-1 text-slate-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
          <span>Bình thường (&le; {threshold})</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
          <span>Bất thường (&gt; {threshold})</span>
        </div>
      </div>
    </div>
  );
};
