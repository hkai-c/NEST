declare module 'react-native-vector-icons/MaterialCommunityIcons' {
  import { Component } from 'react';
  import { TextStyle } from 'react-native';

  interface IconProps {
    name: string;
    size?: number;
    color?: string;
    style?: TextStyle;
  }

  export default class Icon extends Component<IconProps> {}
}

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
    getDuration: () => Promise<number>;
    removePlayBackListener: () => void;
  }
}

declare module 'axios' {
  export interface AxiosRequestConfig {
    headers?: Record<string, string>;
  }

  export interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    config: AxiosRequestConfig;
  }

  interface AxiosInstance {
    get: <T = any>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
    delete: <T = any>(url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
  }

  const axios: AxiosInstance;
  export default axios;
}

declare module '@react-native-async-storage/async-storage' {
  interface AsyncStorage {
    getItem: (key: string) => Promise<string | null>;
    setItem: (key: string, value: string) => Promise<void>;
    removeItem: (key: string) => Promise<void>;
    clear: () => Promise<void>;
    getAllKeys: () => Promise<string[]>;
    multiGet: (keys: string[]) => Promise<[string, string | null][]>;
    multiSet: (keyValuePairs: [string, string][]) => Promise<void>;
    multiRemove: (keys: string[]) => Promise<void>;
  }

  const asyncStorage: AsyncStorage;
  export default asyncStorage;
} 