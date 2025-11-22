"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { HelpCircle, Send } from "lucide-react";

interface DirectorQuestionsProps {
  questions: string[];
  onAnswer: (answer: string) => void;
}

export function DirectorQuestions({ questions, onAnswer }: DirectorQuestionsProps) {
  const [answer, setAnswer] = React.useState("");

  const handleSubmit = () => {
    if (answer.trim()) {
      onAnswer(answer);
      setAnswer("");
    }
  };

  if (questions.length === 0) return null;

  return (
    <Card className="border-amber-500/50 bg-amber-50/50 dark:bg-amber-950/20">
      <CardHeader>
        <div className="flex items-center gap-2">
          <HelpCircle className="h-5 w-5 text-amber-600" />
          <CardTitle>Director Needs Clarification</CardTitle>
        </div>
        <CardDescription>
          Please provide more details to help refine your concept
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {questions.map((question, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-amber-600 font-medium">{idx + 1}.</span>
              <p className="text-sm">{question}</p>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          <Textarea
            placeholder="Provide your answers here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            className="min-h-[100px]"
          />
          <Button 
            onClick={handleSubmit} 
            className="w-full"
            disabled={!answer.trim()}
          >
            <Send className="mr-2 h-4 w-4" />
            Submit Answer
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
