import React, { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Sparkles } from "lucide-react";

interface InputFormProps {
  onSubmit: (idea: string) => void;
  isGenerating: boolean;
}

export function InputForm({ onSubmit, isGenerating }: InputFormProps) {
  const [idea, setIdea] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (idea.trim()) {
      onSubmit(idea);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">New Project</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent>
          <div className="grid w-full gap-2">
            <Label htmlFor="idea">Game Concept</Label>
            <Textarea
              id="idea"
              placeholder="Describe your game idea (e.g., 'A roguelike deckbuilder where you play as a cybernetic cat hacking corporate servers')..."
              className="min-h-[100px]"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              disabled={isGenerating}
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" disabled={!idea.trim() || isGenerating}>
            {isGenerating ? (
              <>
                <Sparkles className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Start Production
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
