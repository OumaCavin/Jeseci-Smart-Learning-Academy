import React, { useState, useCallback } from 'react';

// Icons
const PlayIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const StopIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
  </svg>
);

const SaveIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
  </svg>
);

const SettingsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const FullscreenIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
  </svg>
);

const HistoryIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

interface ExecutionSettings {
  timeout: number;
  memoryLimit: number;
  enableNetwork: boolean;
  enableDebug: boolean;
  saveOutput: boolean;
  stdinEnabled: boolean;
}

interface ExecutionControlsProps {
  isExecuting: boolean;
  canExecute: boolean;
  onExecute: () => void;
  onCancel: () => void;
  onSave?: () => void;
  onHistory?: () => void;
  settings?: Partial<ExecutionSettings>;
  onSettingsChange?: (settings: ExecutionSettings) => void;
  language?: string;
  onLanguageChange?: (language: string) => void;
}

const defaultSettings: ExecutionSettings = {
  timeout: 30000,
  memoryLimit: 256,
  enableNetwork: false,
  enableDebug: false,
  saveOutput: true,
  stdinEnabled: false
};

const languages = [
  { id: 'python', name: 'Python', version: '3.11' },
  { id: 'javascript', name: 'JavaScript', version: 'Node.js 20' },
  { id: 'typescript', name: 'TypeScript', version: '5.0' },
  { id: 'java', name: 'Java', version: '17' },
  { id: 'cpp', name: 'C++', version: 'GCC 12' },
  { id: 'c', name: 'C', version: 'GCC 12' },
  { id: 'rust', name: 'Rust', version: '1.70' },
  { id: 'go', name: 'Go', version: '1.20' },
  { id: 'ruby', name: 'Ruby', version: '3.2' }
];

export function ExecutionControls({
  isExecuting,
  canExecute,
  onExecute,
  onCancel,
  onSave,
  onHistory,
  settings = {},
  onSettingsChange,
  language = 'python',
  onLanguageChange
}: ExecutionControlsProps) {
  const [showSettings, setShowSettings] = useState(false);
  const [localSettings, setLocalSettings] = useState<ExecutionSettings>({ ...defaultSettings, ...settings });
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Handle settings change
  const handleSettingChange = useCallback((key: keyof ExecutionSettings, value: boolean | number) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange?.(newSettings);
  }, [localSettings, onSettingsChange]);

  // Handle fullscreen toggle
  const handleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // Keyboard shortcut handler
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter' && canExecute && !isExecuting) {
          e.preventDefault();
          onExecute();
        } else if (e.key === 's' && onSave) {
          e.preventDefault();
          onSave();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [canExecute, isExecuting, onExecute, onSave]);

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-800 
                   border-b border-gray-200 dark:border-gray-700">
      {/* Left section - Language selector */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <select
            value={language}
            onChange={(e) => onLanguageChange?.(e.target.value)}
            disabled={isExecuting}
            className="appearance-none px-4 py-1.5 pr-10 text-sm bg-white dark:bg-gray-700 
                     border border-gray-300 dark:border-gray-600 rounded-lg
                     text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>

        {/* Keyboard shortcut hint */}
        <span className="text-xs text-gray-500 hidden sm:inline-block">
          <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-600 rounded">Ctrl</kbd>
          <span className="mx-1">+</span>
          <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-600 rounded">Enter</kbd>
          <span className="ml-1">to run</span>
        </span>
      </div>

      {/* Center section - Action buttons */}
      <div className="flex items-center gap-2">
        {/* Run button */}
        <button
          onClick={isExecuting ? onCancel : onExecute}
          disabled={!isExecuting && !canExecute}
          className={`flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm transition-all ${
            isExecuting
              ? 'bg-red-100 hover:bg-red-200 text-red-700 dark:bg-red-900/30 dark:hover:bg-red-900/50 dark:text-red-400'
              : 'bg-green-600 hover:bg-green-700 text-white shadow-sm disabled:opacity-50 disabled:cursor-not-allowed'
          }`}
        >
          {isExecuting ? (
            <>
                <StopIcon />
                Cancel
            </>
          ) : (
            <>
              <PlayIcon />
              Run
            </>
          )}
        </button>

        {/* Save button */}
        {onSave && (
          <button
            onClick={onSave}
            disabled={isExecuting}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 
                     bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
                     rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <SaveIcon />
            <span className="hidden sm:inline">Save</span>
          </button>
        )}

        {/* History button */}
        {onHistory && (
          <button
            onClick={onHistory}
            disabled={isExecuting}
            className="flex items-center gap-2 px-3 py-2 text-gray-500 
                     hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors
                     disabled:opacity-50"
            title="Execution History"
          >
            <HistoryIcon />
          </button>
        )}
      </div>

      {/* Right section - Settings and view options */}
      <div className="flex items-center gap-2">
        {/* Settings dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              showSettings 
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                : 'text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            <SettingsIcon />
            <span className="hidden md:inline text-sm">Settings</span>
          </button>

          {showSettings && (
            <div className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-gray-800 
                          rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 
                          p-4 z-50">
              <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Execution Settings
              </h4>

              <div className="space-y-4">
                {/* Timeout */}
                <div>
                  <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                    Timeout (ms)
                  </label>
                  <input
                    type="number"
                    value={localSettings.timeout}
                    onChange={(e) => handleSettingChange('timeout', parseInt(e.target.value) || 0)}
                    min={1000}
                    max={120000}
                    step={1000}
                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 
                             rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>

                {/* Memory limit */}
                <div>
                  <label className="block text-sm text-gray-700 dark:text-gray-300 mb-1">
                    Memory Limit (MB)
                  </label>
                  <input
                    type="number"
                    value={localSettings.memoryLimit}
                    onChange={(e) => handleSettingChange('memoryLimit', parseInt(e.target.value) || 0)}
                    min={64}
                    max={2048}
                    step={64}
                    className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 
                             rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  />
                </div>

                {/* Toggles */}
                <div className="space-y-2">
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">Enable Network</span>
                    <input
                      type="checkbox"
                      checked={localSettings.enableNetwork}
                      onChange={(e) => handleSettingChange('enableNetwork', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                  </label>

                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">Debug Mode</span>
                    <input
                      type="checkbox"
                      checked={localSettings.enableDebug}
                      onChange={(e) => handleSettingChange('enableDebug', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                  </label>

                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">Save Output</span>
                    <input
                      type="checkbox"
                      checked={localSettings.saveOutput}
                      onChange={(e) => handleSettingChange('saveOutput', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                  </label>
                </div>
              </div>

              <button
                onClick={() => setShowSettings(false)}
                className="w-full mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white 
                         rounded-lg text-sm font-medium transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>

        {/* Fullscreen button */}
        <button
          onClick={handleFullscreen}
          className="flex items-center gap-2 px-3 py-2 text-gray-500 
                   hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
        >
          <FullscreenIcon />
        </button>
      </div>
    </div>
  );
}
