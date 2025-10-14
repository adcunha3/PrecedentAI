import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { QueryService } from '../../services/query.service';
import { LegalCase } from '../../models/legal-case.model';
import { CaseSummary } from '../../models/case-summary.model';

@Component({
  selector: 'app-landing-page',
  imports: [CommonModule, FormsModule],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {
  searchQuery: string = '';
  cases: LegalCase[] = [];
  caseSummary: CaseSummary | null = null;
  isLoading: boolean = false;

  constructor(private queryService: QueryService) { }

  onSearch() {
    if (!this.searchQuery.trim()) return;
    
    this.isLoading = true;
    this.queryService.search(this.searchQuery).subscribe((response) => {
      this.cases = response.cases;
      this.caseSummary = response.web_summary;
      this.isLoading = false;
    });
  }
}
