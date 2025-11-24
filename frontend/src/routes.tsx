import { createBrowserRouter, Navigate } from 'react-router-dom';
import { SignIn } from './pages/auth/SignIn';
import { SignUp } from './pages/auth/SignUp';
import { ConfirmSignUp } from './pages/auth/ConfirmSignUp';
import { PublicLayout } from './components/layout/PublicLayout';
import { PrivateLayout } from './components/layout/PrivateLayout';
import { Dashboard } from './pages/Dashboard';
import { Chat } from './pages/Chat';
import { Settings } from './pages/Settings';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/app/dashboard" replace />,
  },
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      {
        path: 'signin',
        element: <SignIn />,
      },
      {
        path: 'signup',
        element: <SignUp />,
      },
      {
        path: 'confirm-signup',
        element: <ConfirmSignUp />,
      },
    ],
  },
  {
    path: '/app',
    element: <PrivateLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'chat',
        element: <Chat />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/signin" replace />,
  },
]);
