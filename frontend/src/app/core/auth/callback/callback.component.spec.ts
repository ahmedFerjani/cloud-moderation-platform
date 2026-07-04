import { TestBed } from '@angular/core/testing';
import { CallbackComponent } from './callback.component';
import type { ComponentFixture} from '@angular/core/testing';

describe('CallbackComponent', () => {
  let component: CallbackComponent;
  let fixture: ComponentFixture<CallbackComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CallbackComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CallbackComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
