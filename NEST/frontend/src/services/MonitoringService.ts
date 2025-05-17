import LoggingService from './LoggingService';

export interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: string;
  tags?: Record<string, string>;
}

export interface UserAction {
  action: string;
  timestamp: string;
  context?: Record<string, any>;
}

class MonitoringService {
  private static instance: MonitoringService;
  private metrics: PerformanceMetric[] = [];
  private userActions: UserAction[] = [];
  private readonly MAX_METRICS = 1000;
  private readonly FLUSH_INTERVAL = 60000; // 1 minute
  private readonly logger = LoggingService.getInstance();

  private constructor() {
    this.initializeMonitoring();
  }

  public static getInstance(): MonitoringService {
    if (!MonitoringService.instance) {
      MonitoringService.instance = new MonitoringService();
    }
    return MonitoringService.instance;
  }

  private initializeMonitoring(): void {
    // Start periodic metric flushing
    setInterval(() => this.flushMetrics(), this.FLUSH_INTERVAL);
    
    // Track page load performance
    this.trackPageLoad();
    
    // Track network requests
    this.trackNetworkRequests();
  }

  private trackPageLoad(): void {
    if (typeof window !== 'undefined') {
      window.addEventListener('load', () => {
        const timing = window.performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        
        this.recordMetric('page_load_time', loadTime, {
          page: window.location.pathname,
        });
      });
    }
  }

  private trackNetworkRequests(): void {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const startTime = performance.now();
      try {
        const response = await originalFetch(...args);
        const endTime = performance.now();
        
        this.recordMetric('api_request_time', endTime - startTime, {
          url: args[0].toString(),
          method: args[1]?.method || 'GET',
          status: response.status.toString(),
        });
        
        return response;
      } catch (error) {
        const endTime = performance.now();
        
        this.recordMetric('api_request_time', endTime - startTime, {
          url: args[0].toString(),
          method: args[1]?.method || 'GET',
          error: error.message,
        });
        
        throw error;
      }
    };
  }

  public recordMetric(name: string, value: number, tags?: Record<string, string>): void {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: new Date().toISOString(),
      tags,
    };

    this.metrics.push(metric);
    this.logger.debug(`Metric recorded: ${name}`, { value, tags });

    // Trim metrics if they exceed the maximum
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics = this.metrics.slice(-this.MAX_METRICS);
    }
  }

  public trackUserAction(action: string, context?: Record<string, any>): void {
    const userAction: UserAction = {
      action,
      timestamp: new Date().toISOString(),
      context,
    };

    this.userActions.push(userAction);
    this.logger.info(`User action: ${action}`, context);
  }

  private async flushMetrics(): Promise<void> {
    if (this.metrics.length === 0) return;

    const metricsToSend = [...this.metrics];
    this.metrics = [];

    try {
      await fetch('http://localhost:8000/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metrics: metricsToSend,
          userActions: this.userActions,
        }),
      });
      
      this.userActions = [];
    } catch (error) {
      // If sending fails, put the metrics back
      this.metrics = [...metricsToSend, ...this.metrics];
      this.logger.error('Failed to send metrics to server', { error });
    }
  }

  public async getMetrics(): Promise<PerformanceMetric[]> {
    return [...this.metrics];
  }

  public async getUserActions(): Promise<UserAction[]> {
    return [...this.userActions];
  }

  public async clearMetrics(): Promise<void> {
    this.metrics = [];
    this.userActions = [];
  }
}

export default MonitoringService; 