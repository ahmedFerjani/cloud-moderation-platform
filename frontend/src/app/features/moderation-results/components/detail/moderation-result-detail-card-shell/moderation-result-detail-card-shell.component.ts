import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-moderation-result-detail-card-shell',
  imports: [MatCardModule],
  templateUrl: './moderation-result-detail-card-shell.component.html',
  styleUrl: './moderation-result-detail-card-shell.component.scss',
})
export class ModerationResultDetailCardShellComponent {
  readonly title = input<string>('');
}
