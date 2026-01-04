import React, { createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode } from 'react';

// Type definitions for video room and WebRTC
export interface Peer {
  id: string;
  name: string;
  avatar?: string;
  stream: MediaStream | null;
  isMuted: boolean;
  isVideoOff: boolean;
  isScreenSharing: boolean;
  isSpeaking: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'failed';
  role: 'host' | 'participant';
}

export interface RoomConfig {
  roomId: string;
  token: string;
  participantId: string;
  participantName: string;
  isHost: boolean;
  maxParticipants: number;
  enableChat: boolean;
  enableScreenShare: boolean;
  enableRecording: boolean;
  waitingRoomEnabled: boolean;
}

export interface MediaDevice {
  deviceId: string;
  label: string;
  kind: 'audioinput' | 'audiooutput' | 'videoinput';
}

export interface ChatMessage {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
  type: 'text' | 'system';
}

export interface VideoRoomState {
  isInitialized: boolean;
  isConnecting: boolean;
  isConnected: boolean;
  localStream: MediaStream | null;
  screenStream: MediaStream | null;
  peers: Peer[];
  roomId: string | null;
  error: string | null;
  isRecording: boolean;
  recordingDuration: number;
  chatMessages: ChatMessage[];
  unreadMessages: number;
}

export interface VideoRoomContextType {
  // State
  state: VideoRoomState;
  config: RoomConfig | null;
  selectedDevices: {
    audioInput: MediaDevice | null;
    videoInput: MediaDevice | null;
    audioOutput: MediaDevice | null;
  };
  availableDevices: MediaDevice[];
  isMicOn: boolean;
  isCameraOn: boolean;
  isScreenSharing: boolean;
  isFullscreen: boolean;
  
  // Room Operations
  initializeRoom: (roomConfig: RoomConfig) => Promise<void>;
  joinRoom: () => Promise<void>;
  leaveRoom: () => Promise<void>;
  reconnect: () => Promise<void>;
  
  // Media Controls
  toggleMic: () => void;
  toggleCamera: () => void;
  startScreenShare: () => Promise<void>;
  stopScreenShare: () => void;
  
  // Device Management
  fetchAvailableDevices: () => Promise<void>;
  selectAudioInput: (device: MediaDevice) => void;
  selectVideoInput: (device: MediaDevice) => void;
  selectAudioOutput: (device: MediaDevice) => void;
  
  // Recording
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  
  // Fullscreen
  toggleFullscreen: () => void;
  
  // Chat
  sendChatMessage: (content: string) => void;
  clearUnreadMessages: () => void;
  
  // Utilities
  getPeerById: (peerId: string) => Peer | undefined;
}

const VideoRoomContext = createContext<VideoRoomContextType | undefined>(undefined);

