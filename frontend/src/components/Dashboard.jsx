import React, { useState } from 'react';
import SummaryCard from './SummaryCard';
import ImpactCard from './ImpactCard';
import JsonViewer from './JsonViewer';
import ClassificationCard from './ClassificationCard';
import Labels from './Labels';
import { Card, CardContent } from "./ui/card";
import { ExternalLink, MessageSquare, Database } from "lucide-react";

const Dashboard = ({ analysis, meta, repoUrl, issueNumber }) => {
    // Layout: Balanced 2-Column (50/50)
    // Left: Human-Readable Insights (Summary, Impact, Classification)
    // Right: Engineering Data (JSON)

    return (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Meta Header */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground mb-6 uppercase tracking-wider font-semibold opacity-70">
                <div className="flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5" />
                    <span>Processed {meta.fetched_comments_count} Comments</span>
                </div>
                {meta.cached && (
                    <div className="flex items-center gap-1.5 text-blue-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                        <span>Cached Result</span>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-start">
                
                {/* Left Column: Human-Readable Insights */}
                <div className="space-y-4 lg:space-y-6">
                    <section>
                         <h3 className="text-sm font-bold mb-3 lg:mb-4 uppercase tracking-wider text-muted-foreground">
                            Classification
                        </h3>
                        <ClassificationCard type={analysis.type} priorityScore={analysis.priority_score} />
                    </section>

                    <section>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 lg:mb-4">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                                Executive Summary
                            </h3>
                            <Labels labels={analysis.suggested_labels} />
                        </div>
                        <div className="space-y-4 lg:space-y-6">
                            <SummaryCard summary={analysis.summary} />
                            <ImpactCard impact={analysis.potential_impact} />
                        </div>
                     </section>
                     
                     <section className="pt-4 border-t border-border/40">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-card border border-border/50 p-3 lg:p-4 rounded-lg">
                            <div>
                                <h4 className="font-semibold text-sm">Original Source</h4>
                                <p className="text-xs text-muted-foreground mt-1">View the full discussion on GitHub</p>
                            </div>
                            <a 
                                href={`${repoUrl}/issues/${issueNumber}`} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-secondary text-secondary-foreground hover:bg-secondary/80 h-9 px-4 py-2 gap-2 w-full sm:w-auto"
                            >
                                <ExternalLink className="w-4 h-4" />
                                Open
                            </a>
                        </div>
                     </section>
                </div>

                {/* Right Column: Engineering Data (Sticky) */}
                <div className="space-y-6 lg:sticky lg:top-24">
                     <section className="h-[400px] lg:h-[calc(100vh-12rem)] lg:min-h-[600px]">
                         <div className="flex items-center justify-between mb-3 lg:mb-4">
                            <h3 className="text-lg lg:text-xl font-bold flex items-center gap-2">
                                Analysis Payload
                            </h3>
                         </div>
                        <JsonViewer data={analysis} />
                    </section>
                </div>

            </div>
        </div>
    );
};

export default Dashboard;
