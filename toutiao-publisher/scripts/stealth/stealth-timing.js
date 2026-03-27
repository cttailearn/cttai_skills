/**
 * Stealth Timing - Time API obfuscation
 * Randomizes Performance API and timing measurements
 */

(function() {
    'use strict';

    // Timing variance configuration
    const TIMING_CONFIG = {
        variancePercent: 0.05,   // 5% variance in timing values
        driftMax: 50,             // Max milliseconds of timing drift
        initialDrift: 0           // Initial random drift
    };

    // Generate random drift
    let timingDrift = Math.floor(Math.random() * TIMING_CONFIG.driftMax * 2) - TIMING_CONFIG.driftMax;

    /**
     * Add variance to timing value
     */
    function addVariance(value, variancePercent) {
        const variance = value * variancePercent;
        return value + (Math.random() - 0.5) * 2 * variance + timingDrift;
    }

    // 1. Override Performance timing
    const originalPerformance = window.performance;

    if (originalPerformance && originalPerformance.timing) {
        const timingProperties = [
            'navigationStart',
            'unloadEventStart',
            'unloadEventEnd',
            'redirectStart',
            'redirectEnd',
            'fetchStart',
            'domainLookupStart',
            'domainLookupEnd',
            'connectStart',
            'connectEnd',
            'secureConnectionStart',
            'requestStart',
            'responseStart',
            'responseEnd',
            'domLoading',
            'domInteractive',
            'domContentLoadedEventStart',
            'domContentLoadedEventEnd',
            'domComplete',
            'loadEventStart',
            'loadEventEnd'
        ];

        const originalTiming = {};
        timingProperties.forEach(prop => {
            originalTiming[prop] = originalPerformance.timing[prop];
        });

        Object.defineProperty(performance, 'timing', {
            get: function() {
                const timing = {};
                timingProperties.forEach(prop => {
                    const originalValue = originalTiming[prop];
                    if (originalValue && originalValue > 0) {
                        timing[prop] = Math.round(addVariance(originalValue, TIMING_CONFIG.variancePercent));
                    } else {
                        timing[prop] = originalValue;
                    }
                });
                return timing;
            },
            configurable: true
        });
    }

    // 2. Override Performance.now()
    const originalNow = performance.now.bind(performance);
    let nowDrift = 0;

    Object.defineProperty(performance, 'now', {
        get: function() {
            return function() {
                const originalValue = originalNow();
                const variance = TIMING_CONFIG.driftMax * TIMING_CONFIG.variancePercent;
                return originalValue + (Math.random() - 0.5) * variance * 2 + nowDrift;
            };
        },
        configurable: true
    });

    // 3. Override Date.now() subtly
    const originalDateNow = Date.now;
    Object.defineProperty(Date, 'now', {
        get: function() {
            return function() {
                return originalDateNow() + timingDrift;
            };
        },
        configurable: true
    });

    // 4. Override requestAnimationFrame timing
    const originalRAF = window.requestAnimationFrame;
    window.requestAnimationFrame = function(callback) {
        // Add slight delay variance to RAF callbacks
        const delay = (Math.random() - 0.5) * 2;
        return originalRAF.call(window, function(time) {
            callback(time + delay);
        });
    };

    // 5. Override setTimeout to add small variance
    const originalSetTimeout = window.setTimeout;
    window.setTimeout = function(func, delay, ...args) {
        const variance = delay * TIMING_CONFIG.variancePercent;
        const actualDelay = delay + (Math.random() - 0.5) * variance;
        return originalSetTimeout.call(window, func, Math.max(0, actualDelay), ...args);
    };

    // 6. Override setInterval similarly
    const originalSetInterval = window.setInterval;
    window.setInterval = function(func, delay, ...args) {
        const variance = delay * TIMING_CONFIG.variancePercent;
        const actualDelay = delay + (Math.random() - 0.5) * variance;
        return originalSetInterval.call(window, func, Math.max(1, actualDelay), ...args);
    };

    // 7. Add random jitter to Performance entries
    if (originalPerformance && originalPerformance.getEntries) {
        const originalGetEntries = performance.getEntries.bind(performance);
        Object.defineProperty(performance, 'getEntries', {
            get: function() {
                return function() {
                    const entries = originalGetEntries();
                    return entries.map(entry => {
                        const newEntry = {};
                        for (let key in entry) {
                            if (typeof entry[key] === 'number') {
                                newEntry[key] = addVariance(entry[key], TIMING_CONFIG.variancePercent);
                            } else {
                                newEntry[key] = entry[key];
                            }
                        }
                        return newEntry;
                    });
                };
            },
            configurable: true
        });
    }

    console.log('[Stealth] Timing obfuscation applied');
})();
