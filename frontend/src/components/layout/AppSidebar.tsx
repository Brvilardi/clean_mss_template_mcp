import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, MessageSquare, Settings, LogOut, PlusCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { useAuthStore } from '../../store/authStore';

interface AppSidebarProps {
  onClose?: () => void;
}

export function AppSidebar({ onClose }: AppSidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const signOut = useAuthStore((state) => state.signOut);

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/signin');
    } catch (error) {
      console.error('Sign out failed:', error);
    }
  };

  const handleNewChat = () => {
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
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">re:Invent Planner</h2>
        <p className="text-sm text-gray-600 mt-1">AI Assistant</p>
      </div>

      {/* New Chat Button */}
      <div className="p-4 border-b border-gray-200">
        <Button
          onClick={handleNewChat}
          className="w-full justify-start gap-2"
          variant="outline"
        >
          <PlusCircle className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${
                  active
                    ? 'bg-orange-50 text-orange-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Sign Out */}
      <div className="p-4 border-t border-gray-200">
        <Button
          onClick={handleSignOut}
          variant="ghost"
          className="w-full justify-start gap-3 text-gray-700 hover:text-red-600 hover:bg-red-50"
        >
          <LogOut className="h-5 w-5" />
          <span>Sign Out</span>
        </Button>
      </div>
    </div>
  );
}
