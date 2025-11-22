import React from 'react';
import ReactMarkdown from 'react-markdown';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText } from "lucide-react";

interface GDDViewerProps {
  markdown: string;
}

export function GDDViewer({ markdown }: GDDViewerProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Game Design Document
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-[600px] w-full p-6">
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {markdown ? (
              <ReactMarkdown>{markdown}</ReactMarkdown>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-400 py-20">
                <FileText className="h-12 w-12 mb-4 opacity-20" />
                <p>Waiting for generation...</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
