import React from 'react';
import { ChevronDown, Cpu, Zap } from 'lucide-react';

/**
 * Provider selection dropdown.
 * Hidden when only 1 provider is available (auto-selection).
 * 
 * @param {Array} providers - List of available providers
 * @param {string} selectedId - Currently selected provider ID
 * @param {function} onChange - Callback when selection changes
 * @param {boolean} loading - Whether providers are being loaded
 */
const ProviderSelect = ({ providers, selectedId, onChange, loading }) => {
    // Don't show if only 1 provider (auto-select)
    if (!loading && providers.length <= 1) {
        return null;
    }
    
    // Show loading state
    if (loading) {
        return (
            <div className="flex items-center gap-2 text-xs text-muted-foreground animate-pulse">
                <Cpu className="w-3 h-3" />
                Loading providers...
            </div>
        );
    }
    
    // Show error if no providers
    if (providers.length === 0) {
        return (
            <div className="text-xs text-destructive flex items-center gap-1">
                <span>⚠️</span>
                No LLM providers configured
            </div>
        );
    }
    
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium leading-none flex items-center gap-2">
                <Zap className="w-3.5 h-3.5 text-primary" />
                LLM Provider
            </label>
            <div className="relative">
                <select
                    value={selectedId || ''}
                    onChange={(e) => onChange(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring appearance-none cursor-pointer pr-8"
                >
                    {providers.map((provider) => (
                        <option key={provider.id} value={provider.id}>
                            {provider.label} ({provider.model})
                        </option>
                    ))}
                </select>
                <ChevronDown className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            </div>
        </div>
    );
};

export default ProviderSelect;
