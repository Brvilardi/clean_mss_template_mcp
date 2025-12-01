import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SignInForm } from '@/components/auth/SignInForm';
import { useAuthStore } from '@/store/authStore';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export function SignIn() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, checkAuth } = useAuthStore();
  const [needsConfirmation, setNeedsConfirmation] = useState(false);
  const [confirmationEmail, setConfirmationEmail] = useState('');
  const [confirmationPassword, setConfirmationPassword] = useState('');

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSuccess = () => {
    navigate('/app/dashboard');
  };

  const handleError = (error: string) => {
    console.error('Sign in error:', error);
  };

  const handleConfirmationNeeded = (email: string, password: string) => {
    setNeedsConfirmation(true);
    setConfirmationEmail(email);
    setConfirmationPassword(password);
  };

  const handleGoToConfirmation = () => {
    navigate('/confirm-signup', { 
      state: { 
        email: confirmationEmail, 
        password: confirmationPassword,
        fromSignIn: true 
      } 
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-orange-50 to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-1 pb-6">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">re:</span>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center text-slate-800 dark:text-slate-500">
            {t('auth.welcomeBack')}
          </CardTitle>
          <CardDescription className="text-center text-slate-700 dark:text-slate-400">
            {t('auth.signInToAccount')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SignInForm
            onSuccess={handleSuccess}
            onError={handleError}
            onConfirmationNeeded={handleConfirmationNeeded}
          />
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          {needsConfirmation && (
            <div className="text-sm text-center text-slate-700 dark:text-slate-400">
              {t('auth.needToVerifyEmail')}{' '}
              <Button
                variant="link"
                className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
                onClick={handleGoToConfirmation}
              >
                {t('auth.enterConfirmationCode')}
              </Button>
            </div>
          )}
          <div className="text-sm text-center text-slate-700 dark:text-slate-400">
            {t('auth.dontHaveAccount')}{' '}
            <Button
              variant="link"
              className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
              onClick={() => navigate('/signup')}
            >
              {t('auth.clickHereToSignUp')}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
