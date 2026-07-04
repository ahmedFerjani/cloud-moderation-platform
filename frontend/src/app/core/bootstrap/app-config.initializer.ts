import { inject } from '@angular/core';
import { ConfigService } from '../config/config.service';

export function initConfig() {
  const config = inject(ConfigService);

  return config.load();
}
