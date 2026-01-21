import React from 'react';

const Footer = () => {
    return (
        <footer className="border-t border-border mt-auto bg-card/30">
            <div className="container mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
                <p>
                    Powered by <span className="font-medium text-foreground">Google Gemini 2.0 Flash</span>
                </p>
                <div className="flex items-center gap-4">
                    <p>💡 <span className="font-medium text-foreground">Pro Tip:</span> Use a GITHUB_TOKEN for higher limits.</p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
