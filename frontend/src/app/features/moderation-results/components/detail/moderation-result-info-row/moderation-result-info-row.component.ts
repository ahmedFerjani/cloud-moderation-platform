import { Component, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-moderation-result-info-row',
  imports: [MatIconModule],
  templateUrl: './moderation-result-info-row.component.html',
  styleUrl: './moderation-result-info-row.component.scss',
})
export class ModerationResultInfoRowComponent {
  readonly icon = input.required<string>();
  readonly label = input.required<string>();
}
