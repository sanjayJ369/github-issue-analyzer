import React, { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, Circle, XCircle } from "lucide-react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

const steps = [
    { id: 1, message: "Connecting to GitHub API...", duration: 0 },
    { id: 2, message: "Fetching Issue & Comments...", duration: 1500 },
    { id: 3, message: "Preprocessing Markdown content...", duration: 2800 },
    { id: 4, message: "LLM Analyzing impact and priority...", duration: 4200 },
    { id: 5, message: "Generating structured insights...", duration: 5500 },
];

const StatusFeed = ({ error, onRetry }) => {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        if (error) return; // Stop progression on error

        const timers = steps.map((step, index) => {
            return setTimeout(() => {
                setCurrentStep(index);
            }, step.duration);
        });

        return () => timers.forEach(timer => clearTimeout(timer));
    }, [error]);

    return (
        <Card className="p-6 border-dashed border-border/60 bg-card/30 backdrop-blur-sm min-h-[400px] flex flex-col items-center justify-center animate-in fade-in zoom-in-95 duration-300">
             <div className="space-y-6 w-full max-w-md">
                <div className="flex items-center gap-3 justify-center mb-8">
                    <div className="relative">
                        <div className={`absolute inset-0 blur-xl rounded-full ${error ? "bg-destructive/20" : "bg-primary/20"}`} />
                        {error ? (
                            <XCircle className="w-10 h-10 text-destructive relative z-10" />
                        ) : (
                            <Loader2 className="w-10 h-10 animate-spin text-primary relative z-10" />
                        )}
                    </div>
                    <span className="text-xl font-medium tracking-tight">
                        {error ? "Analysis Failed" : "Agent Working..."}
                    </span>
                </div>

                <div className="space-y-4">
                    {steps.map((step, index) => {
                        const isCompleted = !error && currentStep > index;
                        const isCurrent = currentStep === index;
                        const isPending = currentStep < index;
                        const isFailed = error && isCurrent;

                        // If error occurred, steps AFTER valid ones are pending
                        // But the current step is the failed one.
                        
                        return (
                            <div 
                                key={step.id} 
                                className={`flex items-start gap-3 transition-all duration-500 ${
                                    isPending ? "opacity-30 scale-95" : "opacity-100 scale-100"
                                }`}
                            >
                                {isFailed ? (
                                    <XCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                                ) : isCompleted ? (
                                    <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                                ) : isCurrent ? (
                                    <Loader2 className="w-5 h-5 text-primary animate-spin shrink-0 mt-0.5" />
                                ) : (
                                    <Circle className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                                )}
                                
                                <div className="flex flex-col gap-1">
                                    <span className={`text-sm leading-none pt-1 ${isCurrent || isFailed ? "font-semibold text-foreground" : "text-muted-foreground"}`}>
                                        {step.message}
                                    </span>
                                    {isFailed && (
                                        <div className="mt-2 text-xs text-destructive bg-destructive/10 p-3 rounded-md border border-destructive/20 font-mono">
                                            {error}
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
                
                {error && onRetry && (
                    <div className="flex justify-center mt-6 pt-4">
                        <Button onClick={onRetry} variant="outline" className="border-destructive/30 hover:bg-destructive/10 hover:text-destructive">
                            Try Again
                        </Button>
                    </div>
                )}
             </div>
        </Card>
    );
};

export default StatusFeed;
