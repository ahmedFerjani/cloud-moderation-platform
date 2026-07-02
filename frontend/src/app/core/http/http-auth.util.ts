import type { HttpRequest } from '@angular/common/http';

export function addAccessToken(
  req: HttpRequest<unknown>,
  token: string | null | undefined,
): HttpRequest<unknown> {
  if (!token) return req;

  return req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });
}
