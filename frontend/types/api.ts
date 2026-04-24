export type PredictionItem = {
  name: string;
  confidence: number;
};

export type KnowledgeItem = {
  question: string;
  answer: string;
  score: number;
};

export type ChatResponse = {
  emergency: boolean;
  safety_message: string;
  possible_conditions: PredictionItem[];
  why: string[];
  explanations: KnowledgeItem[];
  response: string;
  disclaimer: string;
};
