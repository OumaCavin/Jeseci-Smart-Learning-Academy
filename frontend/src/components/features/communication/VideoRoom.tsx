import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useWebRTC } from '../../hooks/communication/useWebRTC';
import './VideoRoom.css';

interface VideoRoomProps {
  roomId: string;
  userId: string;
  userName: string;
  onLeave?: () => void;
  showChat?: boolean;
  showParticipants?: boolean;
}

export function VideoRoom({
  roomId,
  userId,
  userName,
  onLeave,
  showChat = true,
  showParticipants = true,
}: VideoRoomProps) {
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const [activeSpeaker, setActiveSpeaker] = useState<string | null>(null);
  const [showDeviceSettings, setShowDeviceSettings] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [activeTab, setActiveTab] = useState<'chat' | 'participants' | null>(null);

  const {
    isConnected,
    isConnecting,
    localStream,
    peers,
    connectionQuality,
    isMicOn,
    isCameraOn,
    isScreenSharing,
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
    isRecording,
    recordingDuration,
    startRecording,
    stopRecording,
    getPeerById,
  } = useWebRTC({
    roomId,
    userId,
    userName,
    isHost: false,
    onPeerJoin: (peer) => console.log('Peer joined:', peer.name),
    onPeerLeave: (peerId) => console.log('Peer left:', peerId),
  });

  // Set local video stream
  useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  // Fetch devices on mount
  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  // Join room on mount
  useEffect(() => {
    joinRoom();
  }, [joinRoom]);

  // Handle leave
  const handleLeave = useCallback(async () => {
    await leaveRoom();
    onLeave?.();
  }, [leaveRoom, onLeave]);

  // Format recording duration
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Get connection quality color
  const getQualityColor = () => {
    switch (connectionQuality) {
      case 'excellent': return '#10b981';
      case 'good': return '#3b82f6';
      case 'fair': return '#f59e0b';
      case 'poor': return '#ef4444';
      default: return '#6b7280';
    }
  };

  if (isConnecting) {
    return (
      <div className="video-room loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Connecting to room...</p>
          <span className="room-id">Room: {roomId}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="video-room">
      {/* Main video area */}
      <div className="video-area">
        {/* Remote peers grid */}
        <div className="peers-grid">
          {peers.length === 0 ? (
            <div className="no-peers">
              <span className="no-peers-icon">👥</span>
              <p>Waiting for others to join...</p>
            </div>
          ) : (
            peers.map((peer) => (
              <div key={peer.id} className={`peer-tile ${activeSpeaker === peer.id ? 'speaking' : ''}`}>
                <video
                  autoPlay
                  playsInline
                  ref={(el) => {
                    if (el && peer.stream) {
                      el.srcObject = peer.stream;
                    }
                  }}
                />
                <div className="peer-info">
                  <span className="peer-name">{peer.name}</span>
                  <div className="peer-status">
                    {peer.isMuted && <span className="status-icon">🔇</span>}
                    {peer.isVideoOff && <span className="status-icon">📷</span>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Local video */}
        <div className="local-video-container">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className={`local-video ${!isCameraOn ? 'video-off' : ''}`}
          />
          {!isCameraOn && (
            <div className="video-off-placeholder">
              <span className="avatar">{userName.charAt(0).toUpperCase()}</span>
            </div>
          )}
          <div className="local-info">
            <span className="local-name">You</span>
            <div className="local-status">
              {isMicOn ? null : <span className="status-icon">🔇</span>}
              {isRecording && <span className="recording-indicator">🔴 REC</span>}
            </div>
          </div>
        </div>

        {/* Connection quality indicator */}
        <div className="connection-quality" style={{ backgroundColor: getQualityColor() }}>
          <span>{connectionQuality}</span>
        </div>

        {/* Recording timer */}
        {isRecording && (
          <div className="recording-timer">
            <span className="rec-dot">●</span>
            {formatDuration(recordingDuration)}
          </div>
        )}
      </div>

      {/* Side panel */}
      {(showChat || showParticipants) && (
        <div className={`side-panel ${activeTab ? 'open' : ''}`}>
          <div className="panel-tabs">
            {showChat && (
              <button
                className={`panel-tab ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab(activeTab === 'chat' ? null : 'chat')}
              >
                💬 Chat
              </button>
            )}
            {showParticipants && (
              <button
                className={`panel-tab ${activeTab === 'participants' ? 'active' : ''}`}
                onClick={() => setActiveTab(activeTab === 'participants' ? null : 'participants')}
              >
                👥 {peers.length + 1}
              </button>
            )}
          </div>

          {activeTab === 'chat' && showChat && (
            <div className="chat-panel">
              <div className="chat-messages">
                <div className="chat-message system">
                  <span className="message-text">Welcome to the video room!</span>
                </div>
              </div>
              <div className="chat-input-container">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a message..."
                  onKeyPress={(e) => e.key === 'Enter' && setChatInput('')}
                />
                <button onClick={() => setChatInput('')}>Send</button>
              </div>
            </div>
          )}

          {activeTab === 'participants' && showParticipants && (
            <div className="participants-panel">
              <div className="participant-list">
                <div className="participant-item">
                  <span className="participant-avatar">{userName.charAt(0).toUpperCase()}</span>
                  <span className="participant-name">{userName} (You)</span>
                  <span className="participant-role">Host</span>
                </div>
                {peers.map((peer) => (
                  <div key={peer.id} className="participant-item">
                    <span className="participant-avatar">{peer.name.charAt(0).toUpperCase()}</span>
                    <span className="participant-name">{peer.name}</span>
                    <div className="participant-actions">
                      {peer.isMuted && <span>🔇</span>}
                      {peer.isVideoOff && <span>📷</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Control bar */}
      <div className="control-bar">
        <div className="control-group">
          <button
            className={`control-btn ${!isMicOn ? 'off' : ''}`}
            onClick={toggleMic}
            title={isMicOn ? 'Mute' : 'Unmute'}
          >
            {isMicOn ? '🎤' : '🔇'}
          </button>
          
          <button
            className={`control-btn ${!isCameraOn ? 'off' : ''}`}
            onClick={toggleCamera}
            title={isCameraOn ? 'Turn off camera' : 'Turn on camera'}
          >
            {isCameraOn ? '📹' : '📷'}
          </button>
          
          <button
            className={`control-btn ${isScreenSharing ? 'active' : ''}`}
            onClick={isScreenSharing ? stopScreenShare : startScreenShare}
            title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
          >
            🖥️
          </button>
          
          <button
            className={`control-btn ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            title={isRecording ? 'Stop recording' : 'Start recording'}
          >
            {isRecording ? '⏹️' : '⏺️'}
          </button>
        </div>

        <div className="control-group">
          <button
            className="control-btn"
            onClick={() => setShowDeviceSettings(!showDeviceSettings)}
            title="Device settings"
          >
            ⚙️
          </button>
          
          <button
            className="control-btn"
            onClick={reconnect}
            title="Reconnect"
          >
            🔄
          </button>
        </div>

        <div className="control-group">
          <button
            className="control-btn leave-btn"
            onClick={handleLeave}
            title="Leave room"
          >
            📞
          </button>
        </div>
      </div>

      {/* Device settings modal */}
      {showDeviceSettings && (
        <div className="device-settings-modal" onClick={() => setShowDeviceSettings(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Device Settings</h3>
            
            <div className="setting-group">
              <label>Microphone</label>
              <select
                value={selectedDevices.audioInput?.deviceId || ''}
                onChange={(e) => {
                  const device = availableDevices.find(d => d.deviceId === e.target.value);
                  if (device) selectAudioInput(device);
                }}
              >
                {availableDevices
                  .filter(d => d.kind === 'audioinput')
                  .map(device => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label}
                    </option>
                  ))}
              </select>
            </div>
            
            <div className="setting-group">
              <label>Camera</label>
              <select
                value={selectedDevices.videoInput?.deviceId || ''}
                onChange={(e) => {
                  const device = availableDevices.find(d => d.deviceId === e.target.value);
                  if (device) selectVideoInput(device);
                }}
              >
                {availableDevices
                  .filter(d => d.kind === 'videoinput')
                  .map(device => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label}
                    </option>
                  ))}
              </select>
            </div>
            
            <div className="setting-group">
              <label>Speaker</label>
              <select
                value={selectedDevices.audioOutput?.deviceId || ''}
                onChange={(e) => {
                  const device = availableDevices.find(d => d.deviceId === e.target.value);
                  if (device) selectAudioOutput(device);
                }}
              >
                {availableDevices
                  .filter(d => d.kind === 'audiooutput')
                  .map(device => (
                    <option key={device.deviceId} value={device.deviceId}>
                      {device.label}
                    </option>
                  ))}
              </select>
            </div>
            
            <button className="close-btn" onClick={() => setShowDeviceSettings(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoRoom;
