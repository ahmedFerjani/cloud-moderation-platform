import { ModerationResultDetailComponent } from './pages/moderation-result-detail/moderation-result-detail.component';
import { ModerationResultsComponent } from './pages/moderation-results/moderation-results.component';
import type { Routes } from '@angular/router';

export const moderationResultsRoutes: Routes = [
  { path: '', component: ModerationResultsComponent },
  { path: ':imageId', component: ModerationResultDetailComponent },
];
