import React from 'react';
import { Button } from "./ui/button";
import { Github, Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";

const Navbar = () => {
    const { theme, setTheme } = useTheme()

    return (
        <nav className="border-b border-border bg-card/50 backdrop-blur-xl sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <img 
                        src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                        alt="GitHub Logo" 
                        className="w-8 h-8 invert dark:invert-0 transition-all" 
                    />
                    <span className="font-bold text-lg tracking-tight">GitHub Issue Analyzer</span>
                </div>
                
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" asChild>
                        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                            Docs
                        </a>
                    </Button>
                    <div className="w-px h-4 bg-border mx-1" />
                    <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground" onClick={() => window.open('https://github.com', '_blank')}>
                         <Github className="w-5 h-5" />
                    </Button>
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        className="text-muted-foreground hover:text-foreground"
                        onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                    >
                        <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                        <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                    </Button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
