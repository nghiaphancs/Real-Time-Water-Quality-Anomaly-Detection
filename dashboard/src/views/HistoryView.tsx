import React, { useState, useEffect } from 'react';
import {
  Download,
  Filter,
  Search,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Table,
  LineChart as LineChartIcon,
} from 'lucide-react';
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
import { WaterMetric } from '../types';
import { Card } from '../components/ui/Card';

interface HistoryViewProps {
  liveHistory: WaterMetric[];
}

export const HistoryView: React.FC<HistoryViewProps> = ({ liveHistory }) => {
  const [data, setData] = useState<WaterMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [filterStation, setFilterStation] = useState<string>('ALL');
  const [filterPrediction, setFilterPrediction] = useState<string>('ALL');
  const [selectedFeature, setSelectedFeature] = useState<string>('pH');
  const [search, setSearch] = useState<string>('');

  const fetchHistory = () => {
    setLoading(true);
    fetch(`http://${window.location.hostname}:8000/api/history?limit=150`)
      .then((res) => res.json())
      .then((items: WaterMetric[]) => {
        if (Array.isArray(items) && items.length > 0) {
          setData(items);
        } else {
          setData(liveHistory);
        }
      })
      .catch(() => {
        setData(liveHistory);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Sync with live history if new items arrived
  useEffect(() => {
    if (liveHistory.length > 0 && data.length === 0) {
      setData(liveHistory);
    }
  }, [liveHistory]);

  // Unique stations
  const stations = Array.from(new Set(data.map((d) => d.station).filter(Boolean)));

  // Filtered dataset
  const filteredData = data.filter((item) => {
    const matchStation = filterStation === 'ALL' || item.station === filterStation;
    const matchPrediction = filterPrediction === 'ALL' || item.prediction === filterPrediction;
    const matchSearch =
      search === '' ||
      item.station.toLowerCase().includes(search.toLowerCase()) ||
      item.sensor_timestamp.includes(search) ||
      (item.city && item.city.toLowerCase().includes(search.toLowerCase()));
    return matchStation && matchPrediction && matchSearch;
  });

  // Export CSV handler
  const handleExportCSV = () => {
    window.open(`http://${window.location.hostname}:8000/api/export`, '_blank');
  };

  // Calculations for summary stats
  const totalCount = filteredData.length;
  const anomalyCount = filteredData.filter((d) => d.prediction === 'ANOMALY').length;
  const avgPh = totalCount > 0 ? (filteredData.reduce((acc, d) => acc + d.pH, 0) / totalCount).toFixed(2) : '--';
  const avgDo = totalCount > 0 ? (filteredData.reduce((acc, d) => acc + d.DO, 0) / totalCount).toFixed(2) : '--';
  const maxTurbidity = totalCount > 0 ? Math.max(...filteredData.map((d) => d.turbidity)).toFixed(2) : '--';

  // Chart data
  const chartItems = filteredData.slice(-40).map((d) => ({
    time: d.sensor_timestamp.slice(-5) || d.sensor_timestamp,
    [selectedFeature]: d[selectedFeature as keyof WaterMetric],
    anomaly: d.prediction === 'ANOMALY' ? d[selectedFeature as keyof WaterMetric] : null,
  }));

  return (
    <div className="space-y-6">
      {/* Top action row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Lịch sử Đo & Nhật ký Kiểm chuẩn</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Dữ liệu ghi nhận từ mô hình Edge AI và tệp lưu trữ benchmark_log.csv
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchHistory}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Làm mới</span>
          </button>

          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-1.5 rounded-xl bg-teal-600 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-700 shadow-xs shadow-teal-600/20 transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Xuất file CSV</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Tổng mẫu ghi nhận</span>
          <div className="text-2xl font-extrabold text-slate-800 mt-1">{totalCount}</div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Bất thường phát hiện</span>
          <div className="text-2xl font-extrabold text-red-600 mt-1 flex items-baseline gap-1">
            <span>{anomalyCount}</span>
            <span className="text-xs text-slate-400">({totalCount > 0 ? ((anomalyCount / totalCount) * 100).toFixed(1) : 0}%)</span>
          </div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">pH trung bình</span>
          <div className="text-2xl font-extrabold text-teal-700 mt-1">{avgPh}</div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">DO trung bình</span>
          <div className="text-2xl font-extrabold text-blue-600 mt-1">{avgDo} <span className="text-xs font-normal text-slate-400">mg/L</span></div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200/80 p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Độ đục cao nhất</span>
          <div className="text-2xl font-extrabold text-amber-600 mt-1">{maxTurbidity} <span className="text-xs font-normal text-slate-400">NTU</span></div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Search Box */}
            <div className="relative min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="Tìm trạm, thành phố, ngày..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50/50 pl-9 pr-3 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:bg-white focus:border-teal-500 focus:outline-none"
              />
            </div>

            {/* Station Filter */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-medium">Trạm:</span>
              <select
                value={filterStation}
                onChange={(e) => setFilterStation(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-teal-500 focus:outline-none"
              >
                <option value="ALL">Tất cả trạm ({stations.length})</option>
                {stations.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            {/* Prediction Filter */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-500 font-medium">Trạng thái:</span>
              <select
                value={filterPrediction}
                onChange={(e) => setFilterPrediction(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-teal-500 focus:outline-none"
              >
                <option value="ALL">Tất cả (Mọi trạng thái)</option>
                <option value="NORMAL">Bình thường (NORMAL)</option>
                <option value="ANOMALY">Bất thường (ANOMALY)</option>
              </select>
            </div>
          </div>

          {/* Feature selector for historical chart */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-slate-500 mr-1">Xem biểu đồ:</span>
            {['pH', 'DO', 'turbidity', 'EC', 'temperature'].map((f) => (
              <button
                key={f}
                onClick={() => setSelectedFeature(f)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                  selectedFeature === f
                    ? 'bg-teal-600 text-white font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Dynamic Feature Line Chart */}
        <div className="h-60 w-full mt-5 pt-4 border-t border-slate-100">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartItems} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  border: '1px solid #e2e8f0',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
              <Line
                type="monotone"
                dataKey={selectedFeature}
                stroke="#00A89D"
                strokeWidth={2}
                dot={{ r: 2 }}
                activeDot={{ r: 5 }}
                name={`Giá trị ${selectedFeature}`}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Historical Data Table */}
      <Card
        title={`Bảng Dữ liệu Chi tiết (${filteredData.length} mẫu)`}
        subtitle="Hiển thị thông số 5 cảm biến, kết quả suy luận AI và độ trễ biên"
        icon={<Table className="h-4 w-4 text-teal-600" />}
      >
        <div className="overflow-x-auto -mx-5 -mb-5">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 text-slate-500 font-semibold uppercase tracking-wider border-y border-slate-200/80">
              <tr>
                <th className="py-3 px-4">Thời gian</th>
                <th className="py-3 px-4">Trạm quan trắc</th>
                <th className="py-3 px-3 text-right">pH</th>
                <th className="py-3 px-3 text-right">DO (mg/L)</th>
                <th className="py-3 px-3 text-right">Độ đục (NTU)</th>
                <th className="py-3 px-3 text-right">EC (µS/cm)</th>
                <th className="py-3 px-3 text-right">Nhiệt độ (°C)</th>
                <th className="py-3 px-3 text-center">Score</th>
                <th className="py-3 px-4 text-center">Trạng thái</th>
                <th className="py-3 px-3 text-right">Độ trễ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-400">
                    Không tìm thấy bản ghi nào phù hợp với bộ lọc.
                  </td>
                </tr>
              ) : (
                filteredData.slice(-50).reverse().map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-medium text-slate-700 whitespace-nowrap">
                      {row.sensor_timestamp || row.received_at?.slice(0, 19)}
                    </td>
                    <td className="py-3 px-4 text-slate-600 whitespace-nowrap">
                      <div className="font-semibold text-slate-800">{row.station || 'Station_1'}</div>
                      <div className="text-[10px] text-slate-400">{row.city}</div>
                    </td>
                    <td className="py-3 px-3 text-right font-semibold text-slate-800">{row.pH.toFixed(2)}</td>
                    <td className="py-3 px-3 text-right text-slate-700">{row.DO.toFixed(2)}</td>
                    <td className="py-3 px-3 text-right text-slate-700">{row.turbidity.toFixed(2)}</td>
                    <td className="py-3 px-3 text-right text-slate-700">{row.EC.toFixed(1)}</td>
                    <td className="py-3 px-3 text-right text-slate-700">{row.temperature.toFixed(2)}</td>
                    <td className="py-3 px-3 text-center font-mono text-[11px] text-slate-600">
                      {row.anomaly_score.toFixed(4)}
                    </td>
                    <td className="py-3 px-4 text-center whitespace-nowrap">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                          row.prediction === 'ANOMALY'
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {row.prediction === 'ANOMALY' ? (
                          <>
                            <AlertTriangle className="h-3 w-3" />
                            <span>Bất thường</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="h-3 w-3" />
                            <span>Bình thường</span>
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-slate-500 whitespace-nowrap">
                      {row.inference_latency_ms} ms
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
