import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { ModerationResultsComponent } from './moderation-results.component';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type { ModerationResultsResponse } from '../../models/moderation-results.model';
import type { ComponentFixture } from '@angular/core/testing';

describe('ModerationResultsComponent', () => {
  let component: ModerationResultsComponent;
  let fixture: ComponentFixture<ModerationResultsComponent>;

  beforeEach(async () => {
    const moderationResultsResponse: ModerationResultsResponse = {
      items: [],
      count: 0,
      last_evaluated_key: null,
    };

    await TestBed.configureTestingModule({
      imports: [ModerationResultsComponent],
      providers: [
        {
          provide: ModerationResultsApiService,
          useValue: {
            getModerationResults: () => of(moderationResultsResponse),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ModerationResultsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
