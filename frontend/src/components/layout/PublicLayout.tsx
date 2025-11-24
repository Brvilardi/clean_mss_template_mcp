import { Outlet } from 'react-router-dom';

export function PublicLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            re:Invent Planner
          </h1>
          <p className="text-gray-600">
            AI-powered conference planning assistant
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
