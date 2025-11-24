import { useEffect, useState } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { AppSidebar } from './AppSidebar';
import { Button } from '../ui/button';

export function PrivateLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const performAuthCheck = async () => {
      await checkAuth();
      setAuthChecked(true);
    };
    performAuthCheck();
  }, [checkAuth]);

  // Show loading state while checking authentication
  if (!authChecked || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to sign in if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-shrink-0 lg:w-64 xl:w-72">
        <AppSidebar />
      </aside>

      {/* Sidebar - Mobile */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:hidden
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="relative h-full">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 z-10"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
          <AppSidebar onClose={() => setSidebarOpen(false)} />
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-semibold text-gray-900">
            re:Invent Planner
          </h1>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="h-full w-full max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
