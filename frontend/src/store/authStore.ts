import { create } from 'zustand';
import { AuthService } from '../services/authService';
import type { User, SignUpData } from '../types/auth';
import { useChatStore } from './chatStore';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  signUp: (data: SignUpData) => Promise<void>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  checkAuth: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (email: string, code: string, newPassword: string) => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  signUp: async (data: SignUpData) => {
    set({ isLoading: true, error: null });
    
    try {
      const result = await AuthService.signUp(data);
      
      if (result.nextStep.signUpStep === 'CONFIRM_SIGN_UP') {
        set({ isLoading: false, error: null });
      } else if (result.nextStep.signUpStep === 'DONE') {
        await get().signIn(data.email, data.password);
      }
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Sign up failed' 
      });
      throw error;
    }
  },

  confirmSignUp: async (email: string, code: string) => {
    set({ isLoading: true, error: null });
    
    try {
      await AuthService.confirmSignUp(email, code);
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Confirmation failed' 
      });
      throw error;
    }
  },

  signIn: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // Check if already signed in
      const currentUser = await AuthService.getCurrentUser();
      if (currentUser) {
        // Already signed in, just update state
        set({
          user: currentUser,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
        return;
      }
    } catch {
      // Not signed in, continue with sign in
    }
    
    try {
      const result = await AuthService.signIn(email, password);
      
      if (result.isSignedIn) {
        const user = await AuthService.getCurrentUser();
        
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } else {
        // Check if user needs to confirm their email
        if (result.nextStep.signInStep === 'CONFIRM_SIGN_UP') {
          const error = new Error('Please verify your email first');
          (error as any).code = 'UserNotConfirmedException';
          (error as any).name = 'UserNotConfirmedException';
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message,
          });
          throw error;
        }
        
        set({ 
          isLoading: false,
          error: 'Additional authentication required' 
        });
      }
    } catch (error: any) {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error.message || 'Sign in failed',
      });
      throw error;
    }
  },

  signOut: async () => {
    set({ isLoading: true, error: null });
    
    try {
      await AuthService.signOut();
      
      // Clear chat cache on sign out
      useChatStore.getState().clearCache();
      
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.message || 'Sign out failed',
      });
      throw error;
    }
  },

  checkAuth: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const user = await AuthService.getCurrentUser();
      
      if (user) {
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      } else {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      }
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  forgotPassword: async (email: string) => {
    set({ isLoading: true, error: null });
    
    try {
      await AuthService.forgotPassword(email);
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to send reset code' 
      });
      throw error;
    }
  },

  resetPassword: async (email: string, code: string, newPassword: string) => {
    set({ isLoading: true, error: null });
    
    try {
      await AuthService.resetPassword(email, code, newPassword);
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.message || 'Failed to reset password' 
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
