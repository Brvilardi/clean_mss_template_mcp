import { Suspense, useEffect, useState, useRef } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Menu, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { AppSidebar } from './AppSidebar';
import { Button } from '../ui/button';
import { Skeleton } from '../ui/skeleton';

// Loading fallback for page transitions
function PageLoadingFallback() {
  const { t } = useTranslation();

  return (
    <div className="h-full w-full p-6 space-y-4" role="status" aria-label={t('loading.pageContent')}>
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-64 w-full" />
      <span className="sr-only">{t('loading.default')}</span>
    </div>
  );
}

export function PrivateLayout() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const mainContentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const performAuthCheck = async () => {
      await checkAuth();
      setAuthChecked(true);
    };
    performAuthCheck();
  }, [checkAuth]);

  // Handle escape key to close sidebar
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false);
      }
    };

    if (sidebarOpen) {
      document.addEventListener('keydown', handleEscape);
      // Trap focus in sidebar when open
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [sidebarOpen]);

  const { t } = useTranslation();

  // Show loading state while checking authentication
  if (!authChecked || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" role="status" aria-live="polite">
        <div className="text-center">
          <div 
            className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"
            aria-hidden="true"
          ></div>
          <p className="mt-4 text-gray-600">{t('loading.default')}</p>
          <span className="sr-only">{t('loading.checkingAuth')}</span>
        </div>
      </div>
    );
  }

  // Redirect to sign in if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return (
    <div className="h-screen flex overflow-hidden bg-dati-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          role="presentation"
          aria-hidden="true"
        />
      )}

      {/* Skip to main content link for keyboard navigation */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-dati-primary focus:text-white focus:rounded-md"
      >
        Skip to main content
      </a>

      {/* Sidebar - Desktop */}
      <aside 
        className="hidden lg:flex lg:flex-shrink-0 lg:w-64 xl:w-72"
        aria-label="Main navigation"
      >
        <AppSidebar />
      </aside>

      {/* Sidebar - Mobile */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:hidden
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        aria-label="Main navigation"
        aria-hidden={!sidebarOpen}
      >
        <div className="relative h-full">
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 z-10 focus:ring-2 focus:ring-dati-primary focus:ring-offset-2"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation menu"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </Button>
          <AppSidebar onClose={() => setSidebarOpen(false)} />
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden bg-dati-background border-b border-gray-700 px-4 py-3 flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation menu"
            aria-expanded={sidebarOpen}
            aria-controls="mobile-sidebar"
            className="text-white hover:bg-gray-700 focus:ring-2 focus:ring-dati-primary focus:ring-offset-2"
          >
            <Menu className="h-5 w-5" aria-hidden="true" />
          </Button>
          <h1 className="text-lg font-semibold text-white">
            re:Invent Planner
          </h1>
        </header>

        {/* Page content */}
        <main 
          id="main-content"
          ref={mainContentRef}
          className="flex-1 overflow-auto"
          role="main"
          aria-label="Main content"
          tabIndex={-1}
        >
          <div className="h-full w-full max-w-7xl mx-auto">
            <Suspense fallback={<PageLoadingFallback />}>
              <Outlet />
            </Suspense>
          </div>
        </main>
      </div>
    </div>
  );
}
