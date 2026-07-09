import { Component, computed, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../auth/auth.service';

@Component({
  selector: 'app-navbar',
  imports: [
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatDividerModule,
  ],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss',
})
export class NavbarComponent {
  protected readonly authService = inject(AuthService);
  protected readonly userProfile = this.authService.userProfile;

  protected readonly hasAvatar = computed(() => {
    const avatarUrl = this.userProfile().avatarUrl;
    return typeof avatarUrl === 'string' && avatarUrl.length > 0;
  });

  protected onLogout(): void {
    this.authService.logout().subscribe();
  }

  constructor() {
    console.log(this.userProfile());
  }
}