export function VideoRoomProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<VideoRoomState>({
    isInitialized: false,
    isConnecting: false,
    isConnected: false,
    localStream: null,
    screenStream: null,
    peers: [],
    roomId: null,
    error: null,
    isRecording: false,
    recordingDuration: 0,
    chatMessages: [],
    unreadMessages: 0,
  });
  
  const [config, setConfig] = useState<RoomConfig | null>(null);
  const [selectedDevices, setSelectedDevices] = useState<{
    audioInput: MediaDevice | null;
    videoInput: MediaDevice | null;
    audioOutput: MediaDevice | null;
  }>({ audioInput: null, videoInput: null, audioOutput: null });
  
  const [availableDevices, setAvailableDevices] = useState<MediaDevice[]>([]);
  const [isMicOn, setIsMicOn] = useState(true);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map());
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize room with configuration
  const initializeRoom = useCallback(async (roomConfig: RoomConfig) => {
    try {
      setConfig(roomConfig);
      
      // Request media permissions
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });
      
      setState(prev => ({
        ...prev,
        isInitialized: true,
        localStream: stream,
      }));
      
      // Fetch available devices
      await fetchAvailableDevices();
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to initialize video room: ' + (error as Error).message,
      }));
    }
  }, []);

  // Join the room
  const joinRoom = useCallback(async () => {
    if (!config) return;
    
    setState(prev => ({ ...prev, isConnecting: true }));
    
    try {
      // In production, this would connect to signaling server
      // and establish peer connections
      
      // Simulate connection
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setState(prev => ({
        ...prev,
        isConnecting: false,
        isConnected: true,
        roomId: config.roomId,
      }));
      
      // Add a mock peer for demo
      setState(prev => ({
        ...prev,
        peers: [
          {
            id: 'peer-1',
            name: 'John Doe',
            stream: null,
            isMuted: false,
            isVideoOff: false,
            isScreenSharing: false,
            isSpeaking: false,
            connectionState: 'connected',
            role: 'participant',
          },
        ],
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: 'Failed to join room: ' + (error as Error).message,
      }));
    }
  }, [config]);

  // Leave the room
  const leaveRoom = useCallback(async () => {
    // Stop all tracks
    if (state.localStream) {
      state.localStream.getTracks().forEach(track => track.stop());
    }
    if (state.screenStream) {
      state.screenStream.getTracks().forEach(track => track.stop());
    }
    
    // Close all peer connections
    peerConnectionsRef.current.forEach(pc => pc.close());
    peerConnectionsRef.current.clear();
    
    // Stop recording if active
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
    }
    
    setState({
      isInitialized: false,
      isConnecting: false,
      isConnected: false,
      localStream: null,
      screenStream: null,
      peers: [],
      roomId: null,
      error: null,
      isRecording: false,
      recordingDuration: 0,
      chatMessages: [],
      unreadMessages: 0,
    });
    
    setIsScreenSharing(false);
  }, [state.localStream, state.screenStream]);

  // Reconnect to room
  const reconnect = useCallback(async () => {
    if (!config) return;
    await leaveRoom();
    await initializeRoom(config);
    await joinRoom();
  }, [config, initializeRoom, joinRoom, leaveRoom]);

  // Toggle microphone
  const toggleMic = useCallback(() => {
    if (state.localStream) {
      const audioTrack = state.localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMicOn(audioTrack.enabled);
      }
    }
  }, [state.localStream]);

  // Toggle camera
  const toggleCamera = useCallback(() => {
    if (state.localStream) {
      const videoTrack = state.localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsCameraOn(videoTrack.enabled);
      }
    }
  }, [state.localStream]);

  // Start screen sharing
  const startScreenShare = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });
      
      setState(prev => ({
        ...prev,
        screenStream: stream,
      }));
      
      setIsScreenSharing(true);
      
      // Handle when user stops sharing via browser UI
      stream.getVideoTracks()[0].onended = () => {
        stopScreenShare();
      };
    } catch (error) {
      console.error('Failed to start screen share:', error);
    }
  }, []);

  // Stop screen sharing
  const stopScreenShare = useCallback(() => {
    if (state.screenStream) {
      state.screenStream.getTracks().forEach(track => track.stop());
      setState(prev => ({ ...prev, screenStream: null }));
    }
    setIsScreenSharing(false);
  }, [state.screenStream]);

  // Fetch available media devices
  const fetchAvailableDevices = useCallback(async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      
      const videoDevices: MediaDevice[] = devices
        .filter(d => d.kind === 'videoinput')
        .map(d => ({ deviceId: d.deviceId, label: d.label || `Camera ${d.deviceId.slice(0, 4)}`, kind: d.kind as 'videoinput' }));
      
      const audioInputDevices: MediaDevice[] = devices
        .filter(d => d.kind === 'audioinput')
        .map(d => ({ deviceId: d.deviceId, label: d.label || `Microphone ${d.deviceId.slice(0, 4)}`, kind: d.kind as 'audioinput' }));
      
      const audioOutputDevices: MediaDevice[] = devices
        .filter(d => d.kind === 'audiooutput')
        .map(d => ({ deviceId: d.deviceId, label: d.label || `Speaker ${d.deviceId.slice(0, 4)}`, kind: d.kind as 'audiooutput' }));
      
      const allDevices: MediaDevice[] = [...videoDevices, ...audioInputDevices, ...audioOutputDevices];
      setAvailableDevices(allDevices);
      
      // Select default devices
      if (audioInputDevices.length > 0 && !selectedDevices.audioInput) {
        setSelectedDevices(prev => ({ ...prev, audioInput: audioInputDevices[0] }));
      }
      if (videoDevices.length > 0 && !selectedDevices.videoInput) {
        setSelectedDevices(prev => ({ ...prev, videoInput: videoDevices[0] }));
      }
      if (audioOutputDevices.length > 0 && !selectedDevices.audioOutput) {
        setSelectedDevices(prev => ({ ...prev, audioOutput: audioOutputDevices[0] }));
      }
    } catch (error) {
      console.error('Failed to enumerate devices:', error);
    }
  }, [selectedDevices.audioInput, selectedDevices.videoInput, selectedDevices.audioOutput]);

  // Select audio input device
  const selectAudioInput = useCallback((device: MediaDevice) => {
    setSelectedDevices(prev => ({ ...prev, audioInput: device }));
    
    if (state.localStream) {
      const audioTrack = state.localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.stop();
        
        navigator.mediaDevices.getUserMedia({ audio: { deviceId: device.deviceId } })
          .then(stream => {
            const newAudioTrack = stream.getAudioTracks()[0];
            state.localStream?.addTrack(newAudioTrack);
          });
      }
    }
  }, [state.localStream]);

  // Select video input device
  const selectVideoInput = useCallback((device: MediaDevice) => {
    setSelectedDevices(prev => ({ ...prev, videoInput: device }));
  }, []);

  // Select audio output device
  const selectAudioOutput = useCallback((device: MediaDevice) => {
    setSelectedDevices(prev => ({ ...prev, audioOutput: device }));
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    if (!state.isConnected) return;
    
    setState(prev => ({
      ...prev,
      isRecording: true,
      recordingDuration: 0,
    }));
    
    // Start recording timer
    recordingTimerRef.current = setInterval(() => {
      setState(prev => ({
        ...prev,
        recordingDuration: prev.recordingDuration + 1,
      }));
    }, 1000);
    
    // In production, this would trigger server-side recording
    console.log('Recording started');
  }, [state.isConnected]);

  // Stop recording
  const stopRecording = useCallback(async () => {
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
    }
    
    setState(prev => ({
      ...prev,
      isRecording: false,
    }));
    
    // In production, this would finalize and provide recording URL
    console.log('Recording stopped');
  }, []);

  // Toggle fullscreen
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev);
  }, []);

  // Send chat message
  const sendChatMessage = useCallback((content: string) => {
    if (!config) return;
    
    const message: ChatMessage = {
      id: `msg-${Date.now()}`,
      senderId: config.participantId,
      senderName: config.participantName,
      content,
      timestamp: new Date().toISOString(),
      type: 'text',
    };
    
    setState(prev => ({
      ...prev,
      chatMessages: [...prev.chatMessages, message],
    }));
  }, [config]);

  // Clear unread messages
  const clearUnreadMessages = useCallback(() => {
    setState(prev => ({ ...prev, unreadMessages: 0 }));
  }, []);

  // Get peer by ID
  const getPeerById = useCallback((peerId: string) => {
    return state.peers.find(peer => peer.id === peerId);
  }, [state.peers]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      leaveRoom();
    };
  }, [leaveRoom]);

  const value: VideoRoomContextType = {
    state,
    config,
    selectedDevices,
    availableDevices,
    isMicOn,
    isCameraOn,
    isScreenSharing,
    isFullscreen,
    initializeRoom,
    joinRoom,
    leaveRoom,
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
    toggleFullscreen,
    sendChatMessage,
    clearUnreadMessages,
    getPeerById,
  };

  return (
    <VideoRoomContext.Provider value={value}>
      {children}
    </VideoRoomContext.Provider>
  );
}

export function useVideoRoom() {
  const context = useContext(VideoRoomContext);
  if (context === undefined) {
    throw new Error('useVideoRoom must be used within a VideoRoomProvider');
  }
  return context;
}

export default VideoRoomContext;
