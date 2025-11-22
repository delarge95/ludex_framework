import React, { useState, useEffect } from 'react';
import { Settings, X, Save, AlertTriangle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface SettingsModalProps {
  onProviderChange: (provider: string, model: string) => void;
}

const PROVIDERS = {
  github: {
    name: "GitHub Models",
    models: ["gpt-4o", "gpt-4o-mini", "Llama-3.3-70B-Instruct", "Phi-4"],
    description: "Free during beta. Best for development."
  },
  ollama: {
    name: "Ollama (Local)",
    models: ["mistral:7b", "llama3:8b", "qwen2.5:7b"],
    description: "Runs locally. Requires 'ollama serve'."
  },
  groq: {
    name: "Groq",
    models: ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"],
    description: "Extremely fast inference. Free tier available."
  },
  anthropic: {
    name: "Anthropic",
    models: ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"],
    description: "High quality reasoning. Paid API."
  }
};

export function SettingsModal({ onProviderChange }: SettingsModalProps) {
  const [provider, setProvider] = useState<string>("github");
  const [model, setModel] = useState<string>("gpt-4o");
  const [isOpen, setIsOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "saving" | "success" | "error">("idle");

  // Reset model when provider changes
  useEffect(() => {
    if (PROVIDERS[provider as keyof typeof PROVIDERS]) {
      setModel(PROVIDERS[provider as keyof typeof PROVIDERS].models[0]);
    }
  }, [provider]);

  const handleSave = async () => {
    setStatus("saving");
    try {
      const response = await fetch('http://localhost:9090/config/provider', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, model }),
      });

      if (!response.ok) throw new Error('Failed to update provider');

      onProviderChange(provider, model);
      setStatus("success");
      setTimeout(() => {
        setIsOpen(false);
        setStatus("idle");
      }, 1000);
    } catch (error) {
      console.error(error);
      setStatus("error");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" className="h-9 w-9">
          <Settings className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>System Settings</DialogTitle>
          <DialogDescription>
            Configure the AI provider and model used for generation.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="provider">AI Provider</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger id="provider">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(PROVIDERS).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    {config.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {PROVIDERS[provider as keyof typeof PROVIDERS]?.description}
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="model">Model</Label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger id="model">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {PROVIDERS[provider as keyof typeof PROVIDERS]?.models.map((m) => (
                  <SelectItem key={m} value={m}>
                    {m}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {status === "error" && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Failed to save settings. Check backend connection.
              </AlertDescription>
            </Alert>
          )}
          
          {status === "success" && (
            <Alert className="bg-green-50 text-green-900 border-green-200">
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>
                Settings updated successfully.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} disabled={status === "saving"}>
            {status === "saving" ? "Saving..." : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
