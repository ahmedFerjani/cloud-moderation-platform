import { Routes } from '@angular/router';
import { ShellComponent } from './core/layout/shell/shell.component';

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
        loadChildren: () => import('./features/upload/routes').then((m) => m.routes),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'upload',
  },
];
