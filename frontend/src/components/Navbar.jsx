import { Button } from "./ui/button";
import { Github, Moon, Sun, Bot, Sparkles } from "lucide-react";
import { useTheme } from "./theme-provider";

const Navbar = () => {
    const { theme, setTheme } = useTheme()

    return (
        <nav className="border-b border-border bg-card/50 backdrop-blur-xl sticky top-0 z-50">
            <div className="container mx-auto px-3 sm:px-4 h-14 sm:h-16 flex items-center justify-between">
                <div className="flex items-center gap-2 sm:gap-3 group">
                    <div className="relative flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors">
                        <Bot className="w-5 h-5 sm:w-6 sm:h-6 text-primary transition-transform group-hover:scale-110" />
                        <Sparkles className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
                    </div>
                    <div>
                        <span className="font-bold text-base sm:text-lg tracking-tight block leading-none">IssueInsight</span>
                        <span className="hidden sm:block text-[10px] uppercase tracking-widest text-muted-foreground font-medium">Agentic Analyzer</span>
                    </div>
                </div>
                
                <div className="flex items-center gap-1 sm:gap-2">
                    <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
                        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                            Docs
                        </a>
                    </Button>
                    <div className="hidden sm:block w-px h-4 bg-border mx-1" />
                    <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground w-8 h-8 sm:w-9 sm:h-9" onClick={() => window.open('https://github.com/sanjayJ369/github-issue-analyzer', '_blank')}>
                         <Github className="w-4 h-4 sm:w-5 sm:h-5" />
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
