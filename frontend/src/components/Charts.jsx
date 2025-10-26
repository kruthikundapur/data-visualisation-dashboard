import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Charts = ({ filters = {} }) => {
  const { id } = useParams();
  const [chartData, setChartData] = useState(null);
  const [chartConfig, setChartConfig] = useState({
    chartType: 'bar',
    xAxis: '',
    yAxis: '',
    aggregation: 'count'
  });
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (id) {
      fetchColumns();
    }
  }, [id]);

  useEffect(() => {
    if (chartConfig.xAxis && id) {
      generateChart();
    }
  }, [chartConfig, filters, id]);

  const fetchColumns = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/data/columns/${id}`);
      if (response.data.columns && response.data.columns.length > 0) {
        setColumns(response.data.columns);
        setChartConfig(prev => ({ 
          ...prev, 
          xAxis: prev.xAxis || response.data.columns[0] 
        }));
      }
    } catch (error) {
      console.error('Error fetching columns:', error);
    }
  };

  const generateChart = async () => {
    if (!chartConfig.xAxis || !id) return;

    try {
      const response = await axios.post('http://localhost:8000/charts/data', {
        dataset_id: parseInt(id),
        chart_type: chartConfig.chartType,
        x_axis: chartConfig.xAxis,
        y_axis: chartConfig.yAxis || null,
        aggregation: chartConfig.aggregation,
        filters: filters || {}
      });

      setChartData(response.data);
    } catch (error) {
      console.error('Error generating chart:', error);
    }
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${chartConfig.chartType.toUpperCase()} Chart`,
      },
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6">
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <select
          value={chartConfig.chartType}
          onChange={(e) => setChartConfig(prev => ({ ...prev, chartType: e.target.value }))}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        >
          <option value="bar">Bar Chart</option>
          <option value="line">Line Chart</option>
          <option value="pie">Pie Chart</option>
        </select>

        <select
          value={chartConfig.xAxis}
          onChange={(e) => setChartConfig(prev => ({ ...prev, xAxis: e.target.value }))}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        >
          <option value="">Select X-Axis</option>
          {columns.map(col => (
            <option key={col} value={col}>{col}</option>
          ))}
        </select>

        {chartConfig.chartType !== 'pie' && (
          <select
            value={chartConfig.yAxis}
            onChange={(e) => setChartConfig(prev => ({ ...prev, yAxis: e.target.value }))}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="">Select Y-Axis</option>
            {columns.map(col => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        )}

        {chartConfig.chartType !== 'pie' && (
          <select
            value={chartConfig.aggregation}
            onChange={(e) => setChartConfig(prev => ({ ...prev, aggregation: e.target.value }))}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          >
            <option value="count">Count</option>
            <option value="sum">Sum</option>
            <option value="mean">Average</option>
          </select>
        )}
      </div>

      {chartData && (
        <div className="mt-6">
          {chartData.chart_type === 'bar' && (
            <Bar data={chartData} options={chartOptions} />
          )}
          {chartData.chart_type === 'line' && (
            <Line data={chartData} options={chartOptions} />
          )}
          {chartData.chart_type === 'pie' && (
            <Pie data={chartData} options={chartOptions} />
          )}
        </div>
      )}
      {!chartData && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Select chart options above to generate visualization
        </div>
      )}
    </div>
  );
};

export default Charts;

