import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { AuthService } from '../auth.service';
import { OidcCallbackComponent } from './oidc-callback.component';
import type { ComponentFixture } from '@angular/core/testing';

describe('OidcCallbackComponent', () => {
  let component: OidcCallbackComponent;
  let fixture: ComponentFixture<OidcCallbackComponent>;
  const navigateByUrl = () => Promise.resolve(true);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OidcCallbackComponent],
      providers: [
        {
          provide: AuthService,
          useValue: {
            checkAuth: () => of({}),
          },
        },
        {
          provide: Router,
          useValue: {
            navigateByUrl,
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OidcCallbackComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
