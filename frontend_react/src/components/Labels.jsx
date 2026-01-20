import React from 'react';
import { Badge } from "./ui/badge";

const Labels = ({ labels }) => {
    return (
        <div className="mt-6">
            <h4 className="text-sm font-semibold text-muted-foreground mb-3">SUGGESTED LABELS</h4>
            <div className="flex flex-wrap gap-2">
                {labels.map((label, index) => (
                    <Badge key={index} variant="secondary" className="bg-secondary/50 hover:bg-secondary/70 transition-colors">
                        {label}
                    </Badge>
                ))}
            </div>
        </div>
    );
};

export default Labels;
