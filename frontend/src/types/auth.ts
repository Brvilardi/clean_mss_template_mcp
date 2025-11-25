export interface User {
  id: string; // Cognito sub (user ID)
  email: string;
  companyName: string;
  companyWebsite: string;
  createdAt: Date;
}

export interface SignUpData {
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  companyWebsite: string;
}

export interface SignInData {
  email: string;
  password: string;
}

export interface AuthError {
  message: string;
  code?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
