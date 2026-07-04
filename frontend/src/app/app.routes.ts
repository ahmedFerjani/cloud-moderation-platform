import { authGuard } from './core/auth/auth.guard';
import { ShellComponent } from './core/layout/shell/shell.component';
import type { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
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
      {
        path: 'dashboard',
        loadChildren: () =>
          import('./features/dashboard/dashboard.routes').then((m) => m.dashboardRoutes),
      },
    ],
  },
  {
    path: 'callback',
    loadComponent: () =>
      import('./core/auth/oidc-callback/oidc-callback.component').then(
        (m) => m.OidcCallbackComponent,
      ),
  },
  {
    path: '**',
    redirectTo: 'upload',
  },
];
