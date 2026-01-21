import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { FileText } from "lucide-react";

const SummaryCard = ({ summary }) => {
    return (
        <Card className="border-border/50 shadow-sm">
            <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                    <FileText className="w-5 h-5 text-accent-foreground" />
                    Executive Summary
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="prose prose-sm prose-invert max-w-none text-muted-foreground">
                    <ReactMarkdown>{summary}</ReactMarkdown>
                </div>
            </CardContent>
        </Card>
    );
};

export default SummaryCard;
