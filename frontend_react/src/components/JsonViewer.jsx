import React from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import json from 'react-syntax-highlighter/dist/esm/languages/hljs/json';
import { atomOneDark, docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Button } from "./ui/button";
import { Copy, Code, Maximize2 } from "lucide-react";
import { toast } from "sonner";
import { useTheme } from "./theme-provider";

SyntaxHighlighter.registerLanguage('json', json);

const JsonViewer = ({ data }) => {
    const { theme } = useTheme();
    
    // Determine effective theme (handle "system" if needed, but for now simple check)
    // The ThemeProvider sets a "dark" or "light" class on root, but 'theme' state might be 'system'.
    // However, for this component, we can just check if 'theme' state is dark, or rely on a simple heuristic.
    // Better: let's assume 'dark' if theme is 'dark'. 'system' might be tricky without a hook to get resolved theme.
    // For MVP transparency: default to dark if not explicitly light.
    const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2));
        toast.success("Copied JSON to clipboard");
    };

    return (
        <Card className="border-border/50 shadow-sm flex flex-col h-full max-h-[600px]">
            <CardHeader className="flex flex-row items-center justify-between pb-2 bg-secondary/5 border-b border-border/40">
                <div className="space-y-1">
                    <CardTitle className="text-sm uppercase tracking-wider flex items-center gap-2 text-muted-foreground">
                        <Code className="w-4 h-4" />
                        Structured Data
                    </CardTitle>
                </div>
                <Button variant="ghost" size="sm" onClick={handleCopy} className="h-8 gap-2 text-xs hover:bg-secondary/10">
                    <Copy className="w-3.5 h-3.5" />
                    Copy
                </Button>
            </CardHeader>
            <CardContent className="flex-1 p-0 overflow-hidden relative group">
                {/* Scrollable container */}
                <div className="h-full overflow-auto custom-scrollbar">
                    <SyntaxHighlighter 
                        language="json" 
                        style={isDark ? atomOneDark : docco}
                        customStyle={{ 
                            margin: 0, 
                            padding: '1rem', 
                            backgroundColor: 'transparent', // Let parent bg show through
                            fontSize: '0.8rem',
                            minHeight: '100%',
                            lineHeight: '1.4'
                        }}
                        showLineNumbers={true}
                        lineNumberStyle={{ 
                            minWidth: "2em", 
                            paddingRight: "1em", 
                            color: isDark ? "#454c59" : "#cbd5e1", 
                            textAlign: "right" 
                        }}
                    >
                        {JSON.stringify(data, null, 2)}
                    </SyntaxHighlighter>
                </div>
                
                {/* Fade overlay at bottom - dynamic gradient based on theme?? 
                    Actually, transparent bg solves most issues, but the overlay needs to match card bg.
                    We can use standard tailwind bg-gradient-to-t from-background
                */}
                <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-card to-transparent pointer-events-none opacity-50" />
            </CardContent>
        </Card>
    );
};

export default JsonViewer;
