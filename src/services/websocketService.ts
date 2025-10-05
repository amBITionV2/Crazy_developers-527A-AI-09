// WebSocket service for real-time notifications
export interface EmergencyAlert {
  id: string;
  patient_name: string;
  hospital_name: string;
  blood_group: string;
  units_needed: number;
  urgency_level: string;
  needed_by: string;
  contact_phone: string;
  medical_condition?: string;
  hospital_latitude?: number;
  hospital_longitude?: number;
  search_radius_km: number;
  created_at: string;
}

export interface DonorResponse {
  donor_id: string;
  donor_name: string;
  donor_phone: string;
  donor_blood_group: string;
  response: 'accepted' | 'declined';
  message?: string;
  alert_id: string;
  responded_at: string;
}

export interface WebSocketMessage {
  type: 'emergency_alert' | 'donor_response' | 'connection_status';
  data: EmergencyAlert | DonorResponse | Record<string, unknown>;
  timestamp: string;
}

export type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private messageHandlers: Set<MessageHandler> = new Set();
  private isConnecting = false;

  constructor() {
    this.userId = localStorage.getItem('userId');
  }

  connect(userId?: string) {
    if (userId) {
      this.userId = userId;
      localStorage.setItem('userId', userId);
    }

    if (!this.userId) {
      console.warn('No user ID available for WebSocket connection');
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8001'}/ws/emergency/${this.userId}`;
    
    try {
      console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        
        // Send connection confirmation
        this.notifyHandlers({
          type: 'connection_status',
          data: { status: 'connected' },
          timestamp: new Date().toISOString()
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', message);
          this.notifyHandlers(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket connection closed:', event.code, event.reason);
        this.isConnecting = false;
        this.ws = null;
        
        this.notifyHandlers({
          type: 'connection_status',
          data: { status: 'disconnected', code: event.code, reason: event.reason },
          timestamp: new Date().toISOString()
        });

        // Attempt to reconnect if not intentionally closed
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.isConnecting = false;
        
        this.notifyHandlers({
          type: 'connection_status',
          data: { status: 'error', error: error.toString() },
          timestamp: new Date().toISOString()
        });
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
    }
  }

  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      if (this.reconnectAttempts <= this.maxReconnectAttempts) {
        this.connect();
      } else {
        console.error('❌ Max reconnection attempts reached');
      }
    }, delay);
  }

  disconnect() {
    if (this.ws) {
      console.log('🔌 Disconnecting WebSocket');
      this.ws.close(1000, 'User initiated disconnect');
      this.ws = null;
    }
  }

  addMessageHandler(handler: MessageHandler) {
    this.messageHandlers.add(handler);
  }

  removeMessageHandler(handler: MessageHandler) {
    this.messageHandlers.delete(handler);
  }

  private notifyHandlers(message: WebSocketMessage) {
    this.messageHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  // Send a message to the server (if needed)
  send(message: Record<string, unknown>) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  // Check connection status
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Get connection state
  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();

// React hook for using WebSocket in components
export const useWebSocket = () => {
  return {
    connect: websocketService.connect.bind(websocketService),
    disconnect: websocketService.disconnect.bind(websocketService),
    addMessageHandler: websocketService.addMessageHandler.bind(websocketService),
    removeMessageHandler: websocketService.removeMessageHandler.bind(websocketService),
    send: websocketService.send.bind(websocketService),
    isConnected: websocketService.isConnected.bind(websocketService),
    getConnectionState: websocketService.getConnectionState.bind(websocketService),
  };
};

export default websocketService;