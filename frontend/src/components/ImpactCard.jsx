import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Zap } from "lucide-react";

const ImpactCard = ({ impact }) => {
    return (
        <Card className="border-border/50 shadow-sm mt-6">
            <CardHeader className="pb-3">
                 <CardTitle className="text-lg flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    Impact Assessment
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="prose prose-sm prose-invert max-w-none text-muted-foreground">
                    <ReactMarkdown>{impact}</ReactMarkdown>
                </div>
            </CardContent>
        </Card>
    );
};

export default ImpactCard;
