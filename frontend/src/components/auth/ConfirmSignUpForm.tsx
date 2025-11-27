import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Alert, AlertDescription } from '@/components/ui/alert';

const getConfirmSignUpSchema = (t: (key: string) => string) => z.object({
  code: z
    .string()
    .min(1, t('auth.errors.codeRequired'))
    .length(6, t('auth.errors.codeMustBeSixDigits'))
    .regex(/^\d+$/, t('auth.errors.codeMustBeNumbers')),
});

interface ConfirmSignUpFormProps {
  email: string;
  onSuccess: () => void;
  onError: (error: string) => void;
  onResendCode?: () => void;
}

export function ConfirmSignUpForm({
  email,
  onSuccess,
  onError,
  onResendCode,
}: ConfirmSignUpFormProps) {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const confirmSignUpSchema = getConfirmSignUpSchema(t);
  type ConfirmSignUpFormData = z.infer<typeof confirmSignUpSchema>;

  const form = useForm<ConfirmSignUpFormData>({
    resolver: zodResolver(confirmSignUpSchema),
    defaultValues: {
      code: '',
    },
  });

  const onSubmit = async (data: ConfirmSignUpFormData) => {
    try {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);

      const { useAuthStore } = await import('@/store/authStore');
      await useAuthStore.getState().confirmSignUp(email, data.code);

      setSuccessMessage(t('auth.emailVerified'));
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t('auth.errors.verificationFailed');
      setError(errorMessage);
      onError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      setIsResending(true);
      setError(null);
      setSuccessMessage(null);

      const { AuthService } = await import('@/services/authService');
      await AuthService.resendConfirmationCode(email);

      setSuccessMessage(t('auth.codeResent'));
      if (onResendCode) {
        onResendCode();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t('auth.errors.resendFailed');
      setError(errorMessage);
      onError(errorMessage);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {successMessage && (
        <Alert className="border-green-500/50 bg-green-50 text-green-900 dark:bg-green-900/20 dark:text-green-400">
          <AlertDescription>{successMessage}</AlertDescription>
        </Alert>
      )}

      <div className="text-center space-y-2 mb-6">
        <p className="text-sm text-muted-foreground">
          {t('auth.verificationCodeSentTo')}
        </p>
        <p className="font-semibold text-foreground">{email}</p>
        <p className="text-sm text-muted-foreground">
          {t('auth.enterSixDigitCode')}
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                    maxLength={6}
                    disabled={isLoading}
                    className="text-center text-2xl tracking-widest"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  {t('auth.enterCodeFromEmail')}
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? t('auth.verifying') : t('auth.verifyEmail')}
          </Button>
        </form>
      </Form>

      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">{t('auth.didntReceiveCode')}</p>
        <Button
          variant="link"
          className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
          onClick={handleResendCode}
          disabled={isResending || isLoading}
        >
          {isResending ? t('auth.resending') : t('auth.resendCode')}
        </Button>
      </div>
    </div>
  );
}
