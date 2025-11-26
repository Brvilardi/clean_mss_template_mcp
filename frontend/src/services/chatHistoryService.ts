import { fetchAuthSession } from 'aws-amplify/auth';

/**
 * Parsed event from chat history API (simplified by backend)
 */
export interface SessionEvent {
  event_id: string;
  timestamp: string;
  type: 'text' | 'tool_use' | 'tool_result' | 'blob' | 'error' | 'unknown';
  role: 'user' | 'assistant' | 'system' | 'unknown';
  content: string | ToolUseContent | ToolResultContent | any;
}

/**
 * Tool use content structure
 */
export interface ToolUseContent {
  tool_name: string;
  tool_input: Record<string, any>;
}

/**
 * Tool result content structure
 */
export interface ToolResultContent {
  tool_use_id: string;
  status: string;
  result: string | null;
}

/**
 * Response from chat history API when fetching session events
 */
export interface SessionEventsResponse {
  session_id: string;
  actor_id: string;
  events: SessionEvent[];
  event_count: number;
  timestamp: string;
}

/**
 * Error response from chat history API
 */
export interface ChatHistoryError extends Error {
  suggestions?: string[];
  isRetryable?: boolean;
  statusCode?: number;
}

/**
 * Retry configuration
 */
interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
}

/**
 * Service for managing chat history and session events
 */
export class ChatHistoryService {
  // Get API endpoint from environment or Amplify config
  // Chat history is at /mss-template/chat_history, not under /agent
  private static readonly API_ENDPOINT = 
    import.meta.env.VITE_API_ENDPOINT?.replace('/agent', '') || 
    'https://8cjlle5daa.execute-api.us-east-1.amazonaws.com/prod/mss-template';

  // Default retry configuration
  private static readonly DEFAULT_RETRY_CONFIG: RetryConfig = {
    maxRetries: 3,
    initialDelayMs: 1000,
    maxDelayMs: 10000,
    backoffMultiplier: 2
  };

