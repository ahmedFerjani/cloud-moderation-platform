import { Component, computed, input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { PropertyRowComponent } from '../../../../../shared/components/property-row/property-row.component';
import { ModerationResultDetailCardShellComponent } from '../moderation-result-detail-card-shell/moderation-result-detail-card-shell.component';
import type { ModerationResultItem, ViewAccess } from '../../../models/moderation-results.model';

@Component({
  selector: 'app-moderation-result-image-access-card',
  imports: [
    MatButtonModule,
    MatIconModule,
    ModerationResultDetailCardShellComponent,
    PropertyRowComponent,
  ],
  templateUrl: './moderation-result-image-access-card.component.html',
  styleUrl: './moderation-result-image-access-card.component.scss',
})
export class ModerationResultImageAccessCardComponent {
  readonly item = input.required<ModerationResultItem>();
  readonly nowMs = input.required<number>();
  readonly isRefreshingViewAccess = input(false);
  readonly viewAccessErrorMessage = input<string | null>(null);
  readonly onRenew = input<() => void | Promise<void>>(() => undefined);

  readonly currentViewAccess = computed(() => this.item().view_access ?? null);

  readonly viewAccessRemainingSeconds = computed(() => {
    const access = this.currentViewAccess();
    if (!access) {
      return null;
    }

    const issuedAtMs = Date.parse(access.issued_at);
    if (Number.isNaN(issuedAtMs)) {
      return null;
    }

    const expiresAtMs = issuedAtMs + access.expires_in * 1000;
    return Math.max(0, Math.floor((expiresAtMs - this.nowMs()) / 1000));
  });

  readonly isViewAccessActive = computed(() => {
    const remaining = this.viewAccessRemainingSeconds();
    return remaining !== null && remaining > 0;
  });

  protected formatRemainingTime(totalSeconds: number | null): string {
    if (totalSeconds === null) {
      return 'Unavailable';
    }

    const minutes = Math.floor(totalSeconds / 60)
      .toString()
      .padStart(2, '0');
    const seconds = (totalSeconds % 60).toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  }

  protected getUrlStatusLabel(viewAccess: ViewAccess | null): string {
    if (!viewAccess) {
      return 'Unavailable';
    }

    return this.isViewAccessActive() ? 'Active' : 'Expired';
  }
}
