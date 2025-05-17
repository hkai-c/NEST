import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';
import { trainingService, TrainingMetrics, TrainingStatus } from '../services/trainingService';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const MODEL_TYPES = ['emotion', 'chat', 'meditation'];
const CHART_WIDTH = Dimensions.get('window').width - 40;

export const TrainingDashboardScreen: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [metrics, setMetrics] = useState<TrainingMetrics[]>([]);
  const [loading, setLoading] = useState(false);
  const [trainingParams, setTrainingParams] = useState({
    epochs: 10,
    batch_size: 32,
    learning_rate: 0.001,
  });

  const fetchData = useCallback(async (modelType: string) => {
    try {
      setLoading(true);
      const [statusData, metricsData] = await Promise.all([
        trainingService.getTrainingStatus(modelType),
        trainingService.getTrainingMetrics(modelType),
      ]);
      setStatus(statusData);
      setMetrics(metricsData);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch training data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedModel) {
      fetchData(selectedModel);
      const interval = setInterval(() => fetchData(selectedModel), 5000);
      return () => clearInterval(interval);
    }
  }, [selectedModel, fetchData]);

  const handleStartTraining = async () => {
    try {
      setLoading(true);
      await trainingService.startTraining(selectedModel, trainingParams);
      Alert.alert('Success', 'Training started successfully');
      fetchData(selectedModel);
    } catch (error) {
      Alert.alert('Error', 'Failed to start training');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const renderMetrics = () => {
    if (!status?.metrics) return null;

    const { accuracy, loss, f1_score } = status.metrics;
    return (
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>Accuracy</Text>
          <Text style={styles.metricValue}>{(accuracy * 100).toFixed(2)}%</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>Loss</Text>
          <Text style={styles.metricValue}>{loss.toFixed(4)}</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>F1 Score</Text>
          <Text style={styles.metricValue}>{(f1_score * 100).toFixed(2)}%</Text>
        </View>
      </View>
    );
  };

  const renderCharts = () => {
    if (metrics.length === 0) return null;

    const chartData = {
      labels: metrics.map(m => new Date(m.timestamp).toLocaleTimeString()),
      datasets: [
        {
          data: metrics.map(m => m.loss),
          color: () => '#FF6384',
        },
        {
          data: metrics.map(m => m.accuracy * 100),
          color: () => '#36A2EB',
        },
        {
          data: metrics.map(m => m.f1_score * 100),
          color: () => '#4BC0C0',
        },
      ],
    };

    return (
      <View style={styles.chartContainer}>
        <LineChart
          data={chartData}
          width={CHART_WIDTH}
          height={220}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            decimalPlaces: 2,
            color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16,
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>AI Training Dashboard</Text>

      <View style={styles.modelSelector}>
        {MODEL_TYPES.map(model => (
          <TouchableOpacity
            key={model}
            style={[
              styles.modelButton,
              selectedModel === model && styles.selectedModelButton,
            ]}
            onPress={() => setSelectedModel(model)}
          >
            <Text
              style={[
                styles.modelButtonText,
                selectedModel === model && styles.selectedModelButtonText,
              ]}
            >
              {model.charAt(0).toUpperCase() + model.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {selectedModel && (
        <View style={styles.dashboard}>
          <View style={styles.statusContainer}>
            <Text style={styles.statusLabel}>Status:</Text>
            <Text style={styles.statusValue}>
              {status?.status.replace('_', ' ').toUpperCase() || 'Not Started'}
            </Text>
          </View>

          {renderMetrics()}
          {renderCharts()}

          {status?.status !== 'in_progress' && (
            <TouchableOpacity
              style={styles.startButton}
              onPress={handleStartTraining}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <>
                  <Icon name="play" size={20} color="#ffffff" />
                  <Text style={styles.startButtonText}>Start Training</Text>
                </>
              )}
            </TouchableOpacity>
          )}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  modelSelector: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  modelButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#fff',
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  selectedModelButton: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  modelButtonText: {
    color: '#333',
    fontWeight: '500',
  },
  selectedModelButtonText: {
    color: '#fff',
  },
  dashboard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  statusLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginRight: 10,
  },
  statusValue: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  metricsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  chartContainer: {
    marginBottom: 20,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  startButton: {
    backgroundColor: '#007AFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    marginTop: 10,
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 10,
  },
}); 