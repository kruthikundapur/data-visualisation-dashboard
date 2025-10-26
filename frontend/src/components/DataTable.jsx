import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const DataTable = ({ onFiltersChange }) => {
  const { id } = useParams();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
    totalPages: 0
  });
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [id, pagination.page, searchTerm, sortConfig, filters]);

  useEffect(() => {
    if (onFiltersChange) {
      onFiltersChange(filters);
    }
  }, [filters, onFiltersChange]);

  const handleFilterChange = (column, value) => {
    const newFilters = {
      ...filters,
      [column]: value || null
    };
    // Remove null/empty filters
    Object.keys(newFilters).forEach(key => {
      if (!newFilters[key]) {
        delete newFilters[key];
      }
    });
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/data/filter', {
        dataset_id: parseInt(id),
        filters,
        search_term: searchTerm,
        page: pagination.page,
        page_size: pagination.pageSize,
        sort_by: sortConfig.key,
        sort_order: sortConfig.direction
      });
      
      setData(response.data.data);
      if (response.data.data.length > 0 && columns.length === 0) {
        setColumns(Object.keys(response.data.data[0]));
      }
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
        totalPages: response.data.total_pages
      }));
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const handleSearchChange = (value) => {
    setSearchTerm(value);
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const displayColumns = columns.length > 0 ? columns : (data.length > 0 ? Object.keys(data[0]) : []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="mb-4 flex flex-wrap gap-4 items-center">
        <input
          type="text"
          placeholder="Search across all columns..."
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white flex-1 min-w-[200px]"
        />
        
        {displayColumns.slice(0, 3).map(column => (
          <div key={column} className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
              {column}:
            </label>
            <input
              type="text"
              placeholder={`Filter ${column}...`}
              onChange={(e) => handleFilterChange(column, e.target.value)}
              className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
            />
          </div>
        ))}
      </div>

      {loading && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Loading...
        </div>
      )}

      {!loading && (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  {displayColumns.map(column => (
                    <th
                      key={column}
                      onClick={() => handleSort(column)}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                    >
                      {column}
                      {sortConfig.key === column && (
                        <span className="ml-1">
                          {sortConfig.direction === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {data.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    {displayColumns.map(column => (
                      <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                        {row[column] ?? <span className="text-gray-400">—</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No data found
            </div>
          )}

          {/* Pagination */}
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-700 dark:text-gray-300">
              Showing {((pagination.page - 1) * pagination.pageSize) + 1} to{' '}
              {Math.min(pagination.page * pagination.pageSize, pagination.total)} of{' '}
              {pagination.total} entries
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 dark:bg-gray-700 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page >= pagination.totalPages}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 dark:bg-gray-700 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-600"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DataTable;

