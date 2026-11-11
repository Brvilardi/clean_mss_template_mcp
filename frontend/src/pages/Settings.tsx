import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useChatStore } from '../store/chatStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { User, Building2, Globe, Mail, Trash2, LogOut, MessageSquare, AlertCircle, Languages } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { useTranslation } from 'react-i18next';

export function Settings() {
  const { user, signOut } = useAuthStore();
  const { clearMessages, messages } = useChatStore();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [isClearingHistory, setIsClearingHistory] = useState(false);
  const [showClearSuccess, setShowClearSuccess] = useState(false);

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
      navigate('/signin');
    } catch (error) {
      console.error('Sign out failed:', error);
      setIsSigningOut(false);
    }
  };

  const handleClearHistory = () => {
    setIsClearingHistory(true);
    try {
      clearMessages();
      setShowClearSuccess(true);
      setTimeout(() => {
        setShowClearSuccess(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to clear history:', error);
    } finally {
      setIsClearingHistory(false);
    }
  };

  return (
    <div className="h-full overflow-auto bg-background">
      <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center gap-3 sm:gap-4 mb-2">
            <img 
              src="/dati-logo.png" 
              alt="Dati Logo" 
              className="h-8 w-8 sm:h-10 sm:w-10 object-contain bg-white p-1.5 rounded"
            />
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-foreground">{t('settings.title')}</h1>
          </div>
          <p className="text-muted-foreground text-base sm:text-lg ml-0 sm:ml-14">
            {t('settings.subtitle')}
          </p>
        </div>

        {/* Success Alert */}
        {showClearSuccess && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <AlertCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t('settings.historyCleared')}
            </AlertDescription>
          </Alert>
        )}

        {/* User Information */}
        <Card className="mb-6 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <User className="h-5 w-5 sm:h-6 sm:w-6 text-dati-accent-1" />
              Account Information
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              Your profile details from AWS Cognito
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Email */}
              <div className="flex items-start gap-3 pb-4 border-b">
                <Mail className="h-4 w-4 sm:h-5 sm:w-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-500">Email</p>
                  <p className="text-sm sm:text-base text-gray-900 break-words">{user?.email || 'Not available'}</p>
                </div>
              </div>

              {/* Company Name */}
              <div className="flex items-start gap-3 pb-4 border-b">
                <Building2 className="h-4 w-4 sm:h-5 sm:w-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-500">Company Name</p>
                  <p className="text-sm sm:text-base text-gray-900 break-words">{user?.companyName || 'Not available'}</p>
                </div>
              </div>

              {/* Company Website */}
              <div className="flex items-start gap-3">
                <Globe className="h-4 w-4 sm:h-5 sm:w-5 text-gray-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm font-medium text-gray-500">Company Website</p>
                  {user?.companyWebsite ? (
                    <a 
                      href={user.companyWebsite}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm sm:text-base text-dati-accent-1 hover:underline break-all focus:outline-none focus:ring-2 focus:ring-dati-primary focus:ring-offset-2 rounded"
                    >
                      {user.companyWebsite}
                    </a>
                  ) : (
                    <p className="text-sm sm:text-base text-gray-900">Not available</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Language Preferences */}
        <Card className="mb-6 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <Languages className="h-5 w-5 sm:h-6 sm:w-6 text-dati-accent-1" />
              {t('settings.language')}
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              {t('settings.selectLanguage')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex flex-col gap-3">
                <label htmlFor="language-select" className="text-sm font-medium text-gray-700">
                  {t('settings.preferences')}
                </label>
                <LanguageSwitcher />
                <p className="text-xs sm:text-sm text-gray-500">
                  Your language preference will be saved and applied across the application
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Conversation History */}
        <Card className="mb-6 shadow-md hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <MessageSquare className="h-5 w-5 sm:h-6 sm:w-6 text-dati-accent-1" />
              Conversation History
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              Manage your chat history and conversations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-gray-50 rounded-lg">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900">Current conversation</p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    {messages.length === 0 
                      ? 'No messages yet' 
                      : `${messages.length} message${messages.length === 1 ? '' : 's'}`}
                  </p>
                </div>
                <Badge variant={messages.length > 0 ? "default" : "secondary"} className="self-start sm:self-auto">
                  {messages.length > 0 ? 'Active' : 'Empty'}
                </Badge>
              </div>

              <div className="pt-2">
                <Button
                  variant="destructive"
                  onClick={handleClearHistory}
                  disabled={isClearingHistory || messages.length === 0}
                  className="w-full sm:w-auto focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  {isClearingHistory ? 'Clearing...' : 'Clear Conversation History'}
                </Button>
                <p className="text-xs sm:text-sm text-gray-500 mt-2">
                  This will permanently delete all messages in your current conversation
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <LogOut className="h-5 w-5 sm:h-6 sm:w-6 text-dati-accent-1" />
              Account Actions
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              Sign out of your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-xs sm:text-sm text-gray-600">
                Signing out will end your current session. You'll need to sign in again to access the planner.
              </p>
              <Button
                variant="outline"
                onClick={handleSignOut}
                disabled={isSigningOut}
                className="w-full sm:w-auto border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                <LogOut className="h-4 w-4 mr-2" />
                {isSigningOut ? 'Signing out...' : 'Sign Out'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
