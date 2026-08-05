import { inject } from '@angular/core';
import { ModerationResultToastService } from '../websocket/moderation-result-toast.service';

export function initModerationResultToasts() {
  inject(ModerationResultToastService);
}
