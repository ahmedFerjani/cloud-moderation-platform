import { ModerationResultDetailComponent } from './pages/moderation-result-detail/moderation-result-detail.component';
import { ModerationResultsListComponent } from './pages/moderation-results-list/moderation-results-list.component';
import type { Routes } from '@angular/router';

export const moderationResultsRoutes: Routes = [
  { path: '', component: ModerationResultsListComponent },
  { path: ':imageId', component: ModerationResultDetailComponent },
];
