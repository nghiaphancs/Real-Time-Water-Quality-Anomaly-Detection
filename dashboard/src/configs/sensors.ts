export interface SensorMeta {
  key: string;
  name: string;
  nameVi: string;
  unit: string;
  min: number;
  max: number;
  safeMin: number;
  safeMax: number;
  color: string;
  description: string;
}

export const SENSORS: Record<string, SensorMeta> = {
  pH: {
    key: 'pH',
    name: 'pH Level',
    nameVi: 'Độ kiềm/axit (pH)',
    unit: 'pH',
    min: 5.34,
    max: 8.76,
    safeMin: 6.5,
    safeMax: 8.5,
    color: '#00A89D',
    description: 'Chỉ số đo tính axit hoặc bazơ của nước. Nước uống và sinh hoạt an toàn trong khoảng 6.5 - 8.5.',
  },
  DO: {
    key: 'DO',
    name: 'Dissolved Oxygen',
    nameVi: 'Oxy hòa tan (DO)',
    unit: 'mg/L',
    min: 1.47,
    max: 14.49,
    safeMin: 5.0,
    safeMax: 12.0,
    color: '#0284C7',
    description: 'Lượng dưỡng khí oxy hòa tan cần thiết cho hệ sinh thái thủy sinh và quá trình tự làm sạch nguồn nước.',
  },
  turbidity: {
    key: 'turbidity',
    name: 'Turbidity',
    nameVi: 'Độ đục',
    unit: 'NTU',
    min: 0.0,
    max: 47.48,
    safeMin: 0.0,
    safeMax: 5.0,
    color: '#F59E0B',
    description: 'Độ vẩn đục do chất rắn lơ lửng, bùn cát hữu cơ/vô cơ trong nước. Độ đục cao làm giảm chất lượng nước.',
  },
  EC: {
    key: 'EC',
    name: 'Conductivity',
    nameVi: 'Độ dẫn điện (EC)',
    unit: 'µS/cm',
    min: 136.85,
    max: 842.89,
    safeMin: 200.0,
    safeMax: 800.0,
    color: '#8B5CF6',
    description: 'Khả năng dẫn điện thể hiện tổng lượng ion khoáng hòa tan (TDS) trong khối nước.',
  },
  temperature: {
    key: 'temperature',
    name: 'Temperature',
    nameVi: 'Nhiệt độ nước',
    unit: '°C',
    min: 3.39,
    max: 36.77,
    safeMin: 15.0,
    safeMax: 30.0,
    color: '#EC4899',
    description: 'Nhiệt độ môi trường nước tại trạm đo quan trắc. Ảnh hưởng trực tiếp đến khả năng hòa tan oxy.',
  },
};

export const DEFAULT_SAMPLE_INTERVAL_SEC = 6;
