import { post } from 'aws-amplify/api';
import type { AgentInvocationRequest, AgentInvocationResponse } from '../types/api';

export interface AgentError extends Error {
  suggestions?: string[];
  isRetryable?: boolean;
}

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
   * Transform API errors to user-friendly messages with actionable suggestions
   */
  private static handleError(error: any): AgentError {
    const agentError = new Error() as AgentError;

    // Service unavailable (503)
    if (error.response?.status === 503) {
      agentError.message = 'The agent service is temporarily unavailable. Please try again in a moment.';
      agentError.suggestions = [
        'Wait a few moments and try again',
        'Check the AWS service status page',
        'Contact support if the issue persists'
      ];
      agentError.isRetryable = true;
      return agentError;
    }

    // Bad request (400)
    if (error.response?.status === 400) {
      agentError.message = 'Invalid request. Please check your message and try again.';
      agentError.suggestions = [
        'Ensure your message is not empty',
        'Try rephrasing your question',
        'Avoid special characters that might cause issues'
      ];
      agentError.isRetryable = false;
      return agentError;
    }

    // Unauthorized (401)
    if (error.response?.status === 401) {
      agentError.message = 'Authentication failed. Please sign in again.';
      agentError.suggestions = [
        'Sign out and sign back in',
        'Check if your session has expired',
        'Clear your browser cache and try again'
      ];
      agentError.isRetryable = false;
      return agentError;
    }

    // Forbidden (403)
    if (error.response?.status === 403) {
      agentError.message = 'Access denied. You do not have permission to use this service.';
      agentError.suggestions = [
        'Contact your administrator',
        'Verify your account has the necessary permissions'
      ];
      agentError.isRetryable = false;
      return agentError;
    }

    // Not found (404)
    if (error.response?.status === 404) {
      agentError.message = 'Service endpoint not found. Please contact support.';
      agentError.suggestions = [
        'Verify the application is properly configured',
        'Contact support for assistance'
      ];
      agentError.isRetryable = false;
      return agentError;
    }

    // Rate limiting (429)
    if (error.response?.status === 429) {
      agentError.message = 'Too many requests. Please slow down and try again.';
      agentError.suggestions = [
        'Wait a minute before sending another message',
        'Avoid sending multiple messages rapidly'
      ];
      agentError.isRetryable = true;
      return agentError;
    }

    // Network errors
    if (error.message?.includes('Network') || error.message?.includes('network') || 
        error.name === 'NetworkError' || error.code === 'ERR_NETWORK') {
      agentError.message = 'Network error. Please check your internet connection.';
      agentError.suggestions = [
        'Check your internet connection',
        'Try refreshing the page',
        'Disable VPN if you are using one',
        'Check if your firewall is blocking the connection'
      ];
      agentError.isRetryable = true;
      return agentError;
    }

    // Timeout errors
    if (error.message?.includes('timeout') || error.message?.includes('Timeout') ||
        error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
      agentError.message = 'Request timed out. The service is taking too long to respond.';
      agentError.suggestions = [
        'Try again with a shorter message',
        'Check your internet connection speed',
        'Wait a moment and retry'
      ];
      agentError.isRetryable = true;
      return agentError;
    }

    // CORS errors
    if (error.message?.includes('CORS') || error.message?.includes('cors')) {
      agentError.message = 'Configuration error. Please contact support.';
      agentError.suggestions = [
        'This is a configuration issue',
        'Contact support for assistance'
      ];
      agentError.isRetryable = false;
      return agentError;
    }

    // Default error
    agentError.message = 'An unexpected error occurred. Please try again.';
    agentError.suggestions = [
      'Try refreshing the page',
      'Clear your browser cache',
      'Contact support if the issue persists'
    ];
    agentError.isRetryable = true;
    return agentError;
  }

  /**
   * Check if the browser is online
   */
  static isOnline(): boolean {
    return navigator.onLine;
  }

  /**
   * Detect network connectivity
   */
  static async checkConnectivity(): Promise<boolean> {
    if (!navigator.onLine) {
      return false;
    }

    try {
      // Try to fetch a small resource to verify connectivity
      await fetch('https://www.google.com/favicon.ico', {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-cache'
      });
      return true;
    } catch {
      return false;
    }
  }
}
