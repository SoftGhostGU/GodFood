import React from 'react';
import { Gauge } from '@ant-design/charts';

interface GaugeChartProps {
  option: any;
  style?: React.CSSProperties;
}

const GaugeChart: React.FC<GaugeChartProps> = ({ option, style }) => {
  const config = {
    ...option,
    width: style?.width || 400,
    height: style?.height || 300,
  };

  return <Gauge {...config} />;
};

export default GaugeChart;