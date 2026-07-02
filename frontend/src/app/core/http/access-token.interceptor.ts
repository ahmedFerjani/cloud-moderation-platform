import { inject } from '@angular/core';
import { switchMap, take } from 'rxjs';
import { addAccessToken } from './http-auth.util';
import { AuthService } from '../auth/auth.service';
import type { HttpHandlerFn, HttpRequest } from '@angular/common/http';

export function accessTokenInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn) {
  const authService = inject(AuthService);

  if (!req.url.startsWith('/api')) {
    return next(req);
  }

  return authService.getAccessToken().pipe(
    take(1),
    switchMap((token) => next(addAccessToken(req, token))),
  );
}
