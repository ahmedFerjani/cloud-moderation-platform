import { Service, computed, inject } from '@angular/core';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { map, type Observable } from 'rxjs';
import type { LoginResponse } from 'angular-auth-oidc-client';

export interface AuthUserProfile {
  name: string;
  email: string | null;
  avatarUrl: string | null;
  initials: string | null;
}

interface OidcClaims {
  name?: string;
  email?: string;
  picture?: string;
}

@Service()
export class AuthService {
  private static readonly REDIRECT_URL_KEY = 'auth.redirect-url';

  private readonly oidcSecurityService = inject(OidcSecurityService);

  readonly isAuthenticated = computed(
    () => this.oidcSecurityService.authenticated().isAuthenticated,
  );

  readonly isAuthenticated$ = this.oidcSecurityService.isAuthenticated$.pipe(
    map((r) => r.isAuthenticated),
  );

  readonly userProfile = computed<AuthUserProfile>(() => {
    const userData: { userData?: OidcClaims } = this.oidcSecurityService.userData();
    const { name, email, picture }: OidcClaims = userData.userData ?? {};

    return {
      name: name ?? 'Unknown',
      email: email ?? null,
      avatarUrl: picture ?? null,
      initials: name ? this.getInitials(name) : null,
    };
  });

  checkAuth(): Observable<LoginResponse> {
    return this.oidcSecurityService.checkAuth();
  }

  login(): void {
    this.oidcSecurityService.authorize();
  }

  /**
   * `logoffLocal()` clears the stored ID token so `logoff()` won't append
   * `id_token_hint`. It then relies on the `customParamsEndSessionRequest`
   * config (`client_id` + `logout_uri`) — the params Cognito's hosted UI
   * logout endpoint actually expects
   */
  logout(): Observable<unknown> {
    this.oidcSecurityService.logoffLocal();

    return this.oidcSecurityService.logoff();
  }

  getAccessToken(): Observable<string> {
    return this.oidcSecurityService.getAccessToken();
  }

  setRedirectUrl(url: string): void {
    sessionStorage.setItem(AuthService.REDIRECT_URL_KEY, url);
  }

  getRedirectUrl(): string | null {
    return sessionStorage.getItem(AuthService.REDIRECT_URL_KEY);
  }

  clearRedirectUrl(): void {
    sessionStorage.removeItem(AuthService.REDIRECT_URL_KEY);
  }

  private readonly getInitials = (fullName: string): string => {
    const parts = fullName.trim().split(/\s+/).filter(Boolean);
    const last = parts.length > 1 ? parts.at(-1) : undefined;
    return ((parts.at(0)?.[0] ?? '') + (last?.[0] ?? '')).toUpperCase();
  };
}
