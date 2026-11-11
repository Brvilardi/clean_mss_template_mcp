import { lazy } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { PublicLayout } from './components/layout/PublicLayout';
import { PrivateLayout } from './components/layout/PrivateLayout';

// Lazy load pages for code splitting
const SignIn = lazy(() => import('./pages/auth/SignIn').then(module => ({ default: module.SignIn })));
const SignUp = lazy(() => import('./pages/auth/SignUp').then(module => ({ default: module.SignUp })));
const ConfirmSignUp = lazy(() => import('./pages/auth/ConfirmSignUp').then(module => ({ default: module.ConfirmSignUp })));
const ForgotPassword = lazy(() => import('./pages/auth/ForgotPassword').then(module => ({ default: module.ForgotPassword })));
const ResetPassword = lazy(() => import('./pages/auth/ResetPassword').then(module => ({ default: module.ResetPassword })));
const Dashboard = lazy(() => import('./pages/Dashboard').then(module => ({ default: module.Dashboard })));
const Chat = lazy(() => import('./pages/Chat').then(module => ({ default: module.Chat })));
const Settings = lazy(() => import('./pages/Settings').then(module => ({ default: module.Settings })));

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
      {
        path: 'forgot-password',
        element: <ForgotPassword />,
      },
      {
        path: 'reset-password',
        element: <ResetPassword />,
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
