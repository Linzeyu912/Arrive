import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Layout from './Layout';
import RecordPage from '../features/record/RecordPage';
import MaterialsPage from '../features/materials/MaterialsPage';
import MaterialDetailPage from '../features/materials/MaterialDetailPage';
import SourcesPage from '../features/sources/SourcesPage';
import SourceDetailPage from '../features/sources/SourceDetailPage';
import PropositionsPage from '../features/propositions/PropositionsPage';
import ResponsePage from '../features/responses/ResponsePage';
import NotFoundPage from './NotFoundPage';

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <RecordPage /> },
      { path: '/materials', element: <MaterialsPage /> },
      { path: '/materials/:materialId', element: <MaterialDetailPage /> },
      { path: '/sources', element: <SourcesPage /> },
      { path: '/sources/:sourceId', element: <SourceDetailPage /> },
      { path: '/propositions', element: <PropositionsPage /> },
      { path: '/responses', element: <ResponsePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
