import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SearchResponse } from '../models/search-response.model';

@Injectable({
  providedIn: 'root'
})
export class QueryService { 

    constructor(private http: HttpClient) { }

    search(query: string): Observable<SearchResponse> {
        return this.http.post<SearchResponse>('http://localhost:8000/search', { query });
    }

}