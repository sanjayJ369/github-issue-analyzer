import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Github, Play, RefreshCw, AlertCircle } from "lucide-react";
import ProviderSelect from "./ProviderSelect";
import { getProviders } from "../api";

const STORAGE_KEY = "issueinsight_provider";

const AnalysisForm = ({ onAnalyze, isLoading }) => {
    const [repoUrl, setRepoUrl] = useState("https://github.com/fastapi/fastapi");
    const [issueNumber, setIssueNumber] = useState(1);
    
    // Provider state
    const [providers, setProviders] = useState([]);
    const [selectedProviderId, setSelectedProviderId] = useState(null);
    const [loadingProviders, setLoadingProviders] = useState(true);
    const [fetchError, setFetchError] = useState(false);

    const fetchProviders = useCallback(async () => {
        setLoadingProviders(true);
        setFetchError(false);
        const data = await getProviders();
        
        if (data === null) {
            setFetchError(true);
            setProviders([]);
        } else {
            setProviders(data);
            
            // Only consider available or assumed providers for selection
            const availableProviders = data.filter(p => ['available', 'assumed'].includes(p.status));
            
            // Restore from localStorage or default to first available
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored && availableProviders.some(p => p.id === stored)) {
                setSelectedProviderId(stored);
            } else if (availableProviders.length > 0) {
                // Clear invalid stored value and select first available
                localStorage.removeItem(STORAGE_KEY);
                setSelectedProviderId(availableProviders[0].id);
            }
        }
        setLoadingProviders(false);
    }, []);

    // Fetch providers on mount
    useEffect(() => {
        fetchProviders();
    }, [fetchProviders]);

    // Persist selection to localStorage
    const handleProviderChange = (providerId) => {
        setSelectedProviderId(providerId);
        localStorage.setItem(STORAGE_KEY, providerId);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Pass provider ID (null if only 1 provider for auto-selection)
        const providerToUse = providers.length > 1 ? selectedProviderId : null;
        onAnalyze(repoUrl, issueNumber, providerToUse);
    };

    return (
        <Card className="border-border/50 shadow-xl shadow-black/5 dark:shadow-black/20 bg-card/80 backdrop-blur-sm">
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

                    {/* Provider Selection */}
                    {fetchError ? (
                        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center justify-between">
                             <div className="flex items-center gap-2 text-sm text-destructive">
                                <AlertCircle className="w-4 h-4" />
                                <span>Failed to load providers</span>
                             </div>
                             <Button 
                                type="button" 
                                variant="outline" 
                                size="sm" 
                                className="h-7 text-xs"
                                onClick={fetchProviders}
                             >
                                <RefreshCw className="w-3 h-3 mr-1" />
                                Retry
                             </Button>
                        </div>
                    ) : (
                        <ProviderSelect 
                            providers={providers}
                            selectedId={selectedProviderId}
                            onChange={handleProviderChange}
                            loading={loadingProviders}
                        />
                    )}

                    <Button 
                        type="submit" 
                        className="w-full font-semibold" 
                        disabled={isLoading || loadingProviders || fetchError} 
                        size="lg"
                    >
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
