declare module 'react-native-voice' {
  export interface SpeechResultsEvent {
    value: string[];
  }

  export interface SpeechErrorEvent {
    error: {
      message: string;
    };
  }

  const Voice: {
    onSpeechStart: (callback: () => void) => void;
    onSpeechEnd: (callback: () => void) => void;
    onSpeechResults: (callback: (e: SpeechResultsEvent) => void) => void;
    onSpeechError: (callback: (e: SpeechErrorEvent) => void) => void;
    start: (locale: string) => Promise<void>;
    stop: () => Promise<void>;
    destroy: () => Promise<void>;
    removeAllListeners: () => void;
  };

  export default Voice;
}

declare module 'react-native-audio-recorder-player' {
  export interface AudioSet {
    AVEncoderAudioQualityKeyIOS: number;
    AVNumberOfChannelsKeyIOS: number;
    AVLinearPCMBitDepthKeyIOS: number;
    AVLinearPCMIsBigEndianKeyIOS: boolean;
    AVLinearPCMIsFloatKeyIOS: boolean;
    AVSampleRateKeyIOS: number;
  }

  export interface PlayBackType {
    currentPosition: number;
    duration: number;
    currentPositionSec: number;
    currentDurationSec: number;
    playTime: string;
    duration: string;
  }

  export default class AudioRecorderPlayer {
    addRecordBackListener: (callback: (data: PlayBackType) => void) => void;
    addPlayBackListener: (callback: (data: PlayBackType) => void) => void;
    startRecorder: (path: string, audioSet?: AudioSet) => Promise<string>;
    stopRecorder: () => Promise<string>;
    startPlayer: (path: string) => Promise<string>;
    stopPlayer: () => Promise<string>;
    pausePlayer: () => Promise<string>;
    resumePlayer: () => Promise<string>;
    seekToPlayer: (time: number) => Promise<string>;
    setVolume: (volume: number) => Promise<string>;
  }
}

declare module 'react-native-chart-kit' {
  import { ViewStyle } from 'react-native';

  export interface ChartConfig {
    backgroundColor?: string;
    backgroundGradientFrom?: string;
    backgroundGradientTo?: string;
    decimalPlaces?: number;
    color?: (opacity?: number) => string;
    labelColor?: (opacity?: number) => string;
    style?: ViewStyle;
    propsForDots?: {
      r?: string;
      strokeWidth?: string;
      stroke?: string;
    };
  }

  export interface LineChartData {
    labels: string[];
    datasets: {
      data: number[];
      color?: (opacity?: number) => string;
      strokeWidth?: number;
    }[];
  }

  export interface LineChartProps {
    data: LineChartData;
    width: number;
    height: number;
    chartConfig: ChartConfig;
    bezier?: boolean;
    style?: ViewStyle;
  }

  export class LineChart extends React.Component<LineChartProps> {}
} 