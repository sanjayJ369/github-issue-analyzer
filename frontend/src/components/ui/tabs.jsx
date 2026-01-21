import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from "../../lib/utils";

export const Tabs = ({ tabs }) => {
  const [selectedTab, setSelectedTab] = useState(tabs[0]);

  return (
    <div className="w-full">
      <div className="flex space-x-1 rounded-xl bg-secondary/50 p-1 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.label}
            onClick={() => setSelectedTab(tab)}
            className={cn(
              "relative rounded-lg px-3 py-1.5 text-sm font-medium outline-none transition-colors",
              "hover:text-primary focus:text-primary",
              tab.label === selectedTab.label ? "text-primary-foreground" : "text-muted-foreground"
            )}
          >
            {tab.label === selectedTab.label && (
              <motion.div
                layoutId="active-pill"
                className="absolute inset-0 bg-background shadow-sm rounded-lg"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                style={{ borderRadius: 8 }}
              />
            )}
            <span className="relative z-10">{tab.label}</span>
          </button>
        ))}
      </div>
      <div className="mt-2">
        <AnimatePresence mode='wait'>
          <motion.div
            key={selectedTab.label}
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -10, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {selectedTab.content}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};
