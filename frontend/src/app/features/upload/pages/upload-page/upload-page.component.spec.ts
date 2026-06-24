import { TestBed } from '@angular/core/testing';
import { UploadPageComponent } from './upload-page.component';
import type { ComponentFixture } from '@angular/core/testing';

describe('UploadPageComponent', () => {
  let component: UploadPageComponent;
  let fixture: ComponentFixture<UploadPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UploadPageComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(UploadPageComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
