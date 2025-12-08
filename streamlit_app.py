import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Droplets, ThermometerSun, AlertTriangle, TrendingUp, Database } from 'lucide-react';

const WaterQualityDashboard = () => {
  const [ph, setPh] = useState(7.5);
  const [temperature, setTemperature] = useState(28.0);
  const [prediction, setPrediction] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(false);

  // Initialize with sample historical data
  useEffect(() => {
    const generateHistoricalData = () => {
      const data = [];
      const now = new Date();
      for (let i = 30; i >= 0; i--) {
        const date = new Date(now - i * 24 * 60 * 60 * 1000);
        data.push({
          timestamp: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          fullDate: date,
          pH: 7.0 + Math.random() * 2,
          temperature: 25 + Math.random() * 6,
          ammonia: 0.1 + Math.random() * 0.4
        });
      }
      return data;
    };
    setHistoricalData(generateHistoricalData());
  }, []);

  // Simulate real-time sensor updates
  useEffect(() => {
    if (realTimeMode) {
      const interval = setInterval(() => {
        const newPh = 7.0 + Math.random() * 2;
        const newTemp = 25 + Math.random() * 6;
        setPh(parseFloat(newPh.toFixed(2)));
        setTemperature(parseFloat(newTemp.toFixed(2)));
        
        // Add to historical data
        const now = new Date();
        setHistoricalData(prev => {
          const newData = [...prev, {
            timestamp: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            fullDate: now,
            pH: newPh,
            temperature: newTemp,
            ammonia: predictAmmonia(newPh, newTemp)
          }];
          return newData.slice(-50); // Keep last 50 readings
        });
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [realTimeMode]);

  // Simple ML prediction model (mimics trained model)
  const predictAmmonia = (phValue, tempValue) => {
    // Simplified prediction based on pH and temperature relationship
    // Higher pH + Higher temp = Higher ammonia
    const phFactor = (phValue - 7.0) * 0.08;
    const tempFactor = (tempValue - 25.0) * 0.015;
    const baseAmmonia = 0.15;
    const predicted = baseAmmonia + phFactor + tempFactor + (Math.random() * 0.05);
    return Math.max(0, predicted);
  };

  const handlePredict = () => {
    setLoading(true);
    setTimeout(() => {
      const ammoniaPrediction = predictAmmonia(ph, temperature);
      setPrediction(ammoniaPrediction);
      setLoading(false);
      
      // Add to historical data
      const now = new Date();
      setHistoricalData(prev => [...prev, {
        timestamp: now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        fullDate: now,
        pH: ph,
        temperature: temperature,
        ammonia: ammoniaPrediction
      }].slice(-50));
    }, 500);
  };

  const getRiskLevel = (ammoniaLevel) => {
    if (ammoniaLevel < 0.2) return { level: 'Low', color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' };
    if (ammoniaLevel < 0.4) return { level: 'Moderate', color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' };
    return { level: 'High', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' };
  };

  const getPrescriptiveAdvice = (phValue, tempValue, ammoniaLevel) => {
    const advice = [];
    
    if (phValue > 8.0 && tempValue > 28.0) {
      advice.push({
        priority: 'High',
        icon: '🔴',
        message: 'Critical: Both pH and temperature are elevated. Immediate water change recommended (30-40%).',
        action: 'Perform partial water change and increase aeration'
      });
    } else if (phValue > 8.0) {
      advice.push({
        priority: 'Medium',
        icon: '🟡',
        message: 'pH is elevated. This increases ammonia toxicity.',
        action: 'Add pH buffer or perform gradual water change'
      });
    } else if (tempValue > 28.0) {
      advice.push({
        priority: 'Medium',
        icon: '🟡',
        message: 'Water temperature is high. Reduce temperature to prevent ammonia formation.',
        action: 'Increase aeration, reduce feeding, or add cooling system'
      });
    }

    if (ammoniaLevel > 0.4) {
      advice.push({
        priority: 'High',
        icon: '🔴',
        message: 'High ammonia detected! Immediate action required.',
        action: 'Stop feeding, perform 40-50% water change, add ammonia neutralizer'
      });
    } else if (ammoniaLevel > 0.2) {
      advice.push({
        priority: 'Medium',
        icon: '🟡',
        message: 'Moderate ammonia levels. Monitor closely.',
        action: 'Reduce feeding by 50%, increase monitoring frequency'
      });
    } else {
      advice.push({
        priority: 'Low',
        icon: '🟢',
        message: 'Water quality is within acceptable range.',
        action: 'Continue regular monitoring and maintenance'
      });
    }

    return advice;
  };

  const risk = prediction !== null ? getRiskLevel(prediction) : null;
  const prescriptiveAdvice = prediction !== null ? getPrescriptiveAdvice(ph, temperature, prediction) : [];

  // Calculate statistics
  const stats = historicalData.length > 0 ? {
    avgPh: (historicalData.reduce((sum, d) => sum + d.pH, 0) / historicalData.length).toFixed(2),
    avgTemp: (historicalData.reduce((sum, d) => sum + d.temperature, 0) / historicalData.length).toFixed(2),
    avgAmmonia: (historicalData.reduce((sum, d) => sum + d.ammonia, 0) / historicalData.length).toFixed(3),
    maxAmmonia: Math.max(...historicalData.map(d => d.ammonia)).toFixed(3)
  } : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center gap-3">
            <Droplets className="w-10 h-10 text-blue-500" />
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Water Quality Monitoring System</h1>
              <p className="text-gray-600">Real-time Ammonia Prediction with ML Analytics</p>
            </div>
          </div>
        </div>

        {/* Real-time Toggle */}
        <div className="bg-white rounded-xl shadow-md p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className={`w-5 h-5 ${realTimeMode ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} />
            <span className="font-medium text-gray-700">Sensor Connection Mode</span>
          </div>
          <button
            onClick={() => setRealTimeMode(!realTimeMode)}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              realTimeMode 
                ? 'bg-green-500 text-white hover:bg-green-600' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {realTimeMode ? 'Live Monitoring Active' : 'Enable Real-time Mode'}
          </button>
        </div>

        {/* Input Section */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* pH Input */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-blue-500" />
                pH Level
              </div>
            </label>
            <div className="space-y-3">
              <input
                type="number"
                value={ph}
                onChange={(e) => setPh(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                max="14"
                disabled={realTimeMode}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none text-lg font-medium disabled:bg-gray-100"
              />
              <input
                type="range"
                value={ph}
                onChange={(e) => setPh(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                max="14"
                disabled={realTimeMode}
                className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
              />
              <div className="text-sm text-gray-600">Current: <span className="font-bold text-blue-600">{ph.toFixed(2)}</span></div>
            </div>
          </div>

          {/* Temperature Input */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              <div className="flex items-center gap-2 mb-2">
                <ThermometerSun className="w-5 h-5 text-orange-500" />
                Temperature (°C)
              </div>
            </label>
            <div className="space-y-3">
              <input
                type="number"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                max="40"
                disabled={realTimeMode}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:outline-none text-lg font-medium disabled:bg-gray-100"
              />
              <input
                type="range"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                max="40"
                disabled={realTimeMode}
                className="w-full h-2 bg-orange-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
              />
              <div className="text-sm text-gray-600">Current: <span className="font-bold text-orange-600">{temperature.toFixed(2)}°C</span></div>
            </div>
          </div>
        </div>

        {/* Predict Button */}
        <button
          onClick={handlePredict}
          disabled={loading || realTimeMode}
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : realTimeMode ? 'Auto-predicting...' : '🔍 Predict Ammonia Level'}
        </button>

        {/* Prediction Result */}
        {prediction !== null && (
          <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${risk.border}`}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">🔬 Prediction Result</h2>
                <p className="text-sm text-gray-600">Based on ML Model Analysis</p>
              </div>
              <div className={`px-4 py-2 rounded-lg ${risk.bg} border-2 ${risk.border}`}>
                <span className={`text-sm font-bold ${risk.color}`}>{risk.level} Risk</span>
              </div>
            </div>
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-6 mb-4">
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-1">Predicted Ammonia (mg/L)</div>
                <div className="text-5xl font-bold text-blue-600">{prediction.toFixed(4)}</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-sm text-gray-600">pH Input</div>
                <div className="text-xl font-bold text-gray-800">{ph.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Temperature</div>
                <div className="text-xl font-bold text-gray-800">{temperature.toFixed(2)}°C</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Risk Level</div>
                <div className={`text-xl font-bold ${risk.color}`}>{risk.level}</div>
              </div>
            </div>
          </div>
        )}

        {/* Prescriptive Analytics (Phase 6) */}
        {prescriptiveAdvice.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-6 h-6 text-orange-500" />
              <h2 className="text-xl font-bold text-gray-800">📋 Prescriptive Recommendations</h2>
            </div>
            <div className="space-y-3">
              {prescriptiveAdvice.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-2 ${
                    item.priority === 'High' ? 'border-red-200 bg-red-50' :
                    item.priority === 'Medium' ? 'border-yellow-200 bg-yellow-50' :
                    'border-green-200 bg-green-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{item.icon}</span>
                    <div className="flex-1">
                      <div className="font-semibold text-gray-800 mb-1">{item.message}</div>
                      <div className="text-sm text-gray-700 bg-white bg-opacity-50 p-2 rounded">
                        <span className="font-medium">Action:</span> {item.action}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl shadow-md p-4">
              <div className="text-sm text-gray-600 mb-1">Avg pH</div>
              <div className="text-2xl font-bold text-blue-600">{stats.avgPh}</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-4">
              <div className="text-sm text-gray-600 mb-1">Avg Temp</div>
              <div className="text-2xl font-bold text-orange-600">{stats.avgTemp}°C</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-4">
              <div className="text-sm text-gray-600 mb-1">Avg Ammonia</div>
              <div className="text-2xl font-bold text-purple-600">{stats.avgAmmonia}</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-4">
              <div className="text-sm text-gray-600 mb-1">Peak Ammonia</div>
              <div className="text-2xl font-bold text-red-600">{stats.maxAmmonia}</div>
            </div>
          </div>
        )}

        {/* Historical Trends Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl font-bold text-gray-800">📊 Historical Trends</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={historicalData.slice(-30)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="timestamp" stroke="#666" style={{ fontSize: '12px' }} />
              <YAxis stroke="#666" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
              />
              <Legend />
              <Line type="monotone" dataKey="pH" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} name="pH Level" />
              <Line type="monotone" dataKey="temperature" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} name="Temperature (°C)" />
              <Line type="monotone" dataKey="ammonia" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} name="Ammonia (mg/L)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Ammonia Risk Area Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Database className="w-6 h-6 text-purple-500" />
            <h2 className="text-xl font-bold text-gray-800">🎯 Ammonia Risk Timeline</h2>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={historicalData.slice(-30)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="timestamp" stroke="#666" style={{ fontSize: '12px' }} />
              <YAxis stroke="#666" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
              />
              <Area type="monotone" dataKey="ammonia" stroke="#8b5cf6" fill="#c4b5fd" name="Ammonia (mg/L)" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="mt-4 flex justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-400 rounded"></div>
              <span>Safe (&lt;0.2)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-400 rounded"></div>
              <span>Moderate (0.2-0.4)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-400 rounded"></div>
              <span>High (&gt;0.4)</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-800 text-white rounded-xl shadow-lg p-6 text-center">
          <p className="text-sm">🌊 Water Quality Monitoring System | Powered by ESP32, Firebase & ML Analytics</p>
          <p className="text-xs text-gray-400 mt-2">Phase 5: Real-time Visualization | Phase 6: Prescriptive Analytics ✓</p>
        </div>
      </div>
    </div>
  );
};

export default WaterQualityDashboard;
