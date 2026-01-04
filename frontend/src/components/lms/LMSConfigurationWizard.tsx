import React, { useState, useCallback } from 'react';
import { useLMSIntegration } from '../../hooks/useLMSIntegration';
import { LMSProvider, OAuthConfig } from '../../contexts/LMSIntegrationContext';

// Icons
const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const ChevronRightIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const ChevronLeftIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const LinkIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
);

const CloudIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
  </svg>
);

const ShieldIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

// Provider templates
const providerTemplates: Record<string, Partial<LMSProvider>> = {
  canvas: {
    name: 'Canvas LMS',
    type: 'canvas',
    baseUrl: 'https://canvas.instructure.com',
    apiVersion: 'v1',
    authType: 'oauth2',
    enabled: false
  },
  blackboard: {
    name: 'Blackboard Learn',
    type: 'blackboard',
    baseUrl: '',
    apiVersion: 'learn.api',
    authType: 'oauth2',
    enabled: false
  },
  moodle: {
    name: 'Moodle',
    type: 'moodle',
    baseUrl: '',
    apiVersion: 'webservice/rest.php',
    authType: 'apikey',
    enabled: false
  },
  brightspace: {
    name: 'D2L Brightspace',
    type: 'brightspace',
    baseUrl: '',
    apiVersion: '1.0',
    authType: 'oauth2',
    enabled: false
  }
};

type WizardStep = 'select' | 'configure' | 'authenticate' | 'verify' | 'complete';

interface LMSConfigurationWizardProps {
  onComplete?: (provider: LMSProvider) => void;
  onCancel?: () => void;
  editProviderId?: string;
}

