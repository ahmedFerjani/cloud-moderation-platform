import { Component, inject } from '@angular/core';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../auth.service';
import type { OnInit } from '@angular/core';

@Component({
  selector: 'app-oidc-callback',
  templateUrl: './oidc-callback.component.html',
  imports: [MatProgressSpinner],
})
export class OidcCallbackComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  ngOnInit(): void {
    void this.handleCallback();
  }

  private async handleCallback(): Promise<void> {
    const response = await firstValueFrom(this.auth.checkAuth());

    if (!response.isAuthenticated) {
      return;
    }

    const redirectUrl = this.auth.getRedirectUrl() ?? '/upload';

    this.auth.clearRedirectUrl();

    await this.router.navigateByUrl(redirectUrl);
  }
}
