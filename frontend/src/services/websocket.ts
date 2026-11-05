import { ExecutionEvent } from "../types/ir";

type EventCallback = (event: ExecutionEvent) => void;
type StatusCallback = (connected: boolean) => void;

class ExecutionStreamManager {
  private ws: WebSocket | null = null;
  private sse: EventSource | null = null;
  private listeners: Set<EventCallback> = new Set();
  private statusListeners: Set<StatusCallback> = new Set();
  private isConnected: boolean = false;
  private reconnectTimer: any = null;

  connect() {
    this.disconnect();

    const wsUrl = "ws://127.0.0.1:8000/ws/execution";
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.notifyStatus(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed: ExecutionEvent = JSON.parse(event.data);
          this.notifyListeners(parsed);
        } catch (e) {
          console.error("Failed to parse WebSocket event:", e);
        }
      };

      this.ws.onerror = () => {
        // Fallback to Server-Sent Events (SSE)
        this.fallbackToSSE();
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyStatus(false);
        this.scheduleReconnect();
      };
    } catch {
      this.fallbackToSSE();
    }
  }

  private fallbackToSSE() {
    if (this.sse) return;
    try {
      this.sse = new EventSource("http://127.0.0.1:8000/api/stream/events");

      this.sse.onopen = () => {
        this.isConnected = true;
        this.notifyStatus(true);
      };

      this.sse.onmessage = (event) => {
        try {
          const parsed: ExecutionEvent = JSON.parse(event.data);
          this.notifyListeners(parsed);
        } catch (e) {
          console.error("Failed to parse SSE event:", e);
        }
      };

      this.sse.onerror = () => {
        this.isConnected = false;
        this.notifyStatus(false);
      };
    } catch (e) {
      console.error("SSE fallback error:", e);
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 3000);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.sse) {
      this.sse.close();
      this.sse = null;
    }
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.isConnected = false;
    this.notifyStatus(false);
  }

  subscribe(callback: EventCallback): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  subscribeStatus(callback: StatusCallback): () => void {
    this.statusListeners.add(callback);
    callback(this.isConnected);
    return () => this.statusListeners.delete(callback);
  }

  private notifyListeners(event: ExecutionEvent) {
    this.listeners.forEach((cb) => cb(event));
  }

  private notifyStatus(connected: boolean) {
    this.statusListeners.forEach((cb) => cb(connected));
  }
}

export const streamManager = new ExecutionStreamManager();
