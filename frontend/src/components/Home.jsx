import React, { useState } from 'react';
import AnalysisForm from './AnalysisForm';
import Dashboard from './Dashboard';
import StatusFeed from './StatusFeed';
import { analyzeIssue } from '../api';

const Home = () => {
    const [analysisResult, setAnalysisResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [repoUrl, setRepoUrl] = useState("");
    const [issueNumber, setIssueNumber] = useState(null);

    const handleAnalyze = async (url, num, providerId = null) => {
        setLoading(true);
        setError(null);
        setAnalysisResult(null);
        setRepoUrl(url);
        setIssueNumber(num);

        try {
            const data = await analyzeIssue(url, num, providerId);
            setAnalysisResult(data);
        } catch (err) {
            setError(err.message || "An unexpected error occurred. Please check the URL and ID.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            <div className="text-center mb-8 md:mb-12 space-y-3 md:space-y-4 px-2">
                <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    IssueInsight
                </h1>
                <p className="text-lg sm:text-xl font-semibold text-foreground/80">
                    Agentic GitHub Issue Analyzer
                </p>
                <p className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto">
                    Transform messy issues into structured engineering insights instantly.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Left Column: Input */}
                <div className="lg:col-span-4 xl:col-span-4 lg:sticky lg:top-24 space-y-6">
                    <AnalysisForm onAnalyze={handleAnalyze} isLoading={loading} />
                </div>


                {/* Right Column: Results */}
                <div className="lg:col-span-8 xl:col-span-8 min-h-[500px]">
                    
                    {analysisResult?.meta?.warning && (
                        <div className="p-4 rounded-lg bg-amber-50 dark:bg-yellow-500/10 border border-amber-200 dark:border-yellow-500/30 text-amber-800 dark:text-yellow-400 mb-6 flex items-start gap-3 shadow-sm animate-in fade-in slide-in-from-top-2">
                            <span className="text-xl">⚠️</span>
                            <div>
                                <p className="font-bold text-sm uppercase tracking-wide opacity-90">Warning</p>
                                <p className="text-sm font-medium">{analysisResult.meta.warning}</p>
                            </div>
                        </div>
                    )}
                    
                    {!analysisResult && !loading && !error && (
                        <div className="border border-dashed border-border rounded-xl h-full min-h-[400px] flex flex-col items-center justify-center text-muted-foreground space-y-4 bg-card/20 hover:bg-card/30 transition-colors">
                            <div className="w-20 h-20 rounded-full bg-secondary/50 flex items-center justify-center text-4xl shadow-inner">
                                ✨
                            </div>
                            <div className="text-center space-y-1">
                                <p className="font-medium text-foreground">Ready to Analyze</p>
                                <p className="text-sm">Enter an issue URL to see agentic insights.</p>
                            </div>
                        </div>
                    )}
                    
                    {(loading || error) && !analysisResult && (
                        <StatusFeed 
                            error={error} 
                            onRetry={() => {
                                setError(null);
                                setLoading(false);
                            }} 
                        />
                    )}

                    {analysisResult && (
                        <Dashboard 
                            analysis={analysisResult.analysis} 
                            meta={analysisResult.meta} 
                            repoUrl={repoUrl}
                            issueNumber={issueNumber}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default Home;
