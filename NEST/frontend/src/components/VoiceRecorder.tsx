import React, { useState, useEffect } from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  Platform,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import Voice, { SpeechResultsEvent } from 'react-native-voice';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';

interface VoiceRecorderProps {
  onTranscriptionComplete: (text: string) => void;
  onRecordingComplete: (audioPath: string) => void;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onTranscriptionComplete,
  onRecordingComplete,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const audioRecorderPlayer = new AudioRecorderPlayer();
  let recordingTimer: ReturnType<typeof setInterval>;

  useEffect(() => {
    const setupVoice = () => {
      Voice.onSpeechStart = () => setIsTranscribing(true);
      Voice.onSpeechEnd = () => setIsTranscribing(false);
      Voice.onSpeechResults = (e: SpeechResultsEvent) => {
        if (e.value && e.value[0]) {
          onTranscriptionComplete(e.value[0]);
        }
      };
    };

    setupVoice();

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
      if (recordingTimer) {
        clearInterval(recordingTimer);
      }
    };
  }, [onTranscriptionComplete]);

  const startRecording = async () => {
    try {
      const audioPath = Platform.select({
        ios: 'recording.m4a',
        android: 'sdcard/recording.m4a',
      });

      if (!audioPath) {
        throw new Error('Platform not supported');
      }

      await audioRecorderPlayer.startRecorder(audioPath);
      await Voice.start('en-US');
      setIsRecording(true);
      setRecordingTime(0);

      recordingTimer = setInterval(() => {
        setRecordingTime((prev: number) => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = async () => {
    try {
      const audioPath = await audioRecorderPlayer.stopRecorder();
      await Voice.stop();
      setIsRecording(false);
      if (recordingTimer) {
        clearInterval(recordingTimer);
      }
      onRecordingComplete(audioPath);
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.recordButton, isRecording && styles.recordingButton]}
        onPressIn={startRecording}
        onPressOut={stopRecording}
      >
        <Icon
          name={isRecording ? 'microphone' : 'microphone-outline'}
          size={24}
          color={isRecording ? '#fff' : '#6200ee'}
        />
      </TouchableOpacity>
      {isRecording && (
        <Text style={styles.timer}>{formatTime(recordingTime)}</Text>
      )}
      {isTranscribing && (
        <Text style={styles.transcribingText}>Transcribing...</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recordButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#6200ee',
  },
  recordingButton: {
    backgroundColor: '#6200ee',
  },
  timer: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  transcribingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#6200ee',
    fontStyle: 'italic',
  },
});

export default VoiceRecorder; 