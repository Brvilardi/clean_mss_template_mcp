import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, MessageSquare, Settings, LogOut, PlusCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { useAuthStore } from '../../store/authStore';
import { useChatStore } from '../../store/chatStore';

interface AppSidebarProps {
  onClose?: () => void;
}

export function AppSidebar({ onClose }: AppSidebarProps) {
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
    { path: '/app/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/app/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/app/settings', icon: Settings, label: 'Settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="h-full flex flex-col bg-dati-background border-r border-gray-700">
      {/* Header with Dati Logo */}
      <div className="p-4 sm:p-6 border-b border-gray-700">
        <div className="flex items-center gap-3 mb-2">
          <img 
            src="/dati-logo.png" 
            alt="Dati company logo" 
            className="h-8 w-8 sm:h-10 sm:w-10 object-contain bg-white p-1.5 rounded"
          />
          <div className="flex-1 min-w-0">
            <h2 className="text-lg sm:text-xl font-bold text-white truncate">
              re:Invent Planner
            </h2>
            <p className="text-xs sm:text-sm text-gray-300 truncate">AI Assistant</p>
          </div>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-3 sm:p-4 border-b border-gray-700">
        <Button
          onClick={handleNewChat}
          className="w-full justify-start gap-2 bg-dati-primary hover:bg-dati-accent-4 text-white focus:ring-2 focus:ring-dati-primary focus:ring-offset-2 transition-colors"
          size="sm"
          aria-label="Start a new chat conversation"
        >
          <PlusCircle className="h-4 w-4" aria-hidden="true" />
          <span className="text-sm sm:text-base">New Chat</span>
        </Button>
      </div>

      {/* Navigation */}
      <nav 
        className="flex-1 p-3 sm:p-4 space-y-1 sm:space-y-2 overflow-y-auto"
        aria-label="Primary navigation"
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
                focus:outline-none focus:ring-2 focus:ring-dati-primary focus:ring-offset-2
                ${
                  active
                    ? 'bg-dati-primary/20 text-white font-medium shadow-sm'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
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
      <div className="p-3 sm:p-4 border-t border-gray-700">
        <Button
          onClick={handleSignOut}
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-3 text-gray-300 hover:text-red-400 hover:bg-red-900/20 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
          aria-label="Sign out of your account"
        >
          <LogOut className="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0" aria-hidden="true" />
          <span className="text-sm sm:text-base truncate">Sign Out</span>
        </Button>
      </div>
    </div>
  );
}
