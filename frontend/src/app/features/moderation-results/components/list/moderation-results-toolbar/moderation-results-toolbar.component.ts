import { Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';

export type StatusFilterMode = 'all' | 'safe' | 'unsafe';

@Component({
  selector: 'app-moderation-results-toolbar',
  imports: [
    FormsModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatFormFieldModule,
    MatIconModule,
    MatSelectModule,
  ],
  templateUrl: './moderation-results-toolbar.component.html',
  styleUrl: './moderation-results-toolbar.component.scss',
})
export class ModerationResultsToolbarComponent {
  readonly totalLoaded = input.required<number>();
  readonly selectedFilter = input<StatusFilterMode>('all');
  readonly limit = input.required<number>();
  readonly limitOptions = input<readonly number[]>([]);
  readonly summaryText = input.required<string>();
  readonly isLoading = input(false);

  readonly filterChange = output<StatusFilterMode>();
  readonly limitChange = output<number>();
  readonly refreshRequested = output<void>();

  protected onFilterChange(value: string): void {
    if (value === 'all' || value === 'safe' || value === 'unsafe') {
      this.filterChange.emit(value);
    }
  }

  protected onLimitChange(value: number): void {
    this.limitChange.emit(value);
  }

  protected onRefresh(): void {
    this.refreshRequested.emit();
  }
}
