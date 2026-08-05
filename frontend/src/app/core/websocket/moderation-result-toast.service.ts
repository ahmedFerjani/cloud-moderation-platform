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
      if (message.status === 'success') {
        if (message.moderationStatus === 'unsafe') {
          this.toastr.warning(
            `Image ${message.imageId} was flagged as unsafe.`,
            'Moderation Result',
          );
        } else {
          this.toastr.success(`Image ${message.imageId} passed moderation.`, 'Moderation Result');
        }
      } else {
        this.toastr.error(
          message.reason ?? `Image ${message.imageId} was rejected.`,
          'Moderation Result',
        );
      }
    });
  }
}
