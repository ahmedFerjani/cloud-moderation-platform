import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
  provideEnvironmentInitializer,
} from '@angular/core';
import { type ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideToastr } from 'ngx-toastr';
import { routes } from './app.routes';
import {
  initConfig,
  initIcons,
  initModerationResultToasts,
  initWebSocket,
  provideOidcAuth,
} from './core/bootstrap';
import { accessTokenInterceptor } from './core/http/interceptors/access-token.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(withInterceptors([accessTokenInterceptor])),
    provideRouter(routes),
    provideAppInitializer(initConfig),
    provideEnvironmentInitializer(initIcons),
    provideEnvironmentInitializer(initWebSocket),
    provideEnvironmentInitializer(initModerationResultToasts),
    provideOidcAuth,
    provideToastr(),
  ],
};
