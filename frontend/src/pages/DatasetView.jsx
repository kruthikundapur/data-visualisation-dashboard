import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import DataTable from '../components/DataTable';
import Charts from '../components/Charts';

const DatasetView = () => {
  const { id } = useParams();
  const [sharedFilters, setSharedFilters] = useState({});

  const handleFiltersChange = (filters) => {
    setSharedFilters(filters);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dataset View
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Explore your data with interactive tables and charts. Filters applied to the table will automatically update the charts.
        </p>
      </div>
      <DataTable onFiltersChange={handleFiltersChange} />
      <Charts filters={sharedFilters} />
    </div>
  );
};

export default DatasetView;

