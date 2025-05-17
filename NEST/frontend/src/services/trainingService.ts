import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://localhost:8000';

export interface TrainingMetrics {
  accuracy: number;
  loss: number;
  f1_score: number;
  timestamp: string;
  is_training?: boolean;
}

export interface TrainingStatus {
  status: 'not_started' | 'in_progress' | 'completed';
  message: string;
  metrics?: TrainingMetrics;
}

class TrainingService {
  private async getAuthHeader() {
    const token = await AsyncStorage.getItem('token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  }

  async startTraining(modelType: string, params: {
    epochs?: number;
    batch_size?: number;
    learning_rate?: number;
  }): Promise<{ status: string; message: string }> {
    try {
      const response = await axios.post(
        `${API_URL}/training/train`,
        {
          model_type: modelType,
          ...params,
        },
        await this.getAuthHeader()
      );
      return response.data;
    } catch (error) {
      console.error('Error starting training:', error);
      throw error;
    }
  }

  async getTrainingStatus(modelType: string): Promise<TrainingStatus> {
    try {
      const response = await axios.get(
        `${API_URL}/dashboard/status/${modelType}`,
        await this.getAuthHeader()
      );
      return response.data;
    } catch (error) {
      console.error('Error getting training status:', error);
      throw error;
    }
  }

  async getTrainingMetrics(modelType: string): Promise<TrainingMetrics[]> {
    try {
      const response = await axios.get(
        `${API_URL}/dashboard/metrics/${modelType}`,
        await this.getAuthHeader()
      );
      return response.data;
    } catch (error) {
      console.error('Error getting training metrics:', error);
      throw error;
    }
  }

  async evaluateModel(modelType: string, testData: any[]): Promise<TrainingMetrics> {
    try {
      const response = await axios.post(
        `${API_URL}/training/evaluate`,
        {
          model_type: modelType,
          test_data: testData,
        },
        await this.getAuthHeader()
      );
      return response.data.metrics;
    } catch (error) {
      console.error('Error evaluating model:', error);
      throw error;
    }
  }
}

export const trainingService = new TrainingService(); 