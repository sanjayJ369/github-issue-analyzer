import React from 'react';
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Gauge, Tag, AlertTriangle, Check, Info } from "lucide-react";

const ClassificationCard = ({ type, priorityScore }) => {
    
    // Parse Priority
    const pVal = parseInt(priorityScore.split(" - ")[0]);
    let pColor = "bg-blue-500/10 text-blue-500 border-blue-500/20";
    let pIcon = <Info className="w-5 h-5" />;
    let pLabel = "Low";
    
    if (pVal >= 5) {
        pColor = "bg-red-500/10 text-red-500 border-red-500/20";
        pIcon = <AlertTriangle className="w-5 h-5" />;
        pLabel = "Critical";
    } else if (pVal === 4) {
        pColor = "bg-orange-500/10 text-orange-500 border-orange-500/20";
        pIcon = <AlertTriangle className="w-5 h-5" />;
        pLabel = "High";
    } else if (pVal === 3) {
        pColor = "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
        pIcon = <Gauge className="w-5 h-5" />;
        pLabel = "Medium";
    }

    // Parse Type
    // Map common types to colors if needed, default to slate
 const tColor = "bg-slate-500/10 text-slate-400 border-slate-500/20";

    return (
        <Card className="border-border/50 shadow-sm overflow-hidden">
             {/* Status Header Block */}
            <div className={`p-4 border-b border-border/50 flex items-center justify-between ${pColor} bg-opacity-5 transition-colors duration-300`}>
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${pColor} bg-opacity-20`}>
                        {pIcon}
                    </div>
                    <div>
                        <div className="text-[10px] uppercase tracking-wider font-bold opacity-70">Priority</div>
                        <div className="font-bold text-lg leading-none">{pLabel}</div>
                    </div>
                </div>
                <div className="text-2xl font-bold opacity-40">{pVal}/5</div>
            </div>

            <CardContent className="p-4 space-y-4">
                 <div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold mb-2">Issue Type</div>
                    <div className="flex items-start gap-3 p-3 rounded-lg border border-border/50 bg-secondary/20">
                        <Tag className="w-4 h-4 mt-0.5 text-muted-foreground" />
                        <div>
                            <span className="font-medium text-foreground block capitalize">{type}</span>
                        </div>
                    </div>
                </div>
                
                 <div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold mb-2">Justification</div>
                    <div className="text-sm bg-secondary/10 p-3 rounded-lg border border-border/40 leading-relaxed italic text-muted-foreground">
                        "{priorityScore.split(" - ")[1] || priorityScore}"
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default ClassificationCard;
