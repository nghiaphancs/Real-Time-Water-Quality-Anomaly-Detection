import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Save,
  CheckCircle2,
  Server,
  Layers,
  HardDrive,
  Radio,
  FileSpreadsheet,
  Cpu,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { EdgeConfig, DatasetItem, DeviceInfo } from '../types';

interface SettingsViewProps {
  currentThreshold: number;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ currentThreshold }) => {
  const [threshold, setThreshold] = useState<number>(currentThreshold || 0.35);
  const [windowSize, setWindowSize] = useState<number>(30);
  const [intervalSec, setIntervalSec] = useState<number>(6.0);
  const [sourceMode, setSourceMode] = useState<'csv' | 'device' | 'auto'>('csv');
  const [csvFile, setCsvFile] = useState<string>('china_water_pollution_data.csv');
  const [csvOrder, setCsvOrder] = useState<'sequential' | 'random' | 'by_date'>('sequential');
  const [detectorType, setDetectorType] = useState<'rule_based' | 'onnx'>('rule_based');

  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  // Load initial settings
  useEffect(() => {
    fetch(`http://${window.location.hostname}:8000/api/v1/config`)
      .then((res) => res.json())
      .then((data: EdgeConfig) => {
        if (data?.detector?.threshold) setThreshold(data.detector.threshold);
        if (data?.detector?.window_size) setWindowSize(data.detector.window_size);
        if (data?.detector?.type) setDetectorType(data.detector.type);
        if (data?.source?.mode) setSourceMode(data.source.mode);
        if (data?.source?.csv?.file) setCsvFile(data.source.csv.file);
        if (data?.source?.csv?.order) setCsvOrder(data.source.csv.order);
        if (data?.source?.csv?.interval_sec) setIntervalSec(data.source.csv.interval_sec);
      })
      .catch((err) => console.log('Error loading config:', err));

    // Load datasets
    fetch(`http://${window.location.hostname}:8000/api/v1/datasets`)
      .then((res) => res.json())
      .then((data) => {
        if (data?.datasets) setDatasets(data.datasets);
      })
      .catch((err) => console.log('Error loading datasets:', err));

    // Load devices
    fetch(`http://${window.location.hostname}:8000/api/v1/devices`)
      .then((res) => res.json())
      .then((devs: DeviceInfo[]) => {
        if (Array.isArray(devs)) setDevices(devs);
      })
      .catch((err) => console.log('Error loading devices:', err));
  }, []);

  const handleSave = () => {
    setSaving(true);
    fetch(`http://${window.location.hostname}:8000/api/v1/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        threshold,
        window_size: windowSize,
        interval_sec: intervalSec,
        source_mode: sourceMode,
        csv_file: csvFile,
        csv_order: csvOrder,
        detector_type: detectorType,
      }),
    })
      .then((res) => res.json())
      .then(() => {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 3000);
      })
      .catch((err) => console.error('Save error:', err))
      .finally(() => setSaving(false));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Cấu hình & Quản lý Nguồn Dữ liệu</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Tùy chỉnh linh hoạt giữa phát lại CSV Mock và nhận dữ liệu thời gian thực từ Thiết bị Raspberry Pi / IoT
        </p>
      </div>

      {savedSuccess && (
        <div className="flex items-center gap-2 rounded-2xl bg-emerald-50 border border-emerald-200 p-4 text-emerald-800 text-xs font-semibold animate-fade-in">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <span>Đã áp dụng và lưu thành công cấu hình vào hệ thống biên app.yaml!</span>
        </div>
      )}

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Source Switching & Dataset Selection */}
        <Card
          title="Chế độ Nguồn Dữ liệu (Data Source Mode)"
          subtitle="Chuyển đổi tức thời không cần khởi động lại dịch vụ"
          icon={<Server className="h-4 w-4 text-teal-600" />}
        >
          <div className="space-y-5">
            {/* Mode selection radio */}
            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-2">Chọn chế độ hoạt động:</label>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setSourceMode('csv')}
                  className={`p-3 rounded-xl border text-center font-medium transition-all cursor-pointer ${
                    sourceMode === 'csv'
                      ? 'border-teal-500 bg-teal-50/70 text-teal-800 ring-2 ring-teal-200 font-bold'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <FileSpreadsheet className="h-4 w-4 mx-auto mb-1 text-teal-600" />
                  <span>CSV (Mock)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSourceMode('device')}
                  className={`p-3 rounded-xl border text-center font-medium transition-all cursor-pointer ${
                    sourceMode === 'device'
                      ? 'border-purple-500 bg-purple-50/70 text-purple-800 ring-2 ring-purple-200 font-bold'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Radio className="h-4 w-4 mx-auto mb-1 text-purple-600" />
                  <span>Thiết bị IoT</span>
                </button>

                <button
                  type="button"
                  onClick={() => setSourceMode('auto')}
                  className={`p-3 rounded-xl border text-center font-medium transition-all cursor-pointer ${
                    sourceMode === 'auto'
                      ? 'border-blue-500 bg-blue-50/70 text-blue-800 ring-2 ring-blue-200 font-bold'
                      : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <Cpu className="h-4 w-4 mx-auto mb-1 text-blue-600" />
                  <span>Tự động (Auto)</span>
                </button>
              </div>
              <p className="text-[11px] text-slate-400 mt-2">
                * Chế độ Tự động: Ưu tiên thiết bị khi có kết nối; tự động chuyển sang phát lại CSV nếu mất tín hiệu quá 30 giây.
              </p>
            </div>

            {/* Dataset file selection dropdown */}
            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1.5">
                Tệp dữ liệu CSV (trong thư mục data/datasets/):
              </label>
              <select
                value={csvFile}
                onChange={(e) => setCsvFile(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:border-teal-500 focus:outline-none"
              >
                {datasets.map((d) => (
                  <option key={d.name} value={d.name}>
                    {d.name} ({d.size_kb} KB)
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">
                Muốn đổi tệp dữ liệu, chỉ cần thả tệp `.csv` vào thư mục `data/datasets/`.
              </p>
            </div>

            {/* Order selection */}
            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1.5">Thứ tự đọc dữ liệu CSV:</label>
              <select
                value={csvOrder}
                onChange={(e) => setCsvOrder(e.target.value as any)}
                className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:border-teal-500 focus:outline-none"
              >
                <option value="sequential">Tuần tự từ trên xuống dưới (Mặc định)</option>
                <option value="random">Xáo trộn ngẫu nhiên (Random with seed)</option>
                <option value="by_date">Sắp xếp theo ngày quan trắc (By Date)</option>
              </select>
            </div>

            {/* Interval slider */}
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-800">Chu kỳ cập nhật số liệu:</span>
                <span className="font-mono text-sm font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-200">
                  {intervalSec.toFixed(1)} giây
                </span>
              </div>
              <input
                type="range"
                min="1.0"
                max="15.0"
                step="0.5"
                value={intervalSec}
                onChange={(e) => setIntervalSec(parseFloat(e.target.value))}
                className="w-full accent-teal-600 cursor-pointer"
              />
            </div>
          </div>
        </Card>

        {/* Right: Anomaly Detection & Registered Devices */}
        <div className="space-y-6">
          {/* Anomaly Model Settings */}
          <Card
            title="Thuật toán & Ngưỡng Phát hiện Bất thường"
            subtitle="Độ nhạy và kích thước cửa sổ trượt suy luận"
            icon={<Sliders className="h-4 w-4 text-teal-600" />}
          >
            <div className="space-y-5">
              {/* Threshold Slider */}
              <div>
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="font-semibold text-slate-800">Ngưỡng Anomaly Threshold:</span>
                  <span className="font-mono text-sm font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-200">
                    {threshold.toFixed(2)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.15"
                  max="0.65"
                  step="0.01"
                  value={threshold}
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-full accent-teal-600 cursor-pointer"
                />
                <div className="flex justify-between text-[11px] text-slate-400 mt-1">
                  <span>0.15 (Nhạy cao)</span>
                  <span>0.35 (Hiệu chuẩn chuẩn)</span>
                  <span>0.65 (Nghiêm ngặt)</span>
                </div>
              </div>

              {/* Window Size Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1.5">
                  Kích thước Cửa sổ trượt (Window Size):
                </label>
                <input
                  type="number"
                  min="5"
                  max="100"
                  value={windowSize}
                  onChange={(e) => setWindowSize(parseInt(e.target.value) || 30)}
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-slate-800 focus:border-teal-500 focus:outline-none"
                />
              </div>

              {/* Detector Type selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1.5">Kiến trúc Mô hình:</label>
                <select
                  value={detectorType}
                  onChange={(e) => setDetectorType(e.target.value as any)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 focus:border-teal-500 focus:outline-none"
                >
                  <option value="rule_based">Rule-Based Centroid Deviation (Hiện tại - Đã hiệu chuẩn)</option>
                  <option value="onnx">Mô hình ONNX Runtime (Gắn từ data/models/)</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Connected Devices List */}
          <Card
            title={`Thiết bị Ngoại vi (${devices.length} thiết bị)`}
            subtitle="Danh sách các Raspberry Pi / vi điều khiển đã kết nối vào hệ thống"
            icon={<HardDrive className="h-4 w-4 text-teal-600" />}
          >
            {devices.length === 0 ? (
              <div className="py-4 text-center text-xs text-slate-400">
                Chưa có thiết bị nào kết nối. Để kết nối, gửi dữ liệu qua MQTT (`devices/+/telemetry`) hoặc HTTP (`POST /api/v1/ingest`).
              </div>
            ) : (
              <div className="divide-y divide-slate-100 max-h-40 overflow-y-auto">
                {devices.map((dev) => (
                  <div key={dev.device_id} className="py-2.5 flex items-center justify-between text-xs">
                    <div>
                      <span className="font-bold text-slate-800">{dev.device_id}</span>
                      <span className="text-slate-400 ml-2">({dev.transport.toUpperCase()})</span>
                      <p className="text-[10px] text-slate-400">Gần nhất: {dev.last_seen.slice(11, 19)}</p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                        dev.is_online
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : 'bg-slate-100 text-slate-500 border-slate-200'
                      }`}
                    >
                      {dev.is_online ? 'Trực tuyến' : 'Ngoại tuyến'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pt-2">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-600 px-6 py-3 text-xs font-semibold text-white hover:bg-teal-700 shadow-md shadow-teal-600/20 transition-colors cursor-pointer"
        >
          <Save className="h-4 w-4" />
          <span>{saving ? 'Đang lưu cấu hình...' : 'Lưu & Áp dụng Cấu hình'}</span>
        </button>
      </div>
    </div>
  );
};
