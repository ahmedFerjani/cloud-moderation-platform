import { provideHttpClient } from '@angular/common/http';
import {
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
  provideEnvironmentInitializer,
} from '@angular/core';
import { type ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { initAuth } from './core/auth/auth.initializer';
import { initConfig, initIcons, provideOidcAuth } from './core/providers';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(),
    provideRouter(routes),
    provideAppInitializer(initConfig),
    provideAppInitializer(initAuth),
    provideEnvironmentInitializer(initIcons),
    provideOidcAuth,
  ],
};
