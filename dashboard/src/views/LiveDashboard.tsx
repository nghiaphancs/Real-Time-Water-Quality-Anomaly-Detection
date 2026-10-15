import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import {
  AlertTriangle,
  CheckCircle2,
  Droplets,
  Gauge,
  Activity,
  Cpu,
  Zap,
  MapPin,
  Calendar,
  Layers,
  Info,
} from 'lucide-react';
import { WaterMetric } from '../types';
import { SENSORS } from '../configs/sensors';
import { Card } from '../components/ui/Card';
import { StatBox } from '../components/ui/StatBox';
import { GaugeChart } from '../components/ui/GaugeChart';
import { AlertBanner } from '../components/ui/AlertBanner';

interface LiveDashboardProps {
  current: WaterMetric | null;
  history: WaterMetric[];
  onViewAlerts?: () => void;
}

export const LiveDashboard: React.FC<LiveDashboardProps> = ({
  current,
  history,
  onViewAlerts,
}) => {
  if (!current) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center text-center">
        <div className="relative mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-50 text-teal-600">
          <Droplets className="h-8 w-8 animate-bounce" />
        </div>
        <h3 className="text-base font-semibold text-slate-800">Đang khởi tạo luồng dữ liệu...</h3>
        <p className="mt-1 text-xs text-slate-500 max-w-sm">
          Đang kết nối tới trạm quan trắc biên MQTT/WebSocket và tải số liệu chu kỳ 6 giây.
        </p>
      </div>
    );
  }

  const isAnomaly = current.prediction === 'ANOMALY';
  const isWarmingUp = current.warming_up || false;
  const prevMetric = history.length >= 2 ? history[history.length - 2] : undefined;

  // Chart data formatted
  const chartData = history.slice(-25).map((m) => ({
    time: m.sensor_timestamp ? m.sensor_timestamp.slice(-5) : `#${m.seq}`,
    pH: m.pH,
    DO: m.DO,
    Độ_đục: m.turbidity,
    EC: m.EC,
    Nhiệt_độ: m.temperature,
    score: Number((m.anomaly_score * 100).toFixed(1)),
  }));

  // WQI color helper
  const getWqiColor = (wqi: number | undefined | null) => {
    if (wqi === undefined || wqi === null) return { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' };
    if (wqi >= 80) return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' };
    if (wqi >= 60) return { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' };
    if (wqi >= 40) return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' };
    return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' };
  };

  const wqiStyle = getWqiColor(current.wqi);

  return (
    <div className="space-y-6">
      {/* Alert Banner if Anomaly */}
      <AlertBanner current={current} onViewDetails={onViewAlerts} />

      {/* Warming-up Information Banner */}
      {isWarmingUp && (
        <div className="flex items-center gap-3 rounded-2xl bg-blue-50/80 border border-blue-200 p-4 text-blue-900 text-xs">
          <Info className="h-5 w-5 text-blue-600 flex-shrink-0" />
          <div>
            <span className="font-bold">Đang nạp mẫu đệm khởi động: {current.buffer_current || 1} / {current.buffer_max || 30} mẫu.</span>
            <p className="text-blue-700 mt-0.5">
              Hệ thống đang tích lũy đủ chuỗi mẫu thời gian thực để kích hoạt thuật toán phát hiện bất thường đa biến chuẩn xác.
            </p>
          </div>
        </div>
      )}

      {/* Station Overview & Status Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Station Card */}
        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-xs flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
            <MapPin className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Trạm quan trắc</span>
            <h4 className="font-bold text-slate-800 text-sm">{current.station}</h4>
            <p className="text-xs text-slate-500">{current.city}, {current.province || 'Việt Nam'}</p>
          </div>
        </div>

        {/* Date / Timestamp Card */}
        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-xs flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
            <Calendar className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Thời gian mẫu đo</span>
            <h4 className="font-bold text-slate-800 text-sm">{current.sensor_timestamp || current.received_at}</h4>
            <p className="text-xs text-slate-500">Chu kỳ đẩy: 6 giây / mẫu</p>
          </div>
        </div>

        {/* WQI Index */}
        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-xs flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
            <Droplets className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase text-slate-400">Chỉ số WQI / Đánh giá</span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="font-extrabold text-slate-900 text-base">
                {current.wqi !== undefined && current.wqi !== null ? current.wqi.toFixed(1) : '—'}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${wqiStyle.bg} ${wqiStyle.text} ${wqiStyle.border}`}>
                {current.pollution_level || (current.wqi !== undefined && current.wqi !== null ? 'Good' : '—')}
              </span>
            </div>
          </div>
        </div>

        {/* AI Prediction Status Card */}
        <div
          className={`rounded-2xl p-4 shadow-xs flex items-center gap-3 border transition-all ${
            isAnomaly
              ? 'bg-red-50/80 border-red-200 text-red-900 ring-2 ring-red-200/50'
              : 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
          }`}
        >
          <div
            className={`flex h-11 w-11 items-center justify-center rounded-xl ${
              isAnomaly ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'
            }`}
          >
            {isAnomaly ? <AlertTriangle className="h-5 w-5 animate-pulse" /> : <CheckCircle2 className="h-5 w-5" />}
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase opacity-75">Trạng thái Edge AI</span>
            <div className="flex items-center gap-2 mt-0.5">
              <h4 className="font-bold text-sm">
                {isAnomaly ? 'PHÁT HIỆN BẤT THƯỜNG' : 'BÌNH THƯỜNG (AN TOÀN)'}
              </h4>
            </div>
            <p className="text-[11px] opacity-80">
              {isWarmingUp ? `Đang khởi tạo đệm (${current.buffer_current}/30)` : `Cửa sổ đệm: ${current.buffer_current || 30}/${current.buffer_max || 30} mẫu`}
            </p>
          </div>
        </div>
      </div>

      {/* Core Metrics & AI Anomaly Score Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: 5 Sensor Parameter StatBoxes */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Activity className="h-4 w-4 text-teal-600" />
              <span>Chỉ số 5 Cảm biến Quan trắc</span>
            </h3>
            <span className="text-xs text-slate-500">Cập nhật mỗi 6 giây</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <StatBox
              sensor={SENSORS.pH}
              value={current.pH}
              prevValue={prevMetric?.pH}
              isAnomaly={isAnomaly && (current.pH < SENSORS.pH.safeMin || current.pH > SENSORS.pH.safeMax)}
            />
            <StatBox
              sensor={SENSORS.DO}
              value={current.DO}
              prevValue={prevMetric?.DO}
              isAnomaly={isAnomaly && current.DO < SENSORS.DO.safeMin}
            />
            <StatBox
              sensor={SENSORS.turbidity}
              value={current.turbidity}
              prevValue={prevMetric?.turbidity}
              isAnomaly={isAnomaly && current.turbidity > SENSORS.turbidity.safeMax}
            />
            <StatBox
              sensor={SENSORS.EC}
              value={current.EC}
              prevValue={prevMetric?.EC}
              isAnomaly={isAnomaly && (current.EC < SENSORS.EC.safeMin || current.EC > SENSORS.EC.safeMax)}
            />
            <div className="sm:col-span-2">
              <StatBox
                sensor={SENSORS.temperature}
                value={current.temperature}
                prevValue={prevMetric?.temperature}
                isAnomaly={isAnomaly && (current.temperature < SENSORS.temperature.safeMin || current.temperature > SENSORS.temperature.safeMax)}
              />
            </div>
          </div>
        </div>

        {/* Right: Anomaly Score Gauge & Edge AI Card */}
        <div className="space-y-4">
          <Card
            title="Độ lệch & Điểm Bất thường"
            subtitle="Mô hình suy luận biên (Edge Anomaly Detector)"
            icon={<Gauge className="h-4 w-4 text-teal-600" />}
          >
            <div className="pt-2 pb-4">
              <GaugeChart
                score={current.anomaly_score}
                threshold={current.threshold}
                size={230}
              />
            </div>

            {/* Contributing features tags */}
            {current.contributing_features && current.contributing_features.length > 0 && (
              <div className="mb-3 p-2.5 rounded-xl bg-amber-50 border border-amber-200 text-xs">
                <span className="font-semibold text-amber-900 block mb-1">Đặc trưng lệch chính:</span>
                <div className="flex flex-wrap gap-1">
                  {current.contributing_features.map((feat, i) => (
                    <span key={i} className="px-2 py-0.5 rounded-md bg-white border border-amber-300 text-amber-800 text-[11px] font-medium">
                      {feat}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Ngưỡng phân định (Threshold):</span>
                <span className="font-semibold text-slate-900">{current.threshold}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Độ trễ suy luận (Inference):</span>
                <span className="font-semibold text-teal-700">{current.inference_latency_ms} ms</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Độ trễ đầu-cuối (E2E Latency):</span>
                <span className="font-semibold text-slate-900">{current.end_to_end_latency_ms} ms</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Kích thước mô hình (Model Size):</span>
                <span className="font-semibold text-slate-900">{current.model_size_kb} KB</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Real-time Rolling Line Chart (Last 25 samples @ 6s intervals) */}
      <Card
        title="Biểu đồ Diễn biến Chuỗi Thời gian (Real-time Trend)"
        subtitle="Biến động các thông số nước qua các chu kỳ 6 giây gần nhất"
        icon={<Activity className="h-4 w-4 text-teal-600" />}
      >
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="pH"
                stroke="#00A89D"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
                name="pH"
              />
              <Line
                type="monotone"
                dataKey="DO"
                stroke="#0284C7"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
                name="DO (mg/L)"
              />
              <Line
                type="monotone"
                dataKey="Độ_đục"
                stroke="#F59E0B"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
                name="Độ đục (NTU)"
              />
              <Line
                type="monotone"
                dataKey="Nhiệt_độ"
                stroke="#EC4899"
                strokeWidth={1.5}
                dot={false}
                name="Nhiệt độ (°C)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* System Quick Bar (CPU / RAM / Throughput) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl bg-white border border-slate-200/80 p-3 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs">
            <Cpu className="h-3.5 w-3.5 text-teal-600" />
            <span>Tải CPU Hệ thống</span>
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-xl font-bold text-slate-800">{current.system_cpu_pct}%</span>
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200/80 p-3 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs">
            <Zap className="h-3.5 w-3.5 text-blue-600" />
            <span>RAM Hệ thống</span>
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-xl font-bold text-slate-800">{current.system_ram_pct}%</span>
            <span className="text-xs text-slate-400">({current.process_ram_mb} MB)</span>
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200/80 p-3 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs">
            <Activity className="h-3.5 w-3.5 text-emerald-600" />
            <span>Thông lượng (Throughput)</span>
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-xl font-bold text-slate-800">{current.throughput_msg_per_sec}</span>
            <span className="text-xs text-slate-400">msg/s</span>
          </div>
        </div>

        <div className="rounded-xl bg-white border border-slate-200/80 p-3 shadow-2xs">
          <div className="flex items-center gap-2 text-slate-500 text-xs">
            <Layers className="h-3.5 w-3.5 text-purple-600" />
            <span>Chu kỳ đẩy dữ liệu</span>
          </div>
          <div className="mt-1 flex items-baseline gap-1">
            <span className="text-xl font-bold text-teal-700">6.0</span>
            <span className="text-xs text-slate-400">giây / mẫu</span>
          </div>
        </div>
      </div>
    </div>
  );
};
