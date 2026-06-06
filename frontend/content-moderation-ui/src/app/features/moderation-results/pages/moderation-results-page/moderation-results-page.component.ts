import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { firstValueFrom } from 'rxjs';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type {
  ModerationResultItem,
  ModerationResultsResponse,
} from '../../models/moderation-results.model';
import type { OnInit } from '@angular/core';

type ModerationResultViewModel = ModerationResultItem & {
  timestampLabel: string;
  topLabels: string;
};

@Component({
  selector: 'app-moderation-results-page',
  imports: [MatCardModule, MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './moderation-results-page.component.html',
  styleUrl: './moderation-results-page.component.scss',
})
export class ModerationResultsPageComponent implements OnInit {
  private readonly moderationResultsApiService = inject(ModerationResultsApiService);

  protected readonly isLoading = signal(true);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly items = signal<ModerationResultViewModel[]>([]);
  protected readonly count = signal(0);
  protected readonly hasItems = computed(() => this.items().length > 0);

  ngOnInit(): void {
    void this.loadModerationResults();
  }

  protected async loadModerationResults(): Promise<void> {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    try {
      const response = await firstValueFrom<ModerationResultsResponse>(
        this.moderationResultsApiService.getModerationResults(),
      );
      this.count.set(response.count);
      this.items.set(
        response.items.map((item: ModerationResultItem) => ({
          ...item,
          timestampLabel: this.formatTimestamp(item.timestamp),
          topLabels: item.moderation_labels
            .slice(0, 3)
            .map((label) => label.Name)
            .join(', '),
        })),
      );
    } catch {
      this.errorMessage.set('Unable to load moderation results right now. Please try again.');
      this.items.set([]);
      this.count.set(0);
    } finally {
      this.isLoading.set(false);
    }
  }

  private formatTimestamp(value: string): string {
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }

    return new Intl.DateTimeFormat('en', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(parsed);
  }
}