export function LMSConfigurationWizard({ onComplete, onCancel, editProviderId }: LMSConfigurationWizardProps) {
  const [step, setStep] = useState<WizardStep>('select');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [config, setConfig] = useState<Partial<LMSProvider>>({});
  const [oauthConfig, setOAuthConfig] = useState<OAuthConfig | null>(null);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const {
    addProvider,
    updateProvider,
    testConnection,
    initiateOAuth,
    getOAuthConfig
  } = useLMSIntegration();

  // Handle template selection
  const handleTemplateSelect = useCallback((templateId: string) => {
    setSelectedTemplate(templateId);
    setConfig(providerTemplates[templateId] || {});
    setStep('configure');
  }, []);

  // Handle configuration save
  const handleConfigSave = useCallback(async () => {
    if (!selectedTemplate) return;
    
    setIsProcessing(true);
    try {
      if (config.authType === 'oauth2') {
        const oauth = await getOAuthConfig(selectedTemplate);
        setOAuthConfig(oauth);
        setStep('authenticate');
      } else {
        // Test API key connection
        const result = await testConnection(selectedTemplate);
        setTestResult(result);
        setStep('verify');
      }
    } catch (error) {
      console.error('Failed to get OAuth config:', error);
      setTestResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to configure provider' 
      });
      setStep('verify');
    } finally {
      setIsProcessing(false);
    }
  }, [selectedTemplate, config, getOAuthConfig, testConnection]);

  // Handle OAuth initiation
  const handleInitiateOAuth = useCallback(async () => {
    if (!selectedTemplate) return;
    
    setIsProcessing(true);
    try {
      initiateOAuth(selectedTemplate);
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to initiate OAuth' 
      });
      setStep('verify');
    } finally {
      setIsProcessing(false);
    }
  }, [selectedTemplate, initiateOAuth]);

  // Handle OAuth callback (called after redirect)
  const handleOAuthCallback = useCallback(async (code: string, state: string) => {
    setIsProcessing(true);
    try {
      // The hook handles the callback internally
      setStep('verify');
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Authentication failed' 
      });
    } finally {
      setIsProcessing(false);
    }
  }, []);

  // Handle final verification
  const handleVerify = useCallback(async () => {
    setIsProcessing(true);
    try {
      // Test the connection
      const result = await testConnection(selectedTemplate!);
      setTestResult(result);
      
      if (result.success) {
        setStep('complete');
      }
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Connection test failed' 
      });
    } finally {
      setIsProcessing(false);
    }
  }, [selectedTemplate, testConnection]);

  // Handle provider creation/update
  const handleComplete = useCallback(async () => {
    setIsProcessing(true);
    try {
      let provider: LMSProvider;
      
      if (editProviderId) {
        await updateProvider(editProviderId, { ...config, enabled: true });
        provider = { ...config, id: editProviderId } as LMSProvider;
      } else {
        provider = await addProvider({ ...config, enabled: true });
      }
      
      onComplete?.(provider);
    } catch (error) {
      setTestResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to save provider' 
      });
    } finally {
      setIsProcessing(false);
    }
  }, [config, editProviderId, addProvider, updateProvider, onComplete]);

  // Steps configuration
  const steps: { id: WizardStep; title: string; description: string }[] = [
    { id: 'select', title: 'Select Platform', description: 'Choose your LMS provider' },
    { id: 'configure', title: 'Configure', description: 'Set up connection details' },
    { id: 'authenticate', title: 'Authenticate', description: 'Connect with your LMS' },
    { id: 'verify', title: 'Verify', description: 'Test the connection' },
    { id: 'complete', title: 'Complete', description: 'Ready to sync' }
  ];

  const currentStepIndex = steps.findIndex(s => s.id === step);

  return (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      {/* Progress bar */}
      <div className="bg-gray-100 dark:bg-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          {steps.map((s, index) => (
            <React.Fragment key={s.id}>
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                               ${index < currentStepIndex 
                                 ? 'bg-green-500 text-white' 
                                 : index === currentStepIndex 
                                   ? 'bg-blue-500 text-white' 
                                   : 'bg-gray-300 dark:bg-gray-600 text-gray-500'}`}>
                  {index < currentStepIndex ? <CheckIcon /> : index + 1}
                </div>
                <div className="hidden md:block">
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {s.title}
                  </div>
                  <div className="text-xs text-gray-500">{s.description}</div>
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-4 ${
                  index < currentStepIndex ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Step 1: Select Platform */}
        {step === 'select' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              Select Your Learning Management System
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(providerTemplates).map(([id, template]) => (
                <button
                  key={id}
                  onClick={() => handleTemplateSelect(id)}
                  className="flex items-start gap-4 p-4 border-2 border-gray-200 dark:border-gray-600 
                           rounded-xl hover:border-blue-500 dark:hover:border-blue-400 
                           transition-colors text-left group"
                >
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center 
                                justify-center text-blue-600 dark:text-blue-400 group-hover:bg-blue-500 
                                group-hover:text-white transition-colors">
                    <CloudIcon />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">{template.name}</h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {template.authType === 'oauth2' ? 'OAuth 2.0 Authentication' : 'API Key Authentication'}
                    </p>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 flex items-center gap-2">
                <ShieldIcon />
                Enterprise Integration
              </h4>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                Don't see your LMS? We support custom integrations for enterprise deployments. 
                Contact our team for a tailored solution.
              </p>
            </div>
          </div>
        )}

        {/* Step 2: Configure */}
        {step === 'configure' && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <button
                onClick={() => setStep('select')}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <ChevronLeftIcon />
              </button>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Configure {providerTemplates[selectedTemplate!]?.name}
              </h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Integration Name
                </label>
                <input
                  type="text"
                  value={config.name || ''}
                  onChange={(e) => setConfig({ ...config, name: e.target.value })}
                  placeholder="My LMS Integration"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Base URL
                </label>
                <input
                  type="url"
                  value={config.baseUrl || ''}
                  onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
                  placeholder="https://your-lms-instance.com"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  The base URL of your LMS instance
                </p>
              </div>

              {config.authType === 'apikey' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={(config as { apiKey?: string }).apiKey || ''}
                    onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                    placeholder="Enter your API key"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Generate an API key in your LMS administrator settings
                  </p>
                </div>
              )}

              {config.authType === 'basic' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Username
                    </label>
                    <input
                      type="text"
                      value={(config as { username?: string }).username || ''}
                      onChange={(e) => setConfig({ ...config, username: e.target.value })}
                      placeholder="API username"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                               focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Password
                    </label>
                    <input
                      type="password"
                      value={(config as { password?: string }).password || ''}
                      onChange={(e) => setConfig({ ...config, password: e.target.value })}
                      placeholder="API password"
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                               bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                               focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={onCancel}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 
                         dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfigSave}
                disabled={isProcessing || !config.baseUrl}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 
                         text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {isProcessing ? 'Processing...' : (
                  <>
                    Continue
                    <ChevronRightIcon />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Authenticate */}
        {step === 'authenticate' && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <button
                onClick={() => setStep('configure')}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <ChevronLeftIcon />
              </button>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Authenticate with {providerTemplates[selectedTemplate!]?.name}
              </h2>
            </div>

            <div className="text-center py-12">
              <div className="w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center 
                            justify-center mx-auto mb-6 text-blue-600 dark:text-blue-400">
                <LinkIcon />
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Connect Your Account
              </h3>
              <p className="text-gray-500 max-w-md mx-auto mb-8">
                You'll be redirected to {providerTemplates[selectedTemplate!]?.name} to authorize 
                this integration. We only request the minimum permissions needed.
              </p>

              <button
                onClick={handleInitiateOAuth}
                disabled={isProcessing}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                         font-medium transition-colors disabled:opacity-50"
              >
                {isProcessing ? 'Connecting...' : 'Connect with OAuth'}
              </button>

              <p className="text-xs text-gray-500 mt-4">
                Your credentials are never stored on our servers
              </p>
            </div>
          </div>
        )}

        {/* Step 4: Verify */}
        {step === 'verify' && (
          <div>
            <div className="flex items-center gap-3 mb-6">
              <button
                onClick={() => setStep(config.authType === 'oauth2' ? 'authenticate' : 'configure')}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <ChevronLeftIcon />
              </button>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Verify Connection
              </h2>
            </div>

            <div className="text-center py-8">
              {isProcessing ? (
                <>
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-600 dark:text-gray-400">Testing connection...</p>
                </>
              ) : testResult ? (
                <>
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
                    testResult.success 
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-600' 
                      : 'bg-red-100 dark:bg-red-900/30 text-red-600'
                  }`}>
                    {testResult.success ? <CheckIcon /> : (
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    {testResult.success ? 'Connection Successful!' : 'Connection Failed'}
                  </h3>
                  <p className="text-gray-500 mb-6">{testResult.message}</p>
                  
                  {testResult.success ? (
                    <button
                      onClick={handleComplete}
                      className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg 
                               font-medium transition-colors"
                    >
                      Complete Setup
                    </button>
                  ) : (
                    <button
                      onClick={() => setStep('configure')}
                      className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                               font-medium transition-colors"
                    >
                      Go Back and Fix
                    </button>
                  )}
                </>
              ) : (
                <button
                  onClick={handleVerify}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                           font-medium transition-colors"
                >
                  Test Connection
                </button>
              )}
            </div>
          </div>
        )}

        {/* Step 5: Complete */}
        {step === 'complete' && (
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center 
                          justify-center mx-auto mb-6 text-green-600">
              <CheckIcon />
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Integration Complete!
            </h3>
            <p className="text-gray-500 max-w-md mx-auto mb-8">
              Your {providerTemplates[selectedTemplate!]?.name} integration is ready. 
              You can now sync courses, rosters, and assignments.
            </p>

            <button
              onClick={() => onComplete?.(config as LMSProvider)}
              className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg 
                       font-medium transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useState, useCallback } from 'react';
