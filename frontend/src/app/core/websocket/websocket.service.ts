import { Service, effect, inject } from '@angular/core';
import { Subject, firstValueFrom, timer } from 'rxjs';
import { webSocket, type WebSocketSubject } from 'rxjs/webSocket';
import { AuthService } from '../auth/auth.service';
import { ConfigService } from '../config/config.service';
import type { ModerationResultMessage } from './websocket.model';

const RECONNECT_INITIAL_DELAY_MS = 1_000;
const RECONNECT_MAX_DELAY_MS = 30_000;

/**
 * Maintains a single WebSocket connection for the lifetime of the app,
 * opening it when the user is authenticated and tearing it down on logout.
 * Reconnects automatically after unexpected disconnects while still
 * authenticated (e.g. idle timeouts on the API Gateway connection), backing
 * off exponentially (capped) so repeated failures don't hammer the server.
 */
@Service()
export class WebSocketService {
  private readonly authService = inject(AuthService);
  private readonly configService = inject(ConfigService);

  private socket$: WebSocketSubject<ModerationResultMessage> | null = null;
  private connecting = false;
  private manualDisconnect = false;
  private nextReconnectDelay = RECONNECT_INITIAL_DELAY_MS;

  private readonly messagesSubject = new Subject<ModerationResultMessage>();
  readonly messages$ = this.messagesSubject.asObservable();

  constructor() {
    this.handleAuthStateChange();
  }

  private handleAuthStateChange(): void {
    effect(() => {
      if (this.authService.isAuthenticated()) {
        void this.connect();
      } else {
        this.disconnect();
      }
    });
  }

  private async connect(): Promise<void> {
    if (this.socket$ || this.connecting) {
      return;
    }

    this.connecting = true;

    try {
      const accessToken$ = this.authService.getAccessToken();
      const token = await firstValueFrom(accessToken$);
      this.openSocket(token);
    } catch {
      this.handleConnectionLost();
    } finally {
      this.connecting = false;
    }
  }

  private openSocket(token: string): void {
    this.socket$ = webSocket<ModerationResultMessage>({
      url: this.buildSocketUrl(token),
      openObserver: {
        next: () => {
          this.nextReconnectDelay = RECONNECT_INITIAL_DELAY_MS;
        },
      },
    });

    this.socket$.subscribe({
      next: (message) => this.messagesSubject.next(message),
      error: () => this.handleConnectionLost(),
      complete: () => this.handleConnectionLost(),
    });
  }

  private buildSocketUrl(token: string): string {
    const { websocketUrl } = this.configService.get();
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';

    return `${scheme}://${window.location.host}${websocketUrl}?token=${encodeURIComponent(token)}`;
  }

  private handleConnectionLost(): void {
    this.socket$ = null;

    if (this.manualDisconnect || !this.authService.isAuthenticated()) {
      this.manualDisconnect = false;
      return;
    }

    const delay = this.nextReconnectDelay;
    this.nextReconnectDelay = Math.min(this.nextReconnectDelay * 2, RECONNECT_MAX_DELAY_MS);

    timer(delay).subscribe(() => void this.connect());
  }

  private disconnect(): void {
    this.manualDisconnect = true;
    this.nextReconnectDelay = RECONNECT_INITIAL_DELAY_MS;
    this.socket$?.complete();
    this.socket$ = null;
  }
}
