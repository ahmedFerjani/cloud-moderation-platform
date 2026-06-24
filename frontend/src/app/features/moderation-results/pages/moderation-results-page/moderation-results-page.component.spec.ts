import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { ModerationResultsPageComponent } from './moderation-results-page.component';
import { ModerationResultsApiService } from '../../data-access/moderation-results-api.service';
import type { ModerationResultsResponse } from '../../models/moderation-results.model';
import type { ComponentFixture } from '@angular/core/testing';

describe('ModerationResultsPageComponent', () => {
  let component: ModerationResultsPageComponent;
  let fixture: ComponentFixture<ModerationResultsPageComponent>;

  beforeEach(async () => {
    const moderationResultsResponse: ModerationResultsResponse = {
      items: [],
      count: 0,
      last_evaluated_key: null,
    };

    await TestBed.configureTestingModule({
      imports: [ModerationResultsPageComponent],
      providers: [
        {
          provide: ModerationResultsApiService,
          useValue: {
            getModerationResults: () => of(moderationResultsResponse),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ModerationResultsPageComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
