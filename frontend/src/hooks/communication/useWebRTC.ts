import { useState, useCallback, useEffect, useRef } from 'react';
import { useVideoRoom, MediaDevice, Peer } from '../../contexts/VideoRoomContext';

export interface UseWebRTCOptions {
  roomId: string;
  userId: string;
  userName: string;
  isHost?: boolean;
  onPeerJoin?: (peer: Peer) => void;
  onPeerLeave?: (peerId: string) => void;
  onError?: (error: Error) => void;
}

export interface UseWebRTCReturn {
  // Connection State
  isConnected: boolean;
  isConnecting: boolean;
  localStream: MediaStream | null;
  peers: Peer[];
  connectionQuality: 'excellent' | 'good' | 'fair' | 'poor' | 'disconnected';
  
  // Media Controls
  isMicOn: boolean;
  isCameraOn: boolean;
  isScreenSharing: boolean;
  toggleMic: () => void;
  toggleCamera: () => void;
  startScreenShare: () => Promise<void>;
  stopScreenShare: () => void;
  
  // Device Management
  availableDevices: MediaDevice[];
  selectedDevices: {
    audioInput: MediaDevice | null;
    videoInput: MediaDevice | null;
    audioOutput: MediaDevice | null;
  };
  fetchDevices: () => Promise<void>;
  selectAudioInput: (device: MediaDevice) => void;
  selectVideoInput: (device: MediaDevice) => void;
  selectAudioOutput: (device: MediaDevice) => void;
  
  // Room Actions
  joinRoom: () => Promise<void>;
  leaveRoom: () => Promise<void>;
  reconnect: () => Promise<void>;
  
  // Recording
  isRecording: boolean;
  recordingDuration: number;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  
  // Utilities
  getPeerById: (peerId: string) => Peer | undefined;
}

export function useWebRTC(options: UseWebRTCOptions): UseWebRTCReturn {
  const {
    roomId,
    userId,
    userName,
    isHost = false,
    onPeerJoin,
    onPeerLeave,
    onError,
  } = options;

  const {
    state,
    config,
    initializeRoom,
    joinRoom: joinVideoRoom,
    leaveRoom: leaveVideoRoom,
    reconnect,
    toggleMic,
    toggleCamera,
    startScreenShare,
    stopScreenShare,
    fetchAvailableDevices,
    selectAudioInput,
    selectVideoInput,
    selectAudioOutput,
    startRecording,
    stopRecording,
    getPeerById,
    availableDevices,
    selectedDevices,
  } = useVideoRoom();

  const [connectionQuality, setConnectionQuality] = useState<'excellent' | 'good' | 'fair' | 'poor' | 'disconnected'>('disconnected');

  // Initialize room on mount
  useEffect(() => {
    const init = async () => {
      try {
        await initializeRoom({
          roomId,
          token: 'demo-token',
          participantId: userId,
          participantName: userName,
          isHost,
          maxParticipants: 50,
          enableChat: true,
          enableScreenShare: true,
          enableRecording: true,
          waitingRoomEnabled: false,
        });
      } catch (error) {
        onError?.(error as Error);
      }
    };

    if (roomId && userId) {
      init();
    }

    return () => {
      if (state.isConnected) {
        leaveVideoRoom();
      }
    };
  }, [roomId, userId, userName, isHost, initializeRoom, leaveVideoRoom, onError]);

  // Monitor connection quality
  useEffect(() => {
    if (!state.isConnected) {
      setConnectionQuality('disconnected');
      return;
    }

    // Simulate connection quality monitoring
    const monitorQuality = () => {
      // In production, this would monitor actual network metrics
      const qualities: ('excellent' | 'good' | 'fair' | 'poor')[] = ['excellent', 'good', 'fair', 'good'];
      const randomQuality = qualities[Math.floor(Math.random() * qualities.length)];
      setConnectionQuality(randomQuality);
    };

    monitorQuality();
    const interval = setInterval(monitorQuality, 5000);
    
    return () => clearInterval(interval);
  }, [state.isConnected]);

  // Handle peer events
  useEffect(() => {
    if (state.peers.length > 0) {
      const latestPeer = state.peers[state.peers.length - 1];
      if (latestPeer.connectionState === 'connected') {
        onPeerJoin?.(latestPeer);
      }
    }
  }, [state.peers, onPeerJoin]);

  // Wrapper for joining room
  const joinRoom = useCallback(async () => {
    try {
      await joinVideoRoom();
    } catch (error) {
      onError?.(error as Error);
    }
  }, [joinVideoRoom, onError]);

  // Wrapper for leaving room
  const leaveRoom = useCallback(async () => {
    await leaveVideoRoom();
  }, [leaveVideoRoom]);

  // Wrapper for fetching devices
  const fetchDevices = useCallback(async () => {
    await fetchAvailableDevices();
  }, [fetchAvailableDevices]);

  return {
    isConnected: state.isConnected,
    isConnecting: state.isConnecting,
    localStream: state.localStream,
    peers: state.peers,
    connectionQuality,
    isMicOn: state.localStream?.getAudioTracks().some(t => t.enabled) ?? false,
    isCameraOn: state.localStream?.getVideoTracks().some(t => t.enabled) ?? false,
    isScreenSharing: state.isRecording || false,
    toggleMic,
    toggleCamera,
    startScreenShare,
    stopScreenShare,
    availableDevices,
    selectedDevices,
    fetchDevices,
    selectAudioInput,
    selectVideoInput,
    selectAudioOutput,
    joinRoom,
    leaveRoom,
    reconnect,
    isRecording: state.isRecording,
    recordingDuration: state.recordingDuration,
    startRecording,
    stopRecording,
    getPeerById,
  };
}

export default useWebRTC;
