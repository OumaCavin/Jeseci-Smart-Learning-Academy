import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { useAnalytics } from '../../contexts/AnalyticsContext';

// Generate polygon points for radar chart
function generatePolygonPoints(
  centerX: number,
  centerY: number,
  radius: number,
  levels: number,
  value: number,
  maxValue: number,
  index: number,
  total: number
): string {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2;
  const x = centerX + radius * (value / maxValue) * Math.cos(angle);
  const y = centerY + radius * (value / maxValue) * Math.sin(angle);
  return `${x},${y}`;
}

interface SkillRadarChartProps {
  skillsData: SkillData[];
  size?: number;
  maxLevel?: number;
  showLabels?: boolean;
  animated?: boolean;
  onSkillClick?: (skill: { id: string; name: string; level: number }) => void;
  className?: string;
}

export function SkillRadarChart({
  skillsData,
  size = 300,
  maxLevel = 100,
  showLabels = true,
  animated = true,
  onSkillClick,
  className = ''
}: SkillRadarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredSkill, setHoveredSkill] = useState<string | null>(null);
  const [animationProgress, setAnimationProgress] = useState(0);

  // Animation effect
  useEffect(() => {
    if (!animated) {
      setAnimationProgress(1);
      return;
    }

    const duration = 1000;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimationProgress(eased);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [skillsData, animated]);

  // Flatten all skills
  const allSkills = useMemo(() => {
    return skillsData.flatMap(category => 
      category.skills.map(skill => ({
        ...skill,
        category: category.category
      }))
    );
  }, [skillsData]);

  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size * 0.35;
  const levels = 5;

  // Generate grid levels
  const gridLevels = useMemo(() => {
    return Array.from({ length: levels }, (_, i) => ({
      radius: (radius * (i + 1)) / levels,
      label: Math.round(maxLevel * (i + 1) / levels)
    }));
  }, [radius, levels, maxLevel]);

  // Generate axis lines and labels
  const axes = useMemo(() => {
    return allSkills.map((skill, index) => {
      const angle = (Math.PI * 2 * index) / allSkills.length - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      return {
        skill,
        endX: x,
        endY: y,
        labelX: centerX + (radius + 20) * Math.cos(angle),
        labelY: centerY + (radius + 20) * Math.sin(angle)
      };
    });
  }, [allSkills, centerX, centerY, radius]);

  // Generate polygon points
  const polygonPoints = useMemo(() => {
    return allSkills.map((skill, index) => {
      const angle = (Math.PI * 2 * index) / allSkills.length - Math.PI / 2;
      const scaledValue = (skill.level / maxLevel) * radius * animationProgress;
      const x = centerX + scaledValue * Math.cos(angle);
      const y = centerY + scaledValue * Math.sin(angle);
      return { x, y, skill };
    });
  }, [allSkills, centerX, centerY, radius, maxLevel, animationProgress]);

  // Category colors
  const categoryColors: Record<string, string> = {
    'Algorithms': '#3B82F6',
    'Frontend': '#10B981',
    'Backend': '#8B5CF6',
    'Database': '#F59E0B',
    'DevOps': '#EF4444',
    'Security': '#EC4899',
    'Testing': '#06B6D4',
    'Other': '#6B7280'
  };

  // Handle skill hover
  const handleSkillHover = useCallback((skillId: string | null) => {
    setHoveredSkill(skillId);
  }, []);

  // Calculate average level
  const avgLevel = useMemo(() => {
    if (allSkills.length === 0) return 0;
    return allSkills.reduce((sum, s) => sum + s.level, 0) / allSkills.length;
  }, [allSkills]);

  // Group by category for legend
  const categories = useMemo(() => {
    const cats = new Map<string, { color: string; count: number }>();
    skillsData.forEach(category => {
      const color = categoryColors[category.category] || categoryColors['Other'];
      cats.set(category.category, { color, count: category.skills.length });
    });
    return Array.from(cats.entries());
  }, [skillsData]);

  if (allSkills.length === 0) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-xl ${className}`}
           style={{ width: size, height: size }}>
        <p className="text-gray-500 text-sm">No skill data available</p>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <svg
        ref={svgRef}
        width={size}
        height={size}
        className="overflow-visible"
      >
        {/* Grid circles */}
        {gridLevels.map((level, i) => (
          <circle
            key={i}
            cx={centerX}
            cy={centerY}
            r={level.radius}
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="1"
            className="dark:stroke-gray-700"
          />
        ))}

        {/* Axis lines */}
        {axes.map((axis, i) => (
          <line
            key={i}
            x1={centerX}
            y1={centerY}
            x2={axis.endX}
            y2={axis.endY}
            stroke="#E5E7EB"
            strokeWidth="1"
            className="dark:stroke-gray-700"
          />
        ))}

        {/* Data polygon */}
        <polygon
          points={polygonPoints.map(p => `${p.x},${p.y}`).join(' ')}
          fill="rgba(59, 130, 246, 0.2)"
          stroke="#3B82F6"
          strokeWidth="2"
          className="transition-all duration-500"
        />

        {/* Data points */}
        {polygonPoints.map((point, i) => (
          <g 
            key={i}
            onMouseEnter={() => handleSkillHover(point.skill.id)}
            onMouseLeave={() => handleSkillHover(null)}
            onClick={() => onSkillClick?.(point.skill)}
          >
            <circle
              cx={point.x}
              cy={point.y}
              r={hoveredSkill === point.skill.id ? 8 : 5}
              fill={categoryColors[point.skill.category] || categoryColors['Other']}
              stroke="white"
              strokeWidth="2"
              className="cursor-pointer transition-all"
            />
            
            {/* Hover connection line */}
            {hoveredSkill === point.skill.id && (
              <line
                x1={centerX}
                y1={centerY}
                x2={point.x}
                y2={point.y}
                stroke={categoryColors[point.skill.category] || categoryColors['Other']}
                strokeWidth="1"
                strokeDasharray="4 2"
                opacity="0.5"
              />
            )}
          </g>
        ))}

        {/* Labels */}
        {showLabels && axes.map((axis, i) => {
          const isHovered = hoveredSkill === axis.skill.id;
          
          return (
            <g key={i}>
              <text
                x={axis.labelX}
                y={axis.labelY}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={isHovered ? '#1F2937' : '#6B7280'}
                fontSize="11"
                fontWeight={isHovered ? '600' : '400'}
                className="dark:fill-gray-400 dark:hover:fill-white transition-colors cursor-pointer"
                onMouseEnter={() => handleSkillHover(axis.skill.id)}
                onMouseLeave={() => handleSkillHover(null)}
                onClick={() => onSkillClick?.(axis.skill)}
              >
                {axis.skill.name.length > 12 
                  ? axis.skill.name.slice(0, 12) + '...' 
                  : axis.skill.name}
              </text>
              
              {/* Level badge */}
              <text
                x={axis.labelX}
                y={axis.labelY + 14}
                textAnchor="middle"
                fill="#9CA3AF"
                fontSize="9"
              >
                {axis.skill.level}/{maxLevel}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-3 mt-4 justify-center">
          {categories.map(([category, { color, count }]) => (
            <div key={category} className="flex items-center gap-1.5">
              <div 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {category} ({count})
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      <div className="absolute top-0 right-0 bg-white dark:bg-gray-800 rounded-lg px-3 py-1 
                   shadow-sm border border-gray-200 dark:border-gray-700">
        <span className="text-xs text-gray-500">Avg: </span>
        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {Math.round(avgLevel)}
        </span>
      </div>
    </div>
  );
}

