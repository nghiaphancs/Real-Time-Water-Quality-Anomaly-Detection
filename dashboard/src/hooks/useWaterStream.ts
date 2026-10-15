import { useState, useEffect, useRef } from 'react';
import mqtt from 'mqtt';
import { WaterMetric } from '../types';

const HOST = window.location.hostname || '127.0.0.1';
const MQTT_WS_URL = (import.meta as any).env?.VITE_MQTT_WS || `ws://${HOST}:9001`;
const BACKEND_WS_URL = `ws://${HOST}:8000/ws/live`;
const BACKEND_REST_URL = (import.meta as any).env?.VITE_API_BASE
  ? `${(import.meta as any).env.VITE_API_BASE}/api/v1/latest`
  : `http://${HOST}:8000/api/v1/latest`;

const DEFAULT_INTERVAL_SEC = 6;

export function useWaterStream() {
  const [current, setCurrent] = useState<WaterMetric | null>(null);
  const [history, setHistory] = useState<WaterMetric[]>([]);
  const [alerts, setAlerts] = useState<WaterMetric[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const [connectionType, setConnectionType] = useState<'MQTT' | 'WebSocket' | 'REST'>('MQTT');
  const [countdown, setCountdown] = useState<number>(DEFAULT_INTERVAL_SEC);
  const [refreshIntervalSec, setRefreshIntervalSec] = useState<number>(DEFAULT_INTERVAL_SEC);

  const lastSeqRef = useRef<number>(-1);
  const lastSampleTimeRef = useRef<number>(Date.now());

  const handleNewMetric = (metric: WaterMetric) => {
    if (!metric || metric.seq === undefined) return;

    // Deduplication by monotonic sequence number (seq)
    if (metric.seq === lastSeqRef.current) return;
    lastSeqRef.current = metric.seq;

    setCurrent(metric);
    lastSampleTimeRef.current = Date.now();
    setCountdown(refreshIntervalSec);

    setHistory((prev) => {
      const updated = [...prev, metric];
      return updated.slice(-60); // Keep last 60 points
    });

    if (metric.prediction === 'ANOMALY') {
      setAlerts((prev) => {
        if (prev.some((a) => a.event_id === metric.event_id || a.seq === metric.seq)) {
          return prev;
        }
        return [metric, ...prev].slice(0, 50);
      });
    }
  };

  // 1. Initial REST fetch
  useEffect(() => {
    fetch(BACKEND_REST_URL)
      .then((res) => res.json())
      .then((data: any) => {
        if (data && data.seq !== undefined) {
          handleNewMetric(data);
        }
      })
      .catch((err) => console.log('[REST Initial] error:', err));
  }, []);

  // 2. 1-second interval timer for countdown
  useEffect(() => {
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - lastSampleTimeRef.current) / 1000);
      const remaining = Math.max(0, refreshIntervalSec - (elapsed % refreshIntervalSec));
      setCountdown(remaining);
    }, 1000);
    return () => clearInterval(timer);
  }, [refreshIntervalSec]);

  // 3. Robust Stream Manager: MQTT-over-WebSocket -> Backend WebSocket -> REST Polling fallback
  useEffect(() => {
    let mqttClient: mqtt.MqttClient | null = null;
    let wsClient: WebSocket | null = null;
    let pollInterval: any = null;
    let isCleanedUp = false;

    function startRestPolling() {
      if (isCleanedUp || pollInterval) return;
      setConnectionType('REST');
      pollInterval = setInterval(() => {
        fetch(BACKEND_REST_URL)
          .then((res) => res.json())
          .then((data: any) => {
            if (data && data.seq !== undefined) {
              setConnectionStatus('connected');
              handleNewMetric(data);
            }
          })
          .catch(() => setConnectionStatus('disconnected'));
      }, refreshIntervalSec * 1000);
    }

    function connectBackendWebSocket() {
      if (isCleanedUp) return;
      try {
        wsClient = new WebSocket(BACKEND_WS_URL);
        wsClient.onopen = () => {
          if (!isCleanedUp) {
            setConnectionStatus('connected');
            setConnectionType('WebSocket');
          }
        };
        wsClient.onmessage = (event) => {
          try {
            const metric: WaterMetric = JSON.parse(event.data);
            handleNewMetric(metric);
          } catch (e) {
            console.error('[WS] Parse error:', e);
          }
        };
        wsClient.onerror = () => startRestPolling();
        wsClient.onclose = () => {
          if (!isCleanedUp) startRestPolling();
        };
      } catch {
        startRestPolling();
      }
    }

    // Try MQTT over WebSocket (Port 9001) first
    try {
      mqttClient = mqtt.connect(MQTT_WS_URL, {
        keepalive: 30,
        reconnectPeriod: 4000,
        connectTimeout: 4000,
      });

      mqttClient.on('connect', () => {
        if (!isCleanedUp) {
          setConnectionStatus('connected');
          setConnectionType('MQTT');
          mqttClient?.subscribe('water_quality/result', (err) => {
            if (err) console.error('[MQTT WS] Subscribe error:', err);
          });
        }
      });

      mqttClient.on('message', (_topic, message) => {
        try {
          const metric: WaterMetric = JSON.parse(message.toString());
          handleNewMetric(metric);
        } catch (e) {
          console.error('[MQTT WS] Parse error:', e);
        }
      });

      mqttClient.on('error', () => {
        if (!isCleanedUp && connectionType !== 'WebSocket') {
          connectBackendWebSocket();
        }
      });

      mqttClient.on('close', () => {
        if (!isCleanedUp && connectionType === 'MQTT') {
          connectBackendWebSocket();
        }
      });
    } catch {
      connectBackendWebSocket();
    }

    return () => {
      isCleanedUp = true;
      if (mqttClient) mqttClient.end(true);
      if (wsClient) wsClient.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [refreshIntervalSec]);

  return {
    current,
    history,
    alerts,
    connectionStatus,
    connectionType,
    countdown,
    refreshIntervalSec,
    setRefreshIntervalSec,
    clearAlerts: () => setAlerts([]),
  };
}
