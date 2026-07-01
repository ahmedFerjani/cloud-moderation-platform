import { inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { AuthService } from './auth.service';

export function initAuth() {
  const auth = inject(AuthService);

  return firstValueFrom(auth.checkAuth());
}
