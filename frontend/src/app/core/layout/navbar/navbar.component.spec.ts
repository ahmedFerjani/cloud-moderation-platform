import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { NavbarComponent } from './navbar.component';
import { AuthService, type AuthUserProfile } from '../../auth/auth.service';
import type { ComponentFixture } from '@angular/core/testing';

describe('NavbarComponent', () => {
  let component: NavbarComponent;
  let fixture: ComponentFixture<NavbarComponent>;

  const authServiceMock: Pick<AuthService, 'isAuthenticated' | 'userProfile' | 'logout'> = {
    isAuthenticated: signal(true),
    userProfile: signal<AuthUserProfile>({
      name: 'Test User',
      email: 'test@example.com',
      avatarUrl: null,
      initials: 'TU',
    }),
    logout: () => of({}),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavbarComponent],
      providers: [provideRouter([]), { provide: AuthService, useValue: authServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(NavbarComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
