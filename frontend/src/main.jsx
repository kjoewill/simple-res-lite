import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import ReservationPage from './ReservationPage.jsx';
import AdminPage from './AdminPage.jsx';

const router = createBrowserRouter([
  {
    path: '/',
    element: <ReservationPage />,
  },
  {
    path: '/admin',
    element: <AdminPage />,
  },
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
