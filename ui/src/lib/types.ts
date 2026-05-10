export type CompanyStatus = "generating" | "ready" | "failed";

export interface ScoreBreakdown {
  market: number;
  team: number;
  moat: number;
  traction: number;
  fund_fit: number;
}

export interface Competitor {
  name: string;
  summary: string[];
  strength_score: number;
}

export interface Note {
  id: string;
  body: string;
  created_at: string;
}

export interface CompanyListItem {
  id: string;
  name: string;
  hq: string | null;
  website: string | null;
  market_tag: string | null;
  score_total: number | null;
  favorite: boolean;
  status: CompanyStatus;
  created_at: string;
}

export interface CompanyDetail extends CompanyListItem {
  context: string | null;
  summary: string[] | null;
  investment_thesis: string[] | null;
  risks: string[] | null;
  why_matters: string[] | null;
  score_breakdown: ScoreBreakdown | null;
  memo_markdown: string | null;
  error_message: string | null;
  competitors: Competitor[];
  notes: Note[];
}
