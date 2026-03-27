/**
 * Stealth Scroll - Human-like scrolling behavior
 * Implements smooth scrolling with acceleration/deceleration
 */

(function() {
    'use strict';

    // Scroll configuration
    const SCROLL_CONFIG = {
        baseSpeed: 800,          // Base pixels per second
        speedVariance: 0.3,       // Variance percentage
        accelerationTime: 200,    // Time to reach full speed (ms)
        decelerationDistance: 100, // Distance before target to start slowing
        pauseProbability: 0.15,  // Probability of pause during scroll
        pauseDuration: { min: 100, max: 400 }
    };

    /**
     * Easing function for smooth acceleration/deceleration
     */
    function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    /**
     * Calculate scroll speed based on progress
     */
    function getScrollSpeed(progress, totalDistance) {
        const baseSpeed = SCROLL_CONFIG.baseSpeed * (1 + (Math.random() - 0.5) * SCROLL_CONFIG.speedVariance);

        // Slow down near target
        const distanceToEnd = totalDistance * (1 - progress);
        let slowDownFactor = 1;
        if (distanceToEnd < SCROLL_CONFIG.decelerationDistance) {
            slowDownFactor = Math.max(0.3, distanceToEnd / SCROLL_CONFIG.decelerationDistance);
        }

        // Slow at start
        let speedUpFactor = 1;
        if (progress < 0.1) {
            speedUpFactor = Math.min(1, progress / 0.1);
        }

        return baseSpeed * slowDownFactor * speedUpFactor;
    }

    /**
     * Perform human-like smooth scroll
     */
    window.__stealthScrollTo = function(targetY, duration, callback) {
        const startY = window.scrollY || window.pageYOffset;
        const totalDistance = targetY - startY;

        if (Math.abs(totalDistance) < 5) {
            window.scrollTo(targetY, targetY);
            if (callback) callback();
            return;
        }

        const startTime = performance.now();
        let lastPauseTime = 0;

        function scrollStep(currentTime) {
            const elapsed = currentTime - startTime - lastPauseTime;
            const progress = Math.min(1, elapsed / duration);

            // Random pause
            if (Math.random() < SCROLL_CONFIG.pauseProbability && progress < 0.9) {
                const pauseDuration = SCROLL_CONFIG.pauseDuration.min +
                    Math.random() * (SCROLL_CONFIG.pauseDuration.max - SCROLL_CONFIG.pauseDuration.min);
                lastPauseTime += pauseDuration;
                setTimeout(() => scrollStep(performance.now()), pauseDuration);
                return;
            }

            const easedProgress = easeInOutQuad(progress);
            const currentY = startY + totalDistance * easedProgress;

            window.scrollTo(Math.round(currentX || 0), Math.round(currentY));

            if (progress < 1) {
                requestAnimationFrame(scrollStep);
            } else {
                window.scrollTo(targetY, targetY);
                if (callback) callback();
            }
        }

        requestAnimationFrame(scrollStep);
    };

    /**
     * Scroll by a certain amount with human-like behavior
     */
    window.__stealthScrollBy = function(deltaY, callback) {
        const targetY = (window.scrollY || window.pageYOffset) + deltaY;
        const duration = Math.abs(deltaY) / SCROLL_CONFIG.baseSpeed * 1000;
        window.__stealthScrollTo(targetY, Math.max(200, Math.min(duration, 2000)), callback);
    };

    /**
     * Override default scroll behavior
     */
    const originalScrollTo = window.scrollTo.bind(window);
    window.scrollTo = function(x, y) {
        if (typeof x === 'object' && y === undefined) {
            // scrollTo({top: y, behavior: 'smooth'})
            const options = x;
            if (options.behavior === 'smooth') {
                window.__stealthScrollTo(options.top, 500);
            } else {
                originalScrollTo(x, y);
            }
        } else {
            // Direct scroll
            originalScrollTo(x, y);
        }
    };

    // Override WheelEvent to add variance
    const originalDispatchEvent = EventTarget.prototype.dispatchEvent;
    EventTarget.prototype.dispatchEvent = function(event) {
        if (event instanceof WheelEvent) {
            // Add slight delta variance
            const deltaMultiplier = 1 + (Math.random() - 0.5) * 0.1;
            Object.defineProperty(event, 'deltaY', {
                get: () => event._deltaY * deltaMultiplier,
                set: (val) => { event._deltaY = val; }
            });
        }
        return originalDispatchEvent.call(this, event);
    };

    console.log('[Stealth] Scroll simulation module loaded');
})();
