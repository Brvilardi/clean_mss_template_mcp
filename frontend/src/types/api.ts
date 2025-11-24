// Request to Strands Agent
export interface AgentInvocationRequest {
  input: {
    prompt: string;
  };
  session_id?: string;
}

// Response from Strands Agent
export interface AgentInvocationResponse {
  output: {
    message: string;
    timestamp: string;
    model: string;
    session_id?: string;
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
