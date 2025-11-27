import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { AlertCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { signInSchema, type SignInFormData } from '@/utils/validators';

interface SignInFormProps {
  onSuccess: () => void;
  onError: (error: string) => void;
  onConfirmationNeeded?: (email: string, password: string) => void;
}

export function SignInForm({ onSuccess, onError, onConfirmationNeeded }: SignInFormProps) {
  const { t } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: SignInFormData) => {
    try {
      setIsLoading(true);
      setError(null);

      const { useAuthStore } = await import('@/store/authStore');
      await useAuthStore.getState().signIn(data.email, data.password);

      onSuccess();
    } catch (err) {
      const errorCode = (err as any).code || (err as any).name;
      
      if (errorCode === 'UserNotConfirmedException') {
        const displayMessage = err instanceof Error ? err.message : t('auth.pleaseVerifyEmail');
        setError(displayMessage);
        if (onConfirmationNeeded) {
          onConfirmationNeeded(data.email, data.password);
        }
      } else {
        const displayMessage = err instanceof Error ? err.message : t('auth.errors.signInFailed');
        setError(displayMessage);
        onError(displayMessage);
      }
      setIsLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

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
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('auth.password')}</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder={t('auth.placeholders.password')}
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? t('auth.signingIn') : t('auth.signIn')}
        </Button>
      </form>
    </Form>
  );
}
