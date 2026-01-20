import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Github, Play } from "lucide-react";

const AnalysisForm = ({ onAnalyze, isLoading }) => {
    const [repoUrl, setRepoUrl] = useState("https://github.com/fastapi/fastapi");
    const [issueNumber, setIssueNumber] = useState(1);

    const handleSubmit = (e) => {
        e.preventDefault();
        onAnalyze(repoUrl, issueNumber);
    };

    return (
        <Card className="border-border/50 shadow-xl shadow-black/20">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Github className="w-5 h-5 text-primary" />
                    Analyze Issue
                </CardTitle>
                <CardDescription>
                    Enter the repository URL and issue ID to generate an AI analysis.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            Repository URL
                        </label>
                        <Input 
                            value={repoUrl}
                            onChange={(e) => setRepoUrl(e.target.value)}
                            placeholder="https://github.com/owner/repo"
                            required
                        />
                    </div>
                    
                    <div className="space-y-2">
                        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            Issue ID
                        </label>
                        <Input 
                            type="number" 
                            value={issueNumber}
                            onChange={(e) => setIssueNumber(e.target.value)}
                            min="1"
                            required
                        />
                    </div>

                    <Button type="submit" className="w-full font-semibold" disabled={isLoading} size="lg">
                        {isLoading ? (
                            <>
                                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                                Processing...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4 mr-2 fill-current" />
                                Run Analysis
                            </>
                        )}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
};

export default AnalysisForm;
