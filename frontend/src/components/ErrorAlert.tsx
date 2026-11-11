import { useTranslation } from 'react-i18next';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Button } from './ui/button';
import { AlertCircle, X } from 'lucide-react';

interface ErrorAlertProps {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  suggestions?: string[];
}

export function ErrorAlert({ error, onRetry, onDismiss, suggestions }: ErrorAlertProps) {
  const { t } = useTranslation();

  return (
    <Alert 
      variant="destructive" 
      className="relative"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <AlertCircle className="h-4 w-4" aria-hidden="true" />
      <AlertTitle className="flex items-center justify-between">
        <span>{t('common.error')}</span>
        {onDismiss && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 hover:bg-red-100 dark:hover:bg-red-900 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            onClick={onDismiss}
            aria-label={t('errors.dismissError')}
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </Button>
        )}
      </AlertTitle>
      <AlertDescription className="mt-2 space-y-2">
        <p>{error}</p>
        
        {suggestions && suggestions.length > 0 && (
          <div className="mt-3">
            <p className="font-medium mb-1">{t('errors.suggestions')}</p>
            <ul className="list-disc list-inside space-y-1" role="list">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm">
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {onRetry && (
          <div className="mt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="bg-white hover:bg-red-50 text-red-900 border-red-300 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              aria-label={t('errors.retryAction')}
            >
              {t('errors.tryAgain')}
            </Button>
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
}
