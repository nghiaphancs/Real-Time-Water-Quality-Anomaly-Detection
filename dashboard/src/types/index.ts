export interface WaterMetric {
  event_id?: string;
  seq: number;
  source?: string;
  device_id?: string;
  received_at: string;
  sensor_timestamp: string;
  station: string;
  city: string;
  province?: string;
  pH: number;
  DO: number;
  turbidity: number;
  EC: number;
  temperature: number;
  wqi?: number;
  pollution_level?: string;
  remarks?: string;
  prediction: 'NORMAL' | 'ANOMALY';
  anomaly_score: number;
  threshold: number;
  warming_up?: boolean;
  contributing_features?: string[];
  inference_latency_ms: number;
  end_to_end_latency_ms: number;
  model_size_kb: number;
  system_cpu_pct: number;
  system_ram_pct: number;
  process_ram_mb: number;
  throughput_msg_per_sec: number;
  buffer_current?: number;
  buffer_max?: number;
}

export interface SystemMetrics {
  current: WaterMetric;
  sample_count: number;
  anomaly_count: number;
  anomaly_rate_pct: number;
  avg_inference_latency_ms: number;
  avg_e2e_latency_ms: number;
  model_size_kb: number;
  system_cpu_pct: number;
  system_ram_pct: number;
  process_ram_mb: number;
  throughput_msg_per_sec: number;
}

export interface DatasetItem {
  name: string;
  size_kb: number;
  is_active: boolean;
}

export interface DeviceInfo {
  device_id: string;
  transport: string;
  last_seen: string;
  is_online: boolean;
  last_seq: number;
  sample_count: number;
  meta: Record<string, any>;
}

export interface EdgeConfig {
  app: {
    name: string;
    version: string;
    env: string;
  };
  source: {
    mode: 'csv' | 'device' | 'auto';
    csv: {
      file: string;
      mapping: string;
      order: 'sequential' | 'random' | 'by_date';
      loop: boolean;
      interval_sec: number;
      station?: string | null;
    };
    device: {
      timeout_sec: number;
    };
  };
  detector: {
    type: 'rule_based' | 'onnx';
    threshold: number;
    window_size: number;
    warmup_samples: number;
  };
  mqtt: {
    broker: string;
    port: number;
    ws_port: number;
  };
}

export type ActiveTab = 'live' | 'history' | 'alerts' | 'performance' | 'settings';
