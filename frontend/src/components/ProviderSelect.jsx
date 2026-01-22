import React, { useEffect } from 'react';
import { ChevronDown, Cpu, Zap, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

/**
 * Get color and label for speed indicator
 */
const getSpeedStyles = (speed, latencyMs) => {
    // Use latency-based coloring if available
    if (latencyMs !== null && latencyMs !== undefined) {
        if (latencyMs < 1000) {
            return { color: 'text-emerald-500', bg: 'bg-emerald-500/10', label: 'Fast' };
        } else if (latencyMs < 3000) {
            return { color: 'text-amber-500', bg: 'bg-amber-500/10', label: 'Medium' };
        } else {
            return { color: 'text-rose-500', bg: 'bg-rose-500/10', label: 'Slow' };
        }
    }
    
    // Fallback to speed label
    switch (speed?.toLowerCase()) {
        case 'fast':
            return { color: 'text-emerald-500', bg: 'bg-emerald-500/10', label: 'Fast' };
        case 'medium':
            return { color: 'text-amber-500', bg: 'bg-amber-500/10', label: 'Medium' };
        case 'slow':
            return { color: 'text-rose-500', bg: 'bg-rose-500/10', label: 'Slow' };
        case 'reasoning':
            return { color: 'text-purple-500', bg: 'bg-purple-500/10', label: 'Reasoning' };
        default:
            return { color: 'text-muted-foreground', bg: 'bg-muted/50', label: 'Standard' };
    }
};

/**
 * Get status indicator props
 */
const getStatusIndicator = (status, isAvailable) => {
    if (isAvailable || status === 'available') {
        return { icon: CheckCircle, color: 'text-emerald-500', tooltip: 'Available' };
    } else if (status === 'rate_limited') {
        return { icon: AlertTriangle, color: 'text-amber-500', tooltip: 'Rate Limited' };
    } else {
        return { icon: null, color: 'text-muted-foreground', tooltip: 'Unavailable' };
    }
};

/**
 * Format latency for display
 */
const formatLatency = (ms) => {
    if (ms === null || ms === undefined) return null;
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
};

/**
 * Provider selection dropdown with latency indicators.
 * Hidden when only 1 provider is available (auto-selection).
 * 
 * @param {Array} providers - List of available providers
 * @param {string} selectedId - Currently selected provider ID
 * @param {function} onChange - Callback when selection changes
 * @param {boolean} loading - Whether providers are being loaded
 */
const ProviderSelect = ({ providers, selectedId, onChange, loading }) => {
    // Log available providers for debugging
    useEffect(() => {
        if (!loading && providers && providers.length > 0) {
            console.log("🤖 Available LLM Providers:", providers);
        }
    }, [providers, loading]);
    
    // Don't show if only 1 provider (auto-select)
    if (!loading && providers.length <= 1) {
        return null;
    }
    
    // Show loading state
    if (loading) {
        return (
            <div className="flex items-center gap-2 text-xs text-muted-foreground animate-pulse">
                <Cpu className="w-3 h-3" />
                Discovering providers...
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
    
    // Filter to only available providers for the dropdown
    const availableProviders = providers.filter(p => p.is_available || p.status === 'available');
    const unavailableProviders = providers.filter(p => !p.is_available && p.status !== 'available');
    
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
                    {/* Available providers */}
                    {availableProviders.map((provider) => {
                        const speedStyles = getSpeedStyles(provider.speed, provider.latency_ms);
                        const latencyStr = formatLatency(provider.latency_ms);
                        
                        return (
                            <option 
                                key={provider.id} 
                                value={provider.id}
                            >
                                {provider.label} [{speedStyles.label}]{latencyStr ? ` (${latencyStr})` : ''}
                            </option>
                        );
                    })}
                    
                    {/* Unavailable providers (disabled) */}
                    {unavailableProviders.length > 0 && (
                        <optgroup label="Unavailable">
                            {unavailableProviders.map((provider) => (
                                <option 
                                    key={provider.id} 
                                    value={provider.id}
                                    disabled
                                >
                                    {provider.label} ({provider.status === 'rate_limited' ? 'Rate Limited' : 'Unavailable'})
                                </option>
                            ))}
                        </optgroup>
                    )}
                </select>
                <ChevronDown className="w-4 h-4 absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            </div>
            
            {/* Speed/Latency indicator for selected provider */}
            {selectedId && (() => {
                const selected = providers.find(p => p.id === selectedId);
                if (!selected) return null;
                
                const speedStyles = getSpeedStyles(selected.speed, selected.latency_ms);
                const statusInfo = getStatusIndicator(selected.status, selected.is_available);
                const latencyStr = formatLatency(selected.latency_ms);
                
                return (
                    <div className="flex items-center gap-3 text-xs">
                        {/* Status indicator */}
                        <span className={`flex items-center gap-1 ${statusInfo.color}`}>
                            {statusInfo.icon && <statusInfo.icon className="w-3 h-3" />}
                            {statusInfo.tooltip}
                        </span>
                        
                        {/* Speed indicator */}
                        <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full ${speedStyles.bg} ${speedStyles.color}`}>
                            <Clock className="w-3 h-3" />
                            {speedStyles.label}
                            {latencyStr && <span className="opacity-75">({latencyStr})</span>}
                        </span>
                    </div>
                );
            })()}
        </div>
    );
};

export default ProviderSelect;
