import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { ShellComponent } from './shell.component';
import { AuthService } from '../../auth/auth.service';
import type { ComponentFixture } from '@angular/core/testing';

describe('ShellComponent', () => {
  let component: ShellComponent;
  let fixture: ComponentFixture<ShellComponent>;

  beforeEach(async () => {
    const authServiceMock: Partial<AuthService> = {
      isAuthenticated: signal(false),
      userProfile: signal({
        name: 'Test User',
        email: 'test@example.com',
        avatarUrl: null,
        initials: 'TU',
      }),
      logout: () => of(null),
    };

    await TestBed.configureTestingModule({
      imports: [ShellComponent],
      providers: [provideRouter([]), { provide: AuthService, useValue: authServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(ShellComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
