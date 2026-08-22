import { Component, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-property-row',
  imports: [MatIconModule],
  templateUrl: './property-row.component.html',
  styleUrl: './property-row.component.scss',
})
export class PropertyRowComponent {
  readonly icon = input.required<string>();
  readonly label = input.required<string>();
}
