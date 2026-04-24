export type PredictionItem = {
  condition: string;
  confidence: number;
};

export type KnowledgeItem = {
  question: string;
  answer: string;
  source: string;
  score: number;
  focus?: string | null;
  qtype?: string | null;
};

export type ChatResponse = {
  user_message: string;
  emergency: boolean;
  disclaimer: string;
  possible_conditions: PredictionItem[];
  knowledge_summary: KnowledgeItem[];
  assistant_response: string;
  suggested_next_steps: string[];
  urgent_care_reasons: string[];
  metadata: Record<string, unknown>;
};

export type PredictResponse = {
  user_message: string;
  disclaimer: string;
  possible_conditions: PredictionItem[];
};
