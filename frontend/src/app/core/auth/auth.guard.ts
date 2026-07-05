import { inject } from '@angular/core';
import { map } from 'rxjs';
import { AuthService } from './auth.service';
import type { CanActivateFn } from '@angular/router';

export const authGuard: CanActivateFn = (_route, state) => {
  const authService = inject(AuthService);

  return authService.isAuthenticated$.pipe(
    map((isAuthenticated) => {
      if (isAuthenticated) {
        return true;
      }

      authService.setRedirectUrl(state.url);
      authService.login();

      return false;
    }),
  );
};
