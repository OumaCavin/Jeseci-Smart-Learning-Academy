import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { useAnalytics, ActivityDataPoint } from '../../hooks/useAnalytics';

// Helper function to generate color based on intensity
function getColorForIntensity(intensity: number, maxIntensity: number): string {
  const ratio = intensity / maxIntensity;
  
  if (ratio === 0) return 'bg-gray-100 dark:bg-gray-800';
  if (ratio < 0.2) return 'bg-green-200 dark:bg-green-900/40';
  if (ratio < 0.4) return 'bg-green-300 dark:bg-green-800/50';
  if (ratio < 0.6) return 'bg-green-400 dark:bg-green-700/60';
  if (ratio < 0.8) return 'bg-green-500 dark:bg-green-600/70';
  return 'bg-green-600 dark:bg-green-500/80';
}

// Helper function to format date for tooltip
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric',
    weekday: undefined
  });
}

interface ActivityHeatmapProps {
  data: ActivityDataPoint[];
  year?: number;
  showLabels?: boolean;
  cellSize?: number;
  gap?: number;
  onCellClick?: (dataPoint: ActivityDataPoint) => void;
  className?: string;
}

export function ActivityHeatmap({
  data,
  year = new Date().getFullYear(),
  showLabels = true,
  cellSize = 12,
  gap = 3,
  onCellClick,
  className = ''
}: ActivityHeatmapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; data: ActivityDataPoint } | null>(null);

  // Calculate max intensity for color scaling
  const maxIntensity = useMemo(() => {
    if (data.length === 0) return 1;
    return Math.max(...data.map(d => d.value), 1);
  }, [data]);

  // Group data by week
  const weeks = useMemo(() => {
    const weeksMap = new Map<string, Map<number, ActivityDataPoint>>();
    const startDate = new Date(year, 0, 1);
    const endDate = new Date(year, 11, 31);

    // Initialize all weeks
    const current = new Date(startDate);
    while (current <= endDate) {
      const weekKey = getWeekKey(current);
      if (!weeksMap.has(weekKey)) {
        weeksMap.set(weekKey, new Map());
      }
      current.setDate(current.getDate() + 1);
    }

    // Fill in data
    data.forEach(point => {
      const date = new Date(point.date);
      const weekKey = getWeekKey(date);
      const dayOfWeek = date.getDay();
      
      const week = weeksMap.get(weekKey);
      if (week) {
        week.set(dayOfWeek, point);
      }
    });

    return Array.from(weeksMap.entries()).map(([weekKey, days]) => {
      const [, weekNum] = weekKey.split('-').map(Number);
      return {
        week: weekNum,
        days: Array.from(days.entries()).sort((a, b) => a[0] - b[0])
      };
    }).sort((a, b) => a.week - b.week);
  }, [data, year]);

  // Get week key
  function getWeekKey(date: Date): string {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
    return `${d.getUTCFullYear()}-${weekNo}`;
  }

  // Handle cell hover
  const handleCellHover = useCallback((dataPoint: ActivityDataPoint | undefined, event: React.MouseEvent) => {
    if (dataPoint) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        setTooltip({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top - 40,
          data: dataPoint
        });
      }
    } else {
      setTooltip(null);
    }
  }, []);

  // Day labels
  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className={`relative ${className}`}>
      <div className="flex">
        {/* Day labels */}
        {showLabels && (
          <div className="flex flex-col mr-2" style={{ paddingTop: cellSize }}>
            {dayLabels.map((label, i) => (
              <div 
                key={label}
                className="text-xs text-gray-500"
                style={{ 
                  height: cellSize + gap,
                  lineHeight: `${cellSize}px`
                }}
              >
                {i % 2 === 0 || window.innerWidth > 768 ? label : ''}
              </div>
            ))}
          </div>
        )}

        {/* Heatmap grid */}
        <div 
          ref={containerRef}
          className="flex gap-1 overflow-x-auto pb-2"
          style={{ scrollbarWidth: 'thin' }}
        >
          {weeks.map((week, weekIndex) => (
            <div key={week.week} className="flex flex-col gap-1">
              {/* Week number label */}
              {showLabels && weekIndex % 4 === 0 && (
                <div 
                  className="text-xs text-gray-400 text-center"
                  style={{ height: cellSize }}
                >
                  {week.week}
                </div>
              )}
              {showLabels && weekIndex % 4 !== 0 && (
                <div style={{ height: cellSize }} />
              )}

              {/* Day cells */}
              {Array.from({ length: 7 }).map((_, dayIndex) => {
                const dataPoint = week.days.find(([day]) => day === dayIndex)?.[1];
                const isEmpty = !dataPoint;

                return (
                  <div
                    key={dayIndex}
                    onMouseEnter={(e) => handleCellHover(dataPoint, e)}
                    onMouseLeave={() => setTooltip(null)}
                    onClick={() => dataPoint && onCellClick?.(dataPoint)}
                    className={`rounded-sm transition-all cursor-pointer ${
                      isEmpty 
                        ? 'bg-gray-100 dark:bg-gray-800' 
                        : getColorForIntensity(dataPoint.value, maxIntensity)
                    } ${!isEmpty && onCellClick ? 'hover:ring-2 hover:ring-blue-500' : ''}`}
                    style={{
                      width: cellSize,
                      height: cellSize,
                      marginBottom: gap
                    }}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div 
          className="absolute z-10 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg 
                   px-3 py-2 shadow-lg pointer-events-none"
          style={{
            left: Math.min(tooltip.x, (containerRef.current?.offsetWidth || 200) - 100),
            top: tooltip.y
          }}
        >
          <div className="font-medium">{tooltip.data.value} activities</div>
          <div className="text-gray-400">{formatDate(tooltip.data.date)}</div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-2 mt-4 text-xs text-gray-500">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-sm bg-gray-100 dark:bg-gray-800" />
          <div className="w-3 h-3 rounded-sm bg-green-200 dark:bg-green-900/40" />
          <div className="w-3 h-3 rounded-sm bg-green-400 dark:bg-green-800/50" />
          <div className="w-3 h-3 rounded-sm bg-green-600 dark:bg-green-500/70" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
}

