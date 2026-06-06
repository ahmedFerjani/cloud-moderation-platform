import { TestBed } from '@angular/core/testing';
import { ModerationResultsPageComponent } from './moderation-results-page.component';
import type { ComponentFixture } from '@angular/core/testing';

describe('ModerationResultsPageComponent', () => {
  let component: ModerationResultsPageComponent;
  let fixture: ComponentFixture<ModerationResultsPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModerationResultsPageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ModerationResultsPageComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
