import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { AlertCircle } from 'lucide-react';
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

const confirmSignUpSchema = z.object({
  code: z
    .string()
    .min(1, 'Code is required')
    .length(6, 'Code must be 6 digits')
    .regex(/^\d+$/, 'Code must be numbers only'),
});

type ConfirmSignUpFormData = z.infer<typeof confirmSignUpSchema>;

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
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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

      setSuccessMessage('Email verified! Redirecting...');
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Verification failed';
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

      setSuccessMessage('Code resent! Check your email');
      if (onResendCode) {
        onResendCode();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to resend code';
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
          Verification code sent to
        </p>
        <p className="font-semibold text-foreground">{email}</p>
        <p className="text-sm text-muted-foreground">
          Enter the 6-digit code below
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="code"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Verification Code</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    placeholder="123456"
                    maxLength={6}
                    disabled={isLoading}
                    className="text-center text-2xl tracking-widest"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Enter the 6-digit code from your email
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Verifying...' : 'Verify Email'}
          </Button>
        </form>
      </Form>

      <div className="text-center space-y-2">
        <p className="text-sm text-muted-foreground">Didn't receive the code?</p>
        <Button
          variant="link"
          className="p-0 h-auto font-semibold text-primary hover:text-primary/80"
          onClick={handleResendCode}
          disabled={isResending || isLoading}
        >
          {isResending ? 'Resending...' : 'Resend Code'}
        </Button>
      </div>
    </div>
  );
}
