'use client';

import { useEffect, useRef } from 'react';
import type { ChartSpec } from '@/lib/types';

interface ChartRendererProps {
  chartSpec: ChartSpec;
  chartType?: string;
}

// HOOPTICS Design System - Plotly Template
const hoopticsTemplate = {
  layout: {
    font: {
      family: "'Space Grotesk', 'Inter', sans-serif",
      size: 14,
      color: 'rgb(66, 51, 36)', // --foreground
    },
    colorway: [
      'rgb(255, 122, 69)',   // primary (coral orange)
      'rgb(35, 197, 150)',   // assist-teal
      'rgb(255, 219, 102)',  // victory-gold
      'rgb(177, 152, 217)',  // secondary (adjusted for visibility)
      'rgb(242, 108, 54)',   // court-line
      'rgb(102, 186, 168)',  // assist-teal light variant
    ],
    paper_bgcolor: 'rgb(255, 255, 255)', // card background
    plot_bgcolor: 'rgb(255, 255, 255)',  // card background

    title: {
      font: {
        family: "'Space Grotesk', sans-serif",
        size: 20,
        color: 'rgb(66, 51, 36)', // --foreground
      },
      x: 0.05,
      xanchor: 'left',
    },

    xaxis: {
      gridcolor: 'rgb(223, 213, 201)', // --border
      linecolor: 'rgb(223, 213, 201)',
      tickfont: {
        family: "'Inter', sans-serif",
        size: 12,
        color: 'rgb(89, 78, 64)', // --muted-foreground
      },
      title: {
        font: {
          family: "'Space Grotesk', sans-serif",
          size: 14,
          color: 'rgb(66, 51, 36)',
        },
      },
    },

    yaxis: {
      gridcolor: 'rgb(223, 213, 201)',
      linecolor: 'rgb(223, 213, 201)',
      tickfont: {
        family: "'Inter', sans-serif",
        size: 12,
        color: 'rgb(89, 78, 64)',
      },
      title: {
        font: {
          family: "'Space Grotesk', sans-serif",
          size: 14,
          color: 'rgb(66, 51, 36)',
        },
      },
    },

    legend: {
      font: {
        family: "'Inter', sans-serif",
        size: 12,
        color: 'rgb(66, 51, 36)',
      },
      bgcolor: 'rgba(255, 255, 255, 0.8)',
      bordercolor: 'rgb(223, 213, 201)',
      borderwidth: 1,
    },

    hoverlabel: {
      font: {
        family: "'Inter', sans-serif",
        size: 13,
      },
      bgcolor: 'rgb(66, 51, 36)',
    },
  },
};

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

        // Merge HOOPTICS template with incoming chart layout
        const mergedLayout = {
          ...hoopticsTemplate.layout,
          ...chartSpec.layout,
          // Ensure fonts are preserved even if layout has partial overrides
          font: {
            ...hoopticsTemplate.layout.font,
            ...(chartSpec.layout?.font || {}),
          },
          title: {
            ...hoopticsTemplate.layout.title,
            ...(chartSpec.layout?.title || {}),
          },
        };

        // Create new plot - cast data to any to avoid strict Plotly type checking
        // The backend generates valid Plotly specs, but TS can't verify all chart type combinations
        await Plotly.newPlot(
          plotRef.current,
          chartSpec.data as any,
          mergedLayout as any,
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
        <div className="mt-2 text-xs text-muted-foreground text-center">
          Chart type: <span className="font-medium text-foreground">{chartType}</span>
        </div>
      )}
    </div>
  );
}
