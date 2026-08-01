import { inject } from '@angular/core';
import { WebSocketService } from '../websocket/websocket.service';

export function initWebSocket() {
  inject(WebSocketService);
}
