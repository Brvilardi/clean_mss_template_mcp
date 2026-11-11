import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ConfirmSignUpForm } from '@/components/auth/ConfirmSignUpForm';
import { useAuthStore } from '@/store/authStore';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export function ConfirmSignUp() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, checkAuth } = useAuthStore();
  const email = location.state?.email || '';
  const fromSignIn = location.state?.fromSignIn || false;
  const password = location.state?.password || '';

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  if (!email) {
    navigate('/signup');
    return null;
  }

  const handleSuccess = async () => {
    if (fromSignIn && password) {
      try {
        const { useAuthStore } = await import('@/store/authStore');
        await useAuthStore.getState().signIn(email, password);
        navigate('/app/dashboard');
      } catch (error) {
        console.error('Auto sign-in failed:', error);
        navigate('/signin', {
          state: { message: 'Email verified! Please sign in' },
        });
      }
    } else {
      navigate('/signin', {
        state: { message: 'Email verified! You can now sign in' },
      });
    }
  };

  const handleError = (error: string) => {
    console.error('Confirmation error:', error);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-orange-50 to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-1 pb-6">
          <div className="flex justify-center mb-4">
            <img 
              src="/dati-logo.png" 
              alt="Dati company logo" 
              className="h-16 w-16 object-contain bg-white p-2 rounded-lg shadow-lg"
            />
          </div>
          <CardTitle className="text-2xl font-bold text-center text-slate-800 dark:text-slate-500">
            Verify your email
          </CardTitle>
          <CardDescription className="text-center text-slate-700 dark:text-slate-400">
            Complete your registration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ConfirmSignUpForm
            email={email}
            onSuccess={handleSuccess}
            onError={handleError}
          />
        </CardContent>
      </Card>
    </div>
  );
}
