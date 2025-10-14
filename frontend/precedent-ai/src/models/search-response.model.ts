import { LegalCase } from './legal-case.model';
import { CaseSummary } from './case-summary.model';

export interface SearchResponse {
  is_valid: boolean;
  cases: LegalCase[];
  web_summary: CaseSummary | null;
}
