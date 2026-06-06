import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { firstValueFrom } from 'rxjs';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type {
  ModerationResultItem,
  ModerationResultsResponse,
} from '../../models/moderation-results.model';
import type { OnInit } from '@angular/core';

@Component({
  selector: 'app-moderation-results-page',
  imports: [
    DatePipe,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule,
  ],
  templateUrl: './moderation-results-page.component.html',
  styleUrl: './moderation-results-page.component.scss',
})
export class ModerationResultsPageComponent implements OnInit {
  private readonly moderationResultsApiService = inject(ModerationResultsApiService);

  protected readonly limit = signal(1);
  protected readonly limitOptions = [1, 2] as const;
  protected readonly isLoading = signal(true);
  protected readonly isLoadingMore = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly items = signal<ModerationResultItem[]>([]);
  protected readonly count = signal(0);
  protected readonly lastEvaluatedKey = signal<Record<string, string> | null>(null);
  protected readonly hasItems = computed(() => this.items().length > 0);
  protected readonly hasMore = computed(() => this.lastEvaluatedKey() !== null);

  ngOnInit(): void {
    void this.loadModerationResults();
  }

  protected onLimitChange(value: number): void {
    this.limit.set(value);
    void this.loadModerationResults();
  }

  protected async loadModerationResults(): Promise<void> {
    await this.fetchResults('replace');
  }

  protected async loadMore(): Promise<void> {
    await this.fetchResults('append');
  }

  private async fetchResults(mode: 'replace' | 'append'): Promise<void> {
    const isAppendMode = mode === 'append';

    if (isAppendMode) {
      this.isLoadingMore.set(true);
    } else {
      this.isLoading.set(true);
      this.errorMessage.set(null);
      this.lastEvaluatedKey.set(null);
    }

    try {
      const response = await firstValueFrom<ModerationResultsResponse>(
        this.moderationResultsApiService.getModerationResults(
          this.limit(),
          isAppendMode ? this.lastEvaluatedKey() : undefined,
        ),
      );
      if (isAppendMode) {
        this.count.update((current) => current + response.count);
      } else {
        this.count.set(response.count);
      }
      this.lastEvaluatedKey.set(response.last_evaluated_key);

      const mappedItems = this.mapItems(response.items);
      if (isAppendMode) {
        this.items.update((current) => [...current, ...mappedItems]);
      } else {
        this.items.set(mappedItems);
      }
    } catch {
      if (isAppendMode) {
        this.errorMessage.set('Unable to load more results. Please try again.');
      } else {
        this.errorMessage.set('Unable to load moderation results right now. Please try again.');
        this.items.set([]);
        this.count.set(0);
      }
    } finally {
      if (isAppendMode) {
        this.isLoadingMore.set(false);
      } else {
        this.isLoading.set(false);
      }
    }
  }

  private mapItems(items: ModerationResultItem[]): ModerationResultItem[] {
    return items.map((item) => ({
      ...item,
      moderation_labels: item.moderation_labels.slice(0, 5),
    }));
  }
}
