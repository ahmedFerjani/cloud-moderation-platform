import { HttpClient } from '@angular/common/http';
import { provideAuth, StsConfigHttpLoader, StsConfigLoader } from 'angular-auth-oidc-client';
import { map } from 'rxjs';
import { APP_CONFIG_PATH } from '../config/config.constants';
import type { AppConfig } from '../config/config.model';

const httpLoaderFactory = (httpClient: HttpClient) => {
  const config$ = httpClient.get<AppConfig>(APP_CONFIG_PATH).pipe(
    map((config: AppConfig) => {
      return {
        ...config.cognito,
        secureRoutes: ['/api'],
        useRefreshToken: true,
        silentRenew: true,
      };
    }),
  );

  return new StsConfigHttpLoader(config$);
};

export const provideOidcAuth = provideAuth({
  loader: {
    provide: StsConfigLoader,
    useFactory: httpLoaderFactory,
    deps: [HttpClient],
  },
});
