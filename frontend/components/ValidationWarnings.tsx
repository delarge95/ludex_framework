import React from 'react';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

interface ValidationWarning {
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  category: string;
  message: string;
  affected_field?: string;
  igdb_value?: any;
  steam_value?: any;
  steamspy_value?: any;
  suggested_action?: string;
}

interface ValidationWarningsProps {
  warnings: ValidationWarning[];
}

export default function ValidationWarnings({ warnings }: ValidationWarningsProps) {
  if (warnings.length === 0) {
    return (
      <div className="p-4 bg-green-50 border border-green-200 rounded-md">
        <p className="text-sm text-green-700 flex items-center gap-2">
          <Info className="w-4 h-4" />
          No validation warnings - all data sources are consistent
        </p>
      </div>
    );
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'WARNING':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'INFO':
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'WARNING':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      case 'INFO':
      default:
        return 'bg-blue-50 border-blue-200 text-blue-900';
    }
  };

  const criticalCount = warnings.filter(w => w.severity === 'CRITICAL').length;
  const warningCount = warnings.filter(w => w.severity === 'WARNING').length;
  const infoCount = warnings.filter(w => w.severity === 'INFO').length;

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex gap-4 p-4 bg-gray-50 border border-gray-200 rounded-md">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600" />
          <span className="text-sm font-medium">{criticalCount} Critical</span>
        </div>
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-600" />
          <span className="text-sm font-medium">{warningCount} Warnings</span>
        </div>
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium">{infoCount} Info</span>
        </div>
      </div>

      {/* Warning List */}
      <div className="space-y-3">
        {warnings.map((warning, index) => (
          <div
            key={index}
            className={`p-4 border rounded-md ${getSeverityColor(warning.severity)}`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                {getSeverityIcon(warning.severity)}
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wide">
                    {warning.severity}
                  </span>
                  <span className="text-xs px-2 py-1 bg-white/50 rounded">
                    {warning.category}
                  </span>
                </div>
                
                <p className="text-sm font-medium">{warning.message}</p>
                
                {warning.affected_field && (
                  <p className="text-xs opacity-75">
                    <span className="font-semibold">Field:</span>{' '}
                    <code className="px-1.5 py-0.5 bg-black/10 rounded font-mono">
                      {warning.affected_field}
                    </code>
                  </p>
                )}

                {(warning.igdb_value || warning.steam_value || warning.steamspy_value) && (
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    {warning.igdb_value && (
                      <div className="p-2 bg-white/50 rounded">
                        <p className="font-semibold mb-1">IGDB</p>
                        <p className="font-mono">{JSON.stringify(warning.igdb_value)}</p>
                      </div>
                    )}
                    {warning.steam_value && (
                      <div className="p-2 bg-white/50 rounded">
                        <p className="font-semibold mb-1">Steam</p>
                        <p className="font-mono">{JSON.stringify(warning.steam_value)}</p>
                      </div>
                    )}
                    {warning.steamspy_value && (
                      <div className="p-2 bg-white/50 rounded">
                        <p className="font-semibold mb-1">SteamSpy</p>
                        <p className="font-mono">{JSON.stringify(warning.steamspy_value)}</p>
                      </div>
                    )}
                  </div>
                )}

                {warning.suggested_action && (
                  <div className="mt-2 p-2 bg-white/50 rounded">
                    <p className="text-xs">
                      <span className="font-semibold">→ Suggested Action:</span>{' '}
                      {warning.suggested_action}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
