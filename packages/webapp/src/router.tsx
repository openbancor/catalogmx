import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ValidatorsPage from './pages/ValidatorsPage';
import CalculatorsPage from './pages/CalculatorsPage';
import CatalogsPage from './pages/CatalogsPage';
import ReferencePage from './pages/ReferencePage';
import DatasetPage from './pages/DatasetPage';
import { datasetConfigs, type DatasetId } from './data/datasets';

// Generate routes for all datasets
const datasetRoutes = datasetConfigs.map((dataset) => ({
  path: `/catalogs/${dataset.id}`,
  element: <DatasetPage datasetId={dataset.id as DatasetId} />,
}));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'validators',
        element: <ValidatorsPage />,
      },
      {
        path: 'validators/:validatorId',
        element: <ValidatorsPage />,
      },
      {
        path: 'calculators',
        element: <CalculatorsPage />,
      },
      {
        path: 'calculators/:calculatorId',
        element: <CalculatorsPage />,
      },
      {
        path: 'catalogs',
        element: <CatalogsPage />,
      },
      ...datasetRoutes,
      {
        path: 'reference',
        element: <ReferencePage />,
      },
      {
        path: '*',
        element: <Navigate to="/" replace />,
      },
    ],
  },
], {
  basename: import.meta.env.BASE_URL,
});
