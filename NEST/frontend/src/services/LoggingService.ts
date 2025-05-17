import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  userId?: string;
  sessionId?: string;
}

class LoggingService {
  private static instance: LoggingService;
  private logs: LogEntry[] = [];
  private readonly MAX_LOCAL_LOGS = 1000;
  private readonly FLUSH_INTERVAL = 60000; // 1 minute
  private sessionId: string;
  private userId: string | null = null;

  private constructor() {
    this.sessionId = this.generateSessionId();
    this.initializeLogging();
  }

  public static getInstance(): LoggingService {
    if (!LoggingService.instance) {
      LoggingService.instance = new LoggingService();
    }
    return LoggingService.instance;
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private async initializeLogging(): Promise<void> {
    // Load user ID if available
    this.userId = await AsyncStorage.getItem('userId');
    
    // Start periodic log flushing
    setInterval(() => this.flushLogs(), this.FLUSH_INTERVAL);
    
    // Add event listeners for unhandled errors
    this.setupErrorHandlers();
  }

  private setupErrorHandlers(): void {
    const handleError = (error: Error) => {
      this.error('Unhandled error', { error: error.message, stack: error.stack });
    };

    window.addEventListener('error', (event) => handleError(event.error));
    window.addEventListener('unhandledrejection', (event) => handleError(event.reason));
  }

  public async setUserId(userId: string): Promise<void> {
    this.userId = userId;
    await AsyncStorage.setItem('userId', userId);
  }

  public debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  public info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context);
  }

  public warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context);
  }

  public error(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, context);
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      userId: this.userId || undefined,
      sessionId: this.sessionId,
    };

    this.logs.push(logEntry);
    console.log(`[${level}] ${message}`, context || '');

    // If it's an error, immediately flush logs
    if (level === LogLevel.ERROR) {
      this.flushLogs();
    }

    // Trim logs if they exceed the maximum
    if (this.logs.length > this.MAX_LOCAL_LOGS) {
      this.logs = this.logs.slice(-this.MAX_LOCAL_LOGS);
    }
  }

  private async flushLogs(): Promise<void> {
    if (this.logs.length === 0) return;

    const logsToSend = [...this.logs];
    this.logs = [];

    try {
      await axios.post('http://localhost:8000/logs', {
        logs: logsToSend,
      });
    } catch (error) {
      // If sending fails, put the logs back
      this.logs = [...logsToSend, ...this.logs];
      console.error('Failed to send logs to server:', error);
    }
  }

  public async getLogs(): Promise<LogEntry[]> {
    return [...this.logs];
  }

  public async clearLogs(): Promise<void> {
    this.logs = [];
  }
}

export default LoggingService; 