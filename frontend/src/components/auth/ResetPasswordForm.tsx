import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '../ui/form';
import { Alert, AlertDescription } from '../ui/alert';
import { passwordSchema } from '../../utils/validators';

const resetPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
  code: z.string().min(6, 'Code must be at least 6 characters'),
  newPassword: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

export function ResetPasswordForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { resetPassword, forgotPassword, isLoading, error, clearError } = useAuthStore();
  const [success, setSuccess] = useState(false);

  const emailFromState = (location.state as any)?.email || '';

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      email: emailFromState,
      code: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    clearError();
    setSuccess(false);

    try {
      await resetPassword(data.email, data.code, data.newPassword);
      setSuccess(true);
      
      // Navigate to sign in after 2 seconds
      setTimeout(() => {
        navigate('/signin');
      }, 2000);
    } catch (err) {
      // Error is handled by the store
    }
  };

  const handleResendCode = async () => {
    const email = form.getValues('email');
    if (!email) {
      form.setError('email', { message: 'Email is required' });
      return;
    }

    try {
      await forgotPassword(email);
    } catch (err) {
      // Error is handled by the store
    }
  };

  return (
    <>
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-4">
          <AlertDescription>
            {t('auth.resetPasswordSuccess')}
          </AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t('auth.email')}</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder={t('auth.placeholders.email')}
                    disabled={isLoading || success}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="code"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t('auth.verificationCode')}</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    placeholder={t('auth.placeholders.verificationCode')}
                    disabled={isLoading || success}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="newPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t('auth.newPassword')}</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder={t('auth.placeholders.password')}
                    disabled={isLoading || success}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t('auth.confirmPassword')}</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder={t('auth.placeholders.password')}
                    disabled={isLoading || success}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full" disabled={isLoading || success}>
            {isLoading ? t('auth.resetting') : t('auth.resetPassword')}
          </Button>

          <div className="flex justify-between text-sm text-slate-700 dark:text-slate-500">
            <Button
              type="button"
              variant="link"
              className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
              onClick={handleResendCode}
              disabled={isLoading || success}
            >
              {t('auth.resendCode')}
            </Button>
            <Button
              type="button"
              variant="link"
              className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
              onClick={() => navigate('/signin')}
              disabled={isLoading}
            >
              {t('auth.backToSignIn')}
            </Button>
          </div>
        </form>
      </Form>
    </>
  );
}
