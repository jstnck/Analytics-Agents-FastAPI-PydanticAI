'use client';

import { useEffect, useRef } from 'react';
import type { ChartSpec } from '@/lib/types';

interface ChartRendererProps {
  chartSpec: ChartSpec;
  chartType?: string;
}

export default function ChartRenderer({ chartSpec, chartType }: ChartRendererProps) {
  const plotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Dynamically import Plotly to avoid SSR issues
    const loadPlotly = async () => {
      if (!plotRef.current) return;

      try {
        const Plotly = (await import('plotly.js-dist-min')).default;

        // Clear any existing plot
        Plotly.purge(plotRef.current);

        // Create new plot - cast data to any to avoid strict Plotly type checking
        // The backend generates valid Plotly specs, but TS can't verify all chart type combinations
        await Plotly.newPlot(
          plotRef.current,
          chartSpec.data as any,
          chartSpec.layout as any,
          {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'],
          }
        );
      } catch (error) {
        console.error('Error rendering chart:', error);
      }
    };

    loadPlotly();

    // Cleanup on unmount
    return () => {
      if (plotRef.current) {
        try {
          import('plotly.js-dist-min').then((Plotly) => {
            if (plotRef.current) {
              Plotly.default.purge(plotRef.current);
            }
          });
        } catch (error) {
          console.error('Error cleaning up chart:', error);
        }
      }
    };
  }, [chartSpec]);

  return (
    <div className="w-full h-full">
      <div ref={plotRef} className="w-full h-full min-h-[400px]" />
      {chartType && (
        <div className="mt-2 text-xs text-gray-500 text-center">
          Chart type: <span className="font-medium">{chartType}</span>
        </div>
      )}
    </div>
  );
}
