export type JobType = "Remoto" | "Híbrido" | "Presencial";

export interface Job {
  id: string;
  companyId: string;
  companyName: string;
  title: string;
  description: string;
  requirements: string[];
  salary: string;
  type: JobType;
  location: string;
  status: "Ativa" | "Rascunho" | "Fechada";
  postedAt: string;
}

export type CandidateStatus = "Aplicado" | "Triagem" | "Entrevista" | "Selecionado" | "Rejeitado";

export interface Candidate {
  id: string;
  name: string;
  email: string;
  skills: string[];
  experience: string;
  location: string;
  githubUrl?: string;
  linkedinUrl?: string;
}

export interface Application {
  id: string;
  jobId: string;
  candidateId: string;
  status: CandidateStatus;
  appliedAt: string;
  matchScore: number;
}
