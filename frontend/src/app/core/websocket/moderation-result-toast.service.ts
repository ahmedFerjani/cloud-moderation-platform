import { Service, inject } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { WebSocketService } from './websocket.service';

/**
 * Shows a toast notification for each moderation result received over the
 * WebSocket connection.
 */
@Service()
export class ModerationResultToastService {
  private readonly webSocketService = inject(WebSocketService);
  private readonly toastr = inject(ToastrService);

  constructor() {
    this.webSocketService.messages$.subscribe((message) => {
      const label = message.fileName ?? message.imageId;

      if (message.status === 'success') {
        if (message.moderationStatus === 'unsafe') {
          this.toastr.warning(`Image ${label} was flagged as unsafe.`, 'Moderation Result');
        } else {
          this.toastr.success(`Image ${label} passed moderation.`, 'Moderation Result');
        }
      } else {
        this.toastr.error(message.reason ?? `Image ${label} was rejected.`, 'Moderation Result');
      }
    });
  }
}
