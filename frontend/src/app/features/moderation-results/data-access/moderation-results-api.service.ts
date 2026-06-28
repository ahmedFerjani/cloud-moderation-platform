import { HttpClient } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { environment } from '../../../../environments/environment';
import type { ModerationResultsResponse } from '../models/moderation-results.model';
import type { Observable } from 'rxjs';

@Service()
export class ModerationResultsApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = environment.apiBaseUrl.replace(/\/$/, '');

  getModerationResults(
    limit?: number,
    lastEvaluatedKey?: Record<string, string> | null,
  ): Observable<ModerationResultsResponse> {
    const queryParams: Record<string, string | number> = {};
    if (limit) queryParams['limit'] = limit;
    if (lastEvaluatedKey) queryParams['last_evaluated_key'] = JSON.stringify(lastEvaluatedKey);
    return this.http.get<ModerationResultsResponse>(`${this.apiBaseUrl}/images`, {
      params: queryParams,
    });
  }
}
