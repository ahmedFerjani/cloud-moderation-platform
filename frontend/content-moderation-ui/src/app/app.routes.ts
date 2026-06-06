import { ShellComponent } from './core/layout/shell/shell.component';
import type { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'upload',
      },
      {
        path: 'upload',
        loadChildren: () => import('./features/upload/upload.routes').then((m) => m.uploadRoutes),
      },
      {
        path: 'moderation-results',
        loadChildren: () =>
          import('./features/moderation-results/moderation-results.routes').then(
            (m) => m.moderationResultsRoutes,
          ),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'upload',
  },
];
