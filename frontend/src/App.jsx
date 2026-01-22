import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import { ThemeProvider } from "./components/theme-provider";
import Home from './components/Home';
import About from './components/About';

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <div className="min-h-screen bg-background flex flex-col font-sans text-foreground">
          <Navbar />
          
          <main className="flex-1 container mx-auto px-4 py-8 md:py-12">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>

          <Footer />
          <Toaster theme="system" position="bottom-right" />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
