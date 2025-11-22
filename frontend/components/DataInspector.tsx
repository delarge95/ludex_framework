import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import dynamic from 'next/dynamic';
import { Copy, Download, AlertCircle } from 'lucide-react';

// Dynamically import ReactJson to avoid SSR issues
const ReactJson = dynamic(() => import('@microlink/react-json-view'), { ssr: false });

interface DataInspectorProps {
  isOpen: boolean;
  onClose: () => void;
  currentAgent?: string;
}

export default function DataInspector({ isOpen, onClose, currentAgent = 'market_analyst' }: DataInspectorProps) {
  const [igdbData, setIgdbData] = useState<any>(null);
  const [steamData, setSteamData] = useState<any>(null);
  const [steamspyData, setSteamspyData] = useState<any>(null);
  const [validationWarnings, setValidationWarnings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch data from API
  const fetchData = async (source: string) => {
    setLoading(true);
    setError(null);
    try {
      const apiKey = localStorage.getItem('data_inspector_api_key') || '';
      const response = await fetch(`http://localhost:9090/data/${currentAgent}/${source}`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch ${source} data: ${response.statusText}`);
      }

      const data = await response.json();
      
      switch (source) {
        case 'igdb':
          setIgdbData(data);
          break;
        case 'steam':
          setSteamData(data);
          break;
        case 'steamspy':
          setSteamspyData(data);
          break;
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchValidationWarnings = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiKey = localStorage.getItem('data_inspector_api_key') || '';
      const response = await fetch('http://localhost:9090/data/validation/warnings', {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch validation warnings');
      }

      const data = await response.json();
      setValidationWarnings(data.warnings || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
  };

  // Download as JSON
  const downloadJSON = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Load all data when dialog opens
  React.useEffect(() => {
    if (isOpen) {
      fetchData('igdb');
      fetchData('steam');
      fetchData('steamspy');
      fetchValidationWarnings();
    }
  }, [isOpen, currentAgent]);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'INFO':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Data Inspector - Raw API Data</DialogTitle>
        </DialogHeader>

        {error && (
          <div className="p-4 mb-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <Tabs defaultValue="igdb" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="igdb">IGDB Data</TabsTrigger>
            <TabsTrigger value="steam">Steam Data</TabsTrigger>
            <TabsTrigger value="steamspy">SteamSpy Data</TabsTrigger>
            <TabsTrigger value="validation">Validation</TabsTrigger>
          </TabsList>

          <TabsContent value="igdb" className="mt-4">
            <div className="space-y-2">
              <div className="flex gap-2 justify-end">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(igdbData)}
                  disabled={!igdbData}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => downloadJSON(igdbData, 'igdb_data.json')}
                  disabled={!igdbData}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
              {loading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : igdbData ? (
                <div className="border rounded-md p-4 bg-gray-50 max-h-96 overflow-auto">
                  <ReactJson
                    src={igdbData}
                    theme="rjv-default"
                    collapsed={1}
                    displayDataTypes={false}
                    enableClipboard={false}
                  />
                </div>
              ) : (
                <p className="text-sm text-gray-500">No IGDB data available</p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="steam" className="mt-4">
            <div className="space-y-2">
              <div className="flex gap-2 justify-end">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(steamData)}
                  disabled={!steamData}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => downloadJSON(steamData, 'steam_data.json')}
                  disabled={!steamData}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
              {loading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : steamData ? (
                <div className="border rounded-md p-4 bg-gray-50 max-h-96 overflow-auto">
                  <ReactJson
                    src={steamData}
                    theme="rjv-default"
                    collapsed={1}
                    displayDataTypes={false}
                    enableClipboard={false}
                  />
                </div>
              ) : (
                <p className="text-sm text-gray-500">No Steam data available</p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="steamspy" className="mt-4">
            <div className="space-y-2">
              <div className="flex gap-2 justify-end">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => copyToClipboard(steamspyData)}
                  disabled={!steamspyData}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => downloadJSON(steamspyData, 'steamspy_data.json')}
                  disabled={!steamspyData}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
              {loading ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : steamspyData ? (
                <div className="border rounded-md p-4 bg-gray-50 max-h-96 overflow-auto">
                  <ReactJson
                    src={steamspyData}
                    theme="rjv-default"
                    collapsed={1}
                    displayDataTypes={false}
                    enableClipboard={false}
                  />
                </div>
              ) : (
                <p className="text-sm text-gray-500">No SteamSpy data available</p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="validation" className="mt-4">
            <div className="space-y-3">
              {validationWarnings.length > 0 ? (
                validationWarnings.map((warning, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-md ${getSeverityColor(warning.severity)}`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-sm uppercase">{warning.severity}</p>
                        <p className="text-sm mt-1">{warning.message}</p>
                        {warning.affected_field && (
                          <p className="text-xs mt-2 opacity-75">
                            Field: <span className="font-mono">{warning.affected_field}</span>
                          </p>
                        )}
                        {warning.suggested_action && (
                          <p className="text-xs mt-1">
                            <strong>Suggestion:</strong> {warning.suggested_action}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">No validation warnings</p>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
