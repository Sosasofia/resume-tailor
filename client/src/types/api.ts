export interface ResumeAnalysis {
  match_score: number;
  matching_skills: string[];
  missing_required_skills: string[];
  relevant_experience: string[];
  relevant_projects: string[];
  recommendations: string[];
}