import { Component, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { firstValueFrom } from 'rxjs';
import { ModerationResultListItemComponent } from '../../components/list/moderation-result-list-item/moderation-result-list-item.component';
import {
  ModerationResultsToolbarComponent,
  type StatusFilterMode,
} from '../../components/list/moderation-results-toolbar/moderation-results-toolbar.component';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type {
  ModerationResultItem,
  ModerationResultsResponse,
} from '../../models/moderation-results.model';
import type { OnInit } from '@angular/core';

@Component({
  selector: 'app-moderation-results-list',
  imports: [
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    ModerationResultListItemComponent,
    ModerationResultsToolbarComponent,
  ],
  templateUrl: './moderation-results-list.component.html',
  styleUrl: './moderation-results-list.component.scss',
})
export class ModerationResultsListComponent implements OnInit {
  private readonly moderationResultsApiService = inject(ModerationResultsApiService);

  protected readonly selectedStatusFilter = signal<'all' | 'safe' | 'unsafe'>('all');
  protected readonly limit = signal(1);
  protected readonly limitOptions = [1, 2] as const;
  protected readonly isLoading = signal(true);
  protected readonly isLoadingMore = signal(false);
  protected readonly errorMessage = signal<string | null>(null);
  protected readonly items = signal<ModerationResultItem[]>([]);
  protected readonly lastEvaluatedKey = signal<Record<string, string> | null>(null);
  protected readonly hasItems = computed(() => this.items().length > 0);
  protected readonly filteredItems = computed(() => {
    const statusFilter = this.selectedStatusFilter();
    if (statusFilter === 'all') {
      return this.items();
    }

    if (statusFilter === 'safe') {
      return this.items().filter((item) => !item.unsafe_detected);
    }

    return this.items().filter((item) => item.unsafe_detected);
  });
  protected readonly hasFilteredItems = computed(() => this.filteredItems().length > 0);
  protected readonly filteredResultsSummary = computed(() => {
    const visibleCount = this.filteredItems().length;
    const totalLoaded = this.items().length;
    const mode = this.selectedStatusFilter();
    const percent = totalLoaded > 0 ? Math.round((visibleCount / totalLoaded) * 100) : 0;

    if (mode === 'safe') {
      return `Showing ${visibleCount} safe results (${percent}% of loaded)`;
    }

    if (mode === 'unsafe') {
      return `Showing ${visibleCount} unsafe results (${percent}% of loaded)`;
    }

    return `Showing ${visibleCount} total results (${percent}% of loaded)`;
  });
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

  protected setStatusFilter(value: StatusFilterMode): void {
    this.selectedStatusFilter.set(value);
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
      moderation_labels: [...item.moderation_labels]
        .sort((left, right) => right.Confidence - left.Confidence)
        .slice(0, 5),
    }));
  }
}
