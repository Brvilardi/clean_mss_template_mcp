import { post } from 'aws-amplify/api';
import type { AgentInvocationRequest, AgentInvocationResponse } from '../types/api';

export class AgentService {
  private static readonly API_NAME = 'StrandsAgentAPI';
  private static readonly INVOCATION_PATH = '/invocations';

  /**
   * Send a message to the Strands Agent
   */
  static async sendMessage(
    prompt: string,
    sessionId?: string
  ): Promise<AgentInvocationResponse> {
    try {
      const request: AgentInvocationRequest = {
        input: { prompt },
        ...(sessionId && { session_id: sessionId })
      };

      const response = await post({
        apiName: this.API_NAME,
        path: this.INVOCATION_PATH,
        options: {
          body: request as any,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      }).response;

      const data = await response.body.json() as unknown;
      return data as AgentInvocationResponse;

    } catch (error) {
      // Transform error to user-friendly format
      throw this.handleError(error);
    }
  }

  /**
   * Transform API errors to user-friendly messages
   */
  private static handleError(error: any): Error {
    // Service unavailable
    if (error.response?.status === 503) {
      return new Error('The agent service is temporarily unavailable. Please try again in a moment.');
    }

    // Bad request
    if (error.response?.status === 400) {
      return new Error('Invalid request. Please check your message and try again.');
    }

    // Network errors
    if (error.message?.includes('Network') || error.message?.includes('network')) {
      return new Error('Network error. Please check your connection and try again.');
    }

    // Timeout errors
    if (error.message?.includes('timeout') || error.message?.includes('Timeout')) {
      return new Error('Request timed out. Please try again.');
    }

    // Default error
    return new Error('An unexpected error occurred. Please try again.');
  }
}
