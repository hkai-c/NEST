import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';

interface AudioPlayerProps {
  audioUrl: string;
  onPlaybackComplete?: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  onPlaybackComplete,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentPosition, setCurrentPosition] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const audioPlayer = useRef(new AudioRecorderPlayer());

  useEffect(() => {
    const setupPlayer = async () => {
      try {
        const msg = await audioPlayer.current.startPlayer(audioUrl);
        const duration = await audioPlayer.current.getDuration();
        setDuration(duration);
        await audioPlayer.current.stopPlayer();
      } catch (error) {
        console.error('Error setting up audio player:', error);
      }
    };

    setupPlayer();

    audioPlayer.current.addPlayBackListener((e) => {
      setCurrentPosition(e.currentPosition);
      if (e.currentPosition === e.duration) {
        setIsPlaying(false);
        onPlaybackComplete?.();
      }
    });

    return () => {
      audioPlayer.current.stopPlayer();
      audioPlayer.current.removePlayBackListener();
    };
  }, [audioUrl]);

  const togglePlayback = async () => {
    try {
      if (isPlaying) {
        await audioPlayer.current.pausePlayer();
      } else {
        setIsLoading(true);
        await audioPlayer.current.startPlayer(audioUrl);
        setIsLoading(false);
      }
      setIsPlaying(!isPlaying);
    } catch (error) {
      console.error('Error toggling playback:', error);
      setIsLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = duration > 0 ? (currentPosition / duration) * 100 : 0;

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.playButton}
        onPress={togglePlayback}
        disabled={isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Icon
            name={isPlaying ? 'pause' : 'play'}
            size={20}
            color="#fff"
          />
        )}
      </TouchableOpacity>

      <View style={styles.progressContainer}>
        <View style={[styles.progressBar, { width: `${progress}%` }]} />
      </View>

      <Text style={styles.timeText}>
        {formatTime(currentPosition)} / {formatTime(duration)}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 16,
    padding: 8,
    marginTop: 8,
  },
  playButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  progressContainer: {
    flex: 1,
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
    marginRight: 8,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#6200ee',
    borderRadius: 2,
  },
  timeText: {
    fontSize: 12,
    color: '#fff',
    minWidth: 80,
    textAlign: 'right',
  },
});

export default AudioPlayer; 