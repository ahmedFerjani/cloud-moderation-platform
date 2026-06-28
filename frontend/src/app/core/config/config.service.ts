import { HttpClient } from '@angular/common/http';
import { inject, Service } from '@angular/core';
import { firstValueFrom } from 'rxjs/internal/firstValueFrom';
import { APP_CONFIG_PATH } from './config.constants';
import type { AppConfig } from './config.model';

@Service()
export class ConfigService {
  private readonly http = inject(HttpClient);
  private config: AppConfig | null = null;

  async load(): Promise<void> {
    try {
      const cfg = await firstValueFrom(this.http.get<AppConfig>(APP_CONFIG_PATH));

      this.config = cfg;
    } catch (error) {
      const message =
        `Failed to load runtime application configuration from ${APP_CONFIG_PATH}. ` +
        `Ensure the file exists and is correctly deployed.`;
      throw new Error(message, { cause: error });
    }
  }

  get(): AppConfig {
    if (!this.config) {
      throw new Error('Runtime application configuration is not loaded');
    }
    return this.config;
  }
}