  /**
   * Get events/messages for a specific session
   * 
   * @param sessionId - The session ID to fetch events for
   * @returns Promise with session events response
   * @throws ChatHistoryError with user-friendly message and retry suggestions
   */
  static async getSessionEvents(sessionId: string): Promise<SessionEventsResponse> {
    if (!sessionId || sessionId.trim() === '') {
      throw this.createError(
        'Session ID is required',
        ['Provide a valid session ID'],
        false,
        400
      );
    }

    return this.fetchWithRetry(async () => {
      try {
        // Get the current auth session to retrieve the ID token
        const session = await fetchAuthSession();
        const idToken = session.tokens?.idToken?.toString();

        if (!idToken) {
          throw this.createError(
            'Not authenticated. Please sign in.',
            ['Sign out and sign back in', 'Refresh the page'],
            false,
            401
          );
        }

        console.log('🔐 Fetching session events:', {
          sessionId,
          hasToken: !!idToken,
          endpoint: `${this.API_ENDPOINT}/chat_history`
        });

        const url = `${this.API_ENDPOINT}/chat_history?session_id=${encodeURIComponent(sessionId)}`;
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
          }
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw this.createError(
            errorData.message || `HTTP ${response.status}`,
            this.getSuggestionsForStatus(response.status),
            this.isRetryableStatus(response.status),
            response.status
          );
        }

        const data = await response.json();
        console.log('✅ Session events retrieved:', {
          sessionId,
          eventCount: data.event_count
        });

        return data as SessionEventsResponse;

      } catch (error) {
        console.error('❌ Chat history service error:', error);
        
        // If it's already a ChatHistoryError, rethrow it
        if ((error as ChatHistoryError).suggestions !== undefined) {
          throw error;
        }
        
        // Otherwise, transform it
        throw this.handleError(error);
      }
    });
  }

  /**
   * Fetch with exponential backoff retry logic
   * 
   * @param fetchFn - The fetch function to retry
   * @param config - Retry configuration (optional)
   * @returns Promise with the fetch result
   */
  private static async fetchWithRetry<T>(
    fetchFn: () => Promise<T>,
    config: RetryConfig = this.DEFAULT_RETRY_CONFIG
  ): Promise<T> {
    let lastError: any;
    let delay = config.initialDelayMs;

    for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
      try {
        return await fetchFn();
      } catch (error: any) {
        lastError = error;

        // Don't retry if error is not retryable
        if (!error.isRetryable) {
          throw error;
        }

        // Don't retry if we've exhausted attempts
        if (attempt >= config.maxRetries) {
          console.error(`❌ Max retries (${config.maxRetries}) exceeded`);
          throw error;
        }

        // Calculate delay with exponential backoff
        const currentDelay = Math.min(delay, config.maxDelayMs);
        console.log(`⏳ Retry attempt ${attempt + 1}/${config.maxRetries} after ${currentDelay}ms`);

        // Wait before retrying
        await this.sleep(currentDelay);

        // Increase delay for next attempt
        delay *= config.backoffMultiplier;
      }
    }

    throw lastError;
  }

  /**
   * Sleep for specified milliseconds
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Create a ChatHistoryError with specified properties
   */
  private static createError(
    message: string,
    suggestions: string[],
    isRetryable: boolean,
    statusCode?: number
  ): ChatHistoryError {
    const error = new Error(message) as ChatHistoryError;
    error.suggestions = suggestions;
    error.isRetryable = isRetryable;
    error.statusCode = statusCode;
    return error;
  }

  /**
   * Check if HTTP status code is retryable
   */
  private static isRetryableStatus(status: number): boolean {
    // Retry on server errors (5xx) and rate limiting (429)
    return status >= 500 || status === 429;
  }

  /**
   * Get user-friendly suggestions based on HTTP status code
   */
  private static getSuggestionsForStatus(status: number): string[] {
    switch (status) {
      case 400:
        return [
          'Check that the session ID is valid',
          'Ensure the session exists',
          'Try refreshing the page'
        ];
      case 401:
        return [
          'Sign out and sign back in',
          'Check if your session has expired',
          'Clear your browser cache and try again'
        ];
      case 403:
        return [
          'You may not have permission to access this session',
          'Contact your administrator',
          'Verify your account has the necessary permissions'
        ];
      case 404:
        return [
          'This session may not exist',
          'Check that the session ID is correct',
          'The session may have been deleted'
        ];
      case 429:
        return [
          'Wait a minute before trying again',
          'Avoid making too many requests rapidly'
        ];
      case 500:
      case 502:
      case 503:
      case 504:
        return [
          'The service is temporarily unavailable',
          'Wait a few moments and try again',
          'Contact support if the issue persists'
        ];
      default:
        return [
          'Try refreshing the page',
          'Check your internet connection',
          'Contact support if the issue persists'
        ];
    }
  }

  /**
   * Transform API errors to user-friendly messages with actionable suggestions
   */
  private static handleError(error: any): ChatHistoryError {
    // Network errors
    if (error.message?.includes('Network') || error.message?.includes('network') || 
        error.name === 'NetworkError' || error.code === 'ERR_NETWORK') {
      return this.createError(
        'Network error. Please check your internet connection.',
        [
          'Check your internet connection',
          'Try refreshing the page',
          'Disable VPN if you are using one',
          'Check if your firewall is blocking the connection'
        ],
        true
      );
    }

    // Timeout errors
    if (error.message?.includes('timeout') || error.message?.includes('Timeout') ||
        error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
      return this.createError(
        'Request timed out. The service is taking too long to respond.',
        [
          'Check your internet connection speed',
          'Wait a moment and retry',
          'Contact support if the issue persists'
        ],
        true
      );
    }

    // CORS errors
    if (error.message?.includes('CORS') || error.message?.includes('cors')) {
      return this.createError(
        'Configuration error. Please contact support.',
        [
          'This is a configuration issue',
          'Contact support for assistance'
        ],
        false
      );
    }

    // Default error
    return this.createError(
      error.message || 'An unexpected error occurred. Please try again.',
      [
        'Try refreshing the page',
        'Clear your browser cache',
        'Contact support if the issue persists'
      ],
      true
    );
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
