import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignUpForm } from '@/components/auth/SignUpForm';
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

export function SignUp() {
  const navigate = useNavigate();
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/app/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSuccess = (email: string) => {
    navigate('/confirm-signup', { state: { email } });
  };

  const handleError = (error: string) => {
    console.error('Sign up error:', error);
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
          <CardTitle className="text-2xl font-bold text-center">
            Create an account
          </CardTitle>
          <CardDescription className="text-center">
            Sign up for re:Invent Planner
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SignUpForm onSuccess={handleSuccess} onError={handleError} />
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="text-sm text-center text-muted-foreground">
            Already have an account?{' '}
            <Button
              variant="link"
              className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
              onClick={() => navigate('/signin')}
            >
              Sign in
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
