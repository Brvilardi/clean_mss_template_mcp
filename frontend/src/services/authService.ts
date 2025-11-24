import {
  signUp,
  signIn,
  signOut,
  getCurrentUser,
  fetchUserAttributes,
  confirmSignUp,
  resendSignUpCode,
  type SignUpOutput,
  type SignInOutput,
} from 'aws-amplify/auth';
import type { User, SignUpData, AuthError } from '../types/auth';

export class AuthService {
  static async signUp(data: SignUpData): Promise<SignUpOutput> {
    try {
      return await signUp({
        username: data.email,
        password: data.password,
        options: {
          userAttributes: {
            email: data.email,
            'custom:company_name': data.companyName,
            'custom:company_website': data.companyWebsite,
          },
        },
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async confirmSignUp(email: string, code: string): Promise<void> {
    try {
      await confirmSignUp({
        username: email,
        confirmationCode: code,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async resendConfirmationCode(email: string): Promise<void> {
    try {
      await resendSignUpCode({ username: email });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async signIn(email: string, password: string): Promise<SignInOutput> {
    try {
      return await signIn({
        username: email,
        password: password,
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async signOut(): Promise<void> {
    try {
      await signOut();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  static async getCurrentUser(): Promise<User | null> {
    try {
      const { userId } = await getCurrentUser();
      const attributes = await fetchUserAttributes();

      return {
        id: userId,
        email: attributes.email || '',
        companyName: attributes['custom:company_name'] || '',
        companyWebsite: attributes['custom:company_website'] || '',
        createdAt: new Date(),
      };
    } catch {
      return null;
    }
  }

  static async isAuthenticated(): Promise<boolean> {
    try {
      await getCurrentUser();
      return true;
    } catch {
      return false;
    }
  }

  private static handleError(error: any): Error {
    const errorCode = error.__type || error.name || error.code;
    
    const authError: AuthError = {
      message: 'An unexpected error occurred',
      code: errorCode,
    };

    switch (errorCode) {
      case 'UserNotFoundException':
        authError.message = 'No account found with this email';
        break;
      case 'NotAuthorizedException':
        authError.message = 'Invalid email or password';
        break;
      case 'UserNotConfirmedException':
        authError.message = 'Please verify your email first';
        break;
      case 'UsernameExistsException':
        authError.message = 'Account already exists';
        break;
      case 'InvalidPasswordException':
        authError.message = 'Password does not meet requirements';
        break;
      case 'InvalidParameterException':
        authError.message = 'Invalid input';
        break;
      case 'CodeMismatchException':
        authError.message = 'Invalid verification code';
        break;
      case 'ExpiredCodeException':
        authError.message = 'Code expired. Request a new one';
        break;
      case 'LimitExceededException':
        authError.message = 'Too many attempts. Try again later';
        break;
      case 'NetworkError':
        authError.message = 'Network error. Check your connection';
        break;
      default:
        if (error.message) {
          authError.message = error.message;
        }
    }

    const finalError = new Error(authError.message);
    (finalError as any).code = authError.code;
    (finalError as any).name = errorCode;
    return finalError;
  }
}
