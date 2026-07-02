import { computed, inject, Service } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { map, type Observable } from 'rxjs';
import type { LoginResponse } from 'angular-auth-oidc-client';

@Service()
export class AuthService {
  private readonly oidcSecurityService = inject(OidcSecurityService);

  readonly userData = this.oidcSecurityService.userData;

  readonly isAuthenticated = computed(
    () => this.oidcSecurityService.authenticated().isAuthenticated,
  );
  readonly isAuthenticated$ = this.oidcSecurityService.isAuthenticated$.pipe(
    map((r) => r.isAuthenticated),
  );

  checkAuth(): Observable<LoginResponse> {
    return this.oidcSecurityService.checkAuth();
  }

  getAccessToken(): Observable<string> {
    return this.oidcSecurityService.getAccessToken();
  }

  login(): void {
    this.oidcSecurityService.authorize();
  }

  logout(): Observable<unknown> {
    return this.oidcSecurityService.logoff();
  }
}
