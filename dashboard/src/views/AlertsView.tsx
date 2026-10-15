import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Bell,
  Trash2,
  ShieldAlert,
  ArrowUpRight,
  Info,
} from 'lucide-react';
import { WaterMetric } from '../types';
import { Card } from '../components/ui/Card';
import { SENSORS } from '../configs/sensors';

interface AlertsViewProps {
  alerts: WaterMetric[];
  onClearAlerts: () => void;
}

export const AlertsView: React.FC<AlertsViewProps> = ({ alerts, onClearAlerts }) => {
  const [acknowledged, setAcknowledged] = useState<Record<string, boolean>>({});

  const handleToggleAcknowledge = (id: string) => {
    setAcknowledged((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Sự cố & Cảnh báo Bất thường</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Danh sách các mẫu nước vượt ngưỡng phát hiện bởi thuật toán Edge AI (Threshold &gt; 0.35)
          </p>
        </div>

        {alerts.length > 0 && (
          <button
            onClick={onClearAlerts}
            className="inline-flex items-center gap-1.5 rounded-xl border border-red-200 bg-red-50/50 px-3.5 py-2 text-xs font-semibold text-red-700 hover:bg-red-100 transition-colors cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Xóa danh sách cảnh báo</span>
          </button>
        )}
      </div>

      {alerts.length === 0 ? (
        <Card className="py-12 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 mb-3">
            <CheckCircle className="h-7 w-7" />
          </div>
          <h3 className="text-base font-semibold text-slate-800">Không có sự cố bất thường</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
            Hệ thống đang hoạt động ổn định. Tất cả các chỉ số (pH, DO, Turbidity, EC, Nhiệt độ) đều nằm trong ngưỡng an toàn bình thường.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {alerts.map((item, idx) => {
            const alertId = `${item.sensor_timestamp}-${idx}`;
            const isAck = acknowledged[alertId] || false;

            // Identify anomaly causes
            const causes: string[] = [];
            if (item.pH < SENSORS.pH.safeMin || item.pH > SENSORS.pH.safeMax) {
              causes.push(`pH lệch chuẩn (${item.pH.toFixed(2)})`);
            }
            if (item.DO < SENSORS.DO.safeMin) {
              causes.push(`Oxy hòa tan DO rất thấp (${item.DO.toFixed(2)} mg/L)`);
            }
            if (item.turbidity > SENSORS.turbidity.safeMax) {
              causes.push(`Độ đục cao bất thường (${item.turbidity.toFixed(2)} NTU)`);
            }
            if (item.EC > SENSORS.EC.safeMax) {
              causes.push(`Độ dẫn điện EC tăng cao (${item.EC.toFixed(1)} µS/cm)`);
            }
            if (item.temperature > SENSORS.temperature.safeMax) {
              causes.push(`Nhiệt độ nước cao (${item.temperature.toFixed(2)} °C)`);
            }
            if (causes.length === 0) {
              causes.push(`Tổ hợp đa biến lệch tâm chuẩn hóa (Anomaly Score: ${item.anomaly_score.toFixed(4)})`);
            }

            return (
              <div
                key={alertId}
                className={`rounded-2xl border p-5 transition-all ${
                  isAck
                    ? 'bg-slate-50/70 border-slate-200 opacity-70'
                    : 'bg-white border-red-200 shadow-sm ring-1 ring-red-100'
                }`}
              >
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-3.5">
                    <div
                      className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl ${
                        isAck ? 'bg-slate-200 text-slate-500' : 'bg-red-100 text-red-600'
                      }`}
                    >
                      <AlertTriangle className="h-5 w-5" />
                    </div>

                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-bold text-slate-900 text-sm">
                          Sự cố tại trạm {item.station} ({item.city})
                        </span>
                        <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-bold text-red-700">
                          Score: {item.anomaly_score.toFixed(4)}
                        </span>
                        {isAck && (
                          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                            Đã xác nhận
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-slate-500 mt-1">
                        Thời gian: <span className="font-medium text-slate-700">{item.sensor_timestamp}</span> • Ngưỡng: {item.threshold} • Độ trễ AI: {item.inference_latency_ms} ms
                      </p>

                      {/* Potential causes tags */}
                      <div className="flex flex-wrap items-center gap-1.5 mt-2.5">
                        <span className="text-[11px] text-slate-500 font-medium">Nguyên nhân nghi vấn:</span>
                        {causes.map((c, i) => (
                          <span
                            key={i}
                            className="rounded-lg bg-rose-50 px-2 py-0.5 text-[11px] font-semibold text-rose-700 border border-rose-200"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center">
                    <button
                      onClick={() => handleToggleAcknowledge(alertId)}
                      className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition-colors cursor-pointer ${
                        isAck
                          ? 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                          : 'bg-teal-50 text-teal-700 hover:bg-teal-100 border border-teal-200'
                      }`}
                    >
                      {isAck ? 'Hủy xác nhận' : 'Xác nhận xử lý'}
                    </button>
                  </div>
                </div>

                {/* Sensor values snapshot */}
                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
                  <div className="bg-slate-50 rounded-lg p-2">
                    <span className="text-slate-400 block text-[10px]">pH</span>
                    <span className="font-bold text-slate-800">{item.pH.toFixed(2)}</span>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2">
                    <span className="text-slate-400 block text-[10px]">DO</span>
                    <span className="font-bold text-slate-800">{item.DO.toFixed(2)} mg/L</span>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2">
                    <span className="text-slate-400 block text-[10px]">Độ đục</span>
                    <span className="font-bold text-slate-800">{item.turbidity.toFixed(2)} NTU</span>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2">
                    <span className="text-slate-400 block text-[10px]">EC</span>
                    <span className="font-bold text-slate-800">{item.EC.toFixed(1)} µS/cm</span>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-2">
                    <span className="text-slate-400 block text-[10px]">Nhiệt độ</span>
                    <span className="font-bold text-slate-800">{item.temperature.toFixed(2)} °C</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
