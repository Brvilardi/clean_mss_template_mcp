// Request to Strands Agent
// Note: actor_id is no longer needed - it's extracted from Cognito JWT automatically
export interface AgentInvocationRequest {
  input: {
    prompt: string;
  };
  session_id?: string;
  language?: string; // ISO 639-1 code (pt, en)
}

// Response from Strands Agent
export interface AgentInvocationResponse {
  output: {
    message: string;
    timestamp: string;
    model: string;
    session_id?: string;
    actor_id?: string;
  };
}

// Error response
export interface AgentErrorResponse {
  error: {
    type: string;
    message: string;
    details?: string;
    suggestions?: string[];
  };
}
