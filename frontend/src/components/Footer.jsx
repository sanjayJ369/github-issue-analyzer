import React from 'react';

const Footer = () => {
    return (
        <footer className="border-t border-border mt-auto bg-card/30 backdrop-blur-sm">
            <div className="container mx-auto px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground/80">
                <div className="flex flex-col gap-1 items-center md:items-start">
                    <p className="font-medium text-foreground">GitHub Issue Analyzer</p>
                    <p>© 2026 Powered by Multi-Provider LLMs</p>
                </div>
                
                <div className="flex items-center gap-6">
                    <span className="hover:text-foreground transition-colors cursor-default">
                        React + FastAPI
                    </span>
                    <a href="#" className="hover:text-foreground transition-colors">Documentation</a>
                    <a href="#" className="hover:text-foreground transition-colors">Support</a>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
