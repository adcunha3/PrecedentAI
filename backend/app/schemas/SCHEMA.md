[ User Input ]
      │
      ▼
 ┌────────────────────┐
 │ search.py          │
 │ SearchQuery        │
 │  • query: str      │
 └────────────────────┘
      │
      ▼
[ Query Processing ]
      │
      ▼
 ┌──────────────────────────┐
 │ query_processing.py       │
 │ ProcessedQuery            │
 │  • original_query         │
 │  • processed_result       │
 │     → ProcessedQueryLLM  │
 │  • processing_time        │
 └──────────────────────────┘
      │
      ▼
[ Case Retrieval ]
      │
      ▼
 ┌──────────────────────────┐
 │ case.py                   │
 │ Case                      │
 │  • title                  │
 │  • url                    │
 │  • metadata: CaseMetadata │
 │      • judges, court, etc│
 └──────────────────────────┘
      │
      ▼
[ Summarization ]
      │
      ▼
 ┌───────────────────────────┐
 │ case_summary.py            │
 │ CaseSummary                │
 │  • summary                 │
 │  • findings: List[CaseFinding]│
 └───────────────────────────┘
      │
      ▼
[ API Response to User ]
      │
      ▼
 ┌───────────────────────────┐
 │ search.py                  │
 │ SearchResponse             │
 │  • is_valid: bool          │
 │  • cases: List[LegalCase]  │
 │  • web_summary?: CaseSummary│
 └───────────────────────────┘
