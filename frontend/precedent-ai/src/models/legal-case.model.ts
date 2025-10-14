export interface LegalCase {
  case_name: string;
  summary: string;
  url: string;
  confidence: number;
  jurisdiction: string;
  court?: string;
  year?: number;
  judges: string[];
  legal_topics: string[];
  docket_number?: string;
}
