import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, MessageSquare, Settings, LogOut, PlusCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { useAuthStore } from '../../store/authStore';
import { useChatStore } from '../../store/chatStore';
import { ChatHistoryList } from '../chat/ChatHistoryList';
import { useTranslation } from 'react-i18next';

interface AppSidebarProps {
  onClose?: () => void;
}

export function AppSidebar({ onClose }: AppSidebarProps) {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const signOut = useAuthStore((state) => state.signOut);
  const startNewSession = useChatStore((state) => state.startNewSession);

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/signin');
    } catch (error) {
      console.error('Sign out failed:', error);
    }
  };

  const handleNewChat = () => {
    // Clear conversation history and generate new session ID
    startNewSession();
    // Navigate to chat page
    navigate('/app/chat');
    onClose?.();
  };

  const navItems = [
    { path: '/app/dashboard', icon: Home, label: t('sidebar.dashboard') },
    { path: '/app/chat', icon: MessageSquare, label: t('sidebar.chat') },
    { path: '/app/settings', icon: Settings, label: t('sidebar.settings') },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="h-full flex flex-col bg-card border-r border-border">
      {/* Header with Dati Logo */}
      <div className="p-4 sm:p-6 border-b border-border">
        <div className="flex items-center gap-3 mb-2">
          <img 
            src="/dati-logo.png" 
            alt="Dati company logo" 
            className="h-8 w-8 sm:h-10 sm:w-10 object-contain bg-white p-1.5 rounded"
          />
          <div className="flex-1 min-w-0">
            <h2 className="text-lg sm:text-xl font-bold text-foreground truncate">
              {t('chat.title')}
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground truncate">{t('sidebar.aiAssistant')}</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3 sm:p-4 border-b border-border">
        <Button
          onClick={handleNewChat}
          className="w-full justify-start gap-2 bg-primary hover:bg-primary/90 text-primary-foreground focus:ring-2 focus:ring-ring focus:ring-offset-2 transition-colors"
          size="sm"
          aria-label={t('sidebar.aria.startNewChat')}
        >
          <PlusCircle className="h-4 w-4" aria-hidden="true" />
          <span className="text-sm sm:text-base">{t('sidebar.newChat')}</span>
        </Button>
      </div>

      {/* Chat History Section */}
      <div className="flex-1 flex flex-col overflow-hidden border-b border-border">
        <div className="p-3 sm:p-4 border-b border-border">
          <h3 className="text-sm font-semibold text-foreground">{t('sidebar.chatHistory')}</h3>
        </div>
        <div className="flex-1 overflow-hidden">
          <ChatHistoryList />
        </div>
      </div>

      {/* Navigation */}
      <nav 
        className="p-3 sm:p-4 space-y-1 sm:space-y-2"
        aria-label={t('sidebar.aria.primaryNavigation')}
      >
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              aria-current={active ? 'page' : undefined}
              className={`
                flex items-center gap-3 px-3 sm:px-4 py-2 sm:py-3 rounded-lg transition-all
                focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                ${
                  active
                    ? 'bg-primary/20 text-foreground font-medium shadow-sm'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                }
              `}
            >
              <Icon className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" aria-hidden="true" />
              <span className="text-sm sm:text-base truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Sign Out */}
      <div className="p-3 sm:p-4 border-t border-border">
        <Button
          onClick={handleSignOut}
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/10 focus:ring-2 focus:ring-ring focus:ring-offset-2 transition-colors"
          aria-label={t('sidebar.aria.signOut')}
        >
          <LogOut className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" aria-hidden="true" />
          <span className="text-sm sm:text-base truncate">{t('sidebar.signOut')}</span>
        </Button>
      </div>
    </div>
  );
}
