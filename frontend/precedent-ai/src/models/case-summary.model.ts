import { CaseFinding } from './case-finding.model';

export interface CaseSummary {
  summary: string;
  findings: CaseFinding[];
}