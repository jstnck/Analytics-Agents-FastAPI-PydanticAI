'use client';

import { useState } from 'react';
import type { MessageMetadata } from '@/lib/types';

interface MetadataDisplayProps {
  metadata: MessageMetadata;
}

export default function MetadataDisplay({ metadata }: MetadataDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Check if there's anything to display
  const hasSqlQuery = metadata.sql_query;
  const hasDataSummary = metadata.data_summary && Object.keys(metadata.data_summary).length > 0;

  if (!hasSqlQuery && !hasDataSummary) {
    return null;
  }

  return (
    <div className="mt-3 border-t border-gray-200 pt-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
      >
        {isExpanded ? '▼' : '▶'} {hasSqlQuery ? 'SQL Query' : 'Details'}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-3">
          {/* SQL Query */}
          {hasSqlQuery && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-1">SQL Query:</div>
              <div className="bg-gray-900 text-gray-100 p-3 rounded text-xs font-mono overflow-x-auto">
                <pre className="whitespace-pre-wrap break-words">{metadata.sql_query}</pre>
              </div>
            </div>
          )}

          {/* Data Summary */}
          {hasDataSummary && (
            <div>
              <div className="text-xs font-semibold text-gray-700 mb-1">Data Summary:</div>
              <div className="bg-gray-50 p-3 rounded text-xs">
                <pre className="whitespace-pre-wrap break-words">
                  {JSON.stringify(metadata.data_summary, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
