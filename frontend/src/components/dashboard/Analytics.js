import React, { useRef, useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { fetchWeeklyAdherenceData } from "../../services/api";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Helper function to format date label
const formatDateLabel = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
};

// Function to dynamically color the data points and line
const getColorBasedOnAdherence = (adherenceValue) => {
  if (adherenceValue === 100) {
    return {
      borderColor: "rgb(34, 197, 94)", // Green for perfect adherence
      backgroundColor: "rgba(34, 197, 94, 0.2)", // Light green fill
    };
  } else if (adherenceValue >= 80) {
    return {
      borderColor: "rgb(234, 179, 8)", // Yellow/amber for good adherence
      backgroundColor: "rgba(234, 179, 8, 0.2)", // Light amber fill
    };
  } else {
    return {
      borderColor: "rgb(239, 68, 68)", // Red for poor adherence
      backgroundColor: "rgba(239, 68, 68, 0.2)", // Light red fill
    };
  }
};

const Analytics = () => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const chartRef = useRef(null);

  useEffect(() => {
    const fetchAdherenceData = async () => {
      try {
        setLoading(true);
        const response = await fetchWeeklyAdherenceData();
        
        console.log("Raw API Response:", response);

        // Check if response is an array or has a data property
        const adherenceData = Array.isArray(response) 
          ? response 
          : (response.data || []);

        if (adherenceData.length === 0) {
          setError("No adherence data available");
          setLoading(false);
          return;
        }

        const labels = adherenceData.map(item => formatDateLabel(item.date));
        const values = adherenceData.map(item => item.adherence);

        // Create dynamic color scheme based on adherence
        const dynamicColors = values.map(value => 
          getColorBasedOnAdherence(value)
        );

        setChartData({
          labels,
          datasets: [
            {
              label: "Daily Medication Adherence (%)",
              data: values,
              fill: true,
              tension: 0.4,
              borderWidth: 2,
              pointRadius: 6,
              pointHoverRadius: 8,
              ...dynamicColors[0], // Use the first color scheme as default
              pointBackgroundColor: values.map((value, index) => 
                dynamicColors[index].borderColor
              ),
            },
          ],
        });
        setLoading(false);
      } catch (err) {
        console.error("Full Error Object:", err);
        console.error("Error fetching adherence data:", err.message);
        setError(`Failed to load adherence data: ${err.message}`);
        setLoading(false);
      }
    };

    fetchAdherenceData();

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  if (loading) return <p>Loading adherence data...</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!chartData) return <p>No adherence data available</p>;

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow-md h-96">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        Daily Medication Adherence
      </h3>
      <div style={{ position: "relative", height: "100%" }}>
        <Line
          ref={chartRef}
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Adherence (%)'
                },
                grid: {
                  color: (context) => {
                    if (context.tick.value === 100) {
                      return 'rgba(34, 197, 94, 0.2)'; // Highlight perfect adherence line
                    }
                    return 'rgba(0, 0, 0, 0.1)';
                  }
                }
              }
            },
            plugins: {
              legend: { display: true },
              title: {
                display: true,
                text: 'Medication Adherence Over Last 7 Days',
                font: {
                  size: 16
                }
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return `Adherence: ${context.parsed.y}%`;
                  }
                }
              }
            },
            interaction: {
              mode: 'nearest',
              intersect: false,
            }
          }}
        />
      </div>
    </div>
  );
};

export default Analytics;