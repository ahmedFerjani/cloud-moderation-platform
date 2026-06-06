import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { environment } from '../../../../environments/environment';
import type { ModerationResultsResponse } from '../models/moderation-results.model';
import type { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ModerationResultsApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = environment.apiBaseUrl.replace(/\/$/, '');

  getModerationResults(): Observable<ModerationResultsResponse> {
    return this.http.get<ModerationResultsResponse>(`${this.apiBaseUrl}/moderation-results`);
  }
}
