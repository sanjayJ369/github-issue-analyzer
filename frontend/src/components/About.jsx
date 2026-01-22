import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Github, Bot, Sparkles, Zap, Brain, Shield } from "lucide-react";

const FeatureCard = ({ icon: Icon, title, description }) => (
    <Card className="bg-card/50 backdrop-blur-sm border-border/50 hover:bg-card/80 transition-colors">
        <CardHeader>
            <Icon className="w-8 h-8 text-primary mb-2" />
            <CardTitle className="text-xl">{title}</CardTitle>
        </CardHeader>
        <CardContent>
            <p className="text-muted-foreground">{description}</p>
        </CardContent>
    </Card>
);

const About = () => {
    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Hero Section */}
            <div className="text-center space-y-4 max-w-3xl mx-auto">
                <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-primary/10 mb-4">
                    <Bot className="w-8 h-8 text-primary" />
                </div>
                <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                    About IssueInsight
                </h1>
                <p className="text-xl text-muted-foreground leading-relaxed">
                    An intelligent agentic tool designed to transform potential GitHub chaos into 
                    structured, actionable engineering insights.
                </p>
            </div>

            {/* Mission Section */}
            <div className="grid md:grid-cols-2 gap-8 items-center">
                <div className="space-y-6">
                    <h2 className="text-3xl font-bold tracking-tight">Our Mission</h2>
                    <p className="text-lg text-muted-foreground">
                        Open source maintenance is hard. IssueInsight aims to reduce the burden on maintainers 
                        by automatically analyzing incoming issues, assessing their impact, and suggesting 
                        proper categorization before a human ever needs to intervene.
                    </p>
                    <div className="flex gap-4">
                        <div className="flex items-center gap-2 text-sm font-medium bg-secondary/50 px-4 py-2 rounded-full">
                            <Sparkles className="w-4 h-4 text-yellow-500" />
                            AI-Powered Analysis
                        </div>
                        <div className="flex items-center gap-2 text-sm font-medium bg-secondary/50 px-4 py-2 rounded-full">
                            <Zap className="w-4 h-4 text-primary" />
                            Real-time Insights
                        </div>
                    </div>
                </div>
                <div className="relative rounded-2xl overflow-hidden border border-border/50 shadow-2xl">
                    <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-transparent opacity-50" />
                    <div className="p-8 bg-card/30 backdrop-blur-xl h-full flex flex-col justify-center items-center text-center space-y-4">
                        <Github className="w-16 h-16 opacity-20" />
                        <p className="font-mono text-sm opacity-50">.github/workflows/issue-insight.yml</p>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-6">
                <FeatureCard 
                    icon={Brain}
                    title="Smart Categorization"
                    description="Automatically determines if an issue is a bug, feature request, or question based on context, not just labels."
                />
                <FeatureCard 
                    icon={Shield}
                    title="Impact Assessment"
                    description="Evaluates the potential severity and user impact of issues to help prioritize critical fixes."
                />
                <FeatureCard 
                    icon={Zap}
                    title="Actionable Steps"
                    description="Provides immediate triage recommendations and suggested labels to keep your repository organized."
                />
            </div>
        </div>
    );
};

export default About;
