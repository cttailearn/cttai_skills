/**
 * Stealth Mouse - Realistic mouse movement simulation
 * Uses Bezier curves for natural-looking mouse trajectories
 */

(function() {
    'use strict';

    // Mouse movement configuration
    const MOUSE_CONFIG = {
        minSteps: 8,
        maxSteps: 25,
        baseSpeed: 0.3,
        speedVariance: 0.2,
        pauseProbability: 0.1,
        pauseDuration: { min: 50, max: 200 }
    };

    /**
     * Generate a cubic Bezier curve point
     */
    function cubicBezier(t, p0, p1, p2, p3) {
        const t2 = t * t;
        const t3 = t2 * t;
        const mt = 1 - t;
        const mt2 = mt * mt;
        const mt3 = mt2 * mt;
        return mt3 * p0 + 3 * mt2 * t * p1 + 3 * mt * t2 * p2 + t3 * p3;
    }

    /**
     * Calculate distance between two points
     */
    function distance(p1, p2) {
        return Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
    }

    /**
     * Generate control points for Bezier curve
     * Creates natural-looking mouse path
     */
    function generateControlPoints(start, end) {
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        const dist = distance(start, end);

        // Control point offset based on distance
        const offsetMagnitude = dist * (0.2 + Math.random() * 0.3);

        // Random direction perpendicular to movement
        const perpX = -dy / dist || 0;
        const perpY = dx / dist || 0;
        const sign = Math.random() > 0.5 ? 1 : -1;

        const offsetX = perpX * offsetMagnitude * sign;
        const offsetY = perpY * offsetMagnitude * sign;

        return {
            p0: start,
            p1: {
                x: start.x + dx * 0.33 + offsetX,
                y: start.y + dy * 0.33 + offsetY
            },
            p2: {
                x: start.x + dx * 0.66 + offsetX,
                y: start.y + dy * 0.66 + offsetY
            },
            p3: end
        };
    }

    /**
     * Move mouse with human-like trajectory
     */
    window.__stealthMouseMove = function(pageMouse, targetX, targetY, callback) {
        const startX = pageMouse._lastX || 0;
        const startY = pageMouse._lastY || 0;

        // If no last position, start at current mouse position
        if (!pageMouse._lastX) {
            pageMouse._lastX = startX;
            pageMouse._lastY = startY;
        }

        const start = { x: startX, y: startY };
        const end = { x: targetX, y: targetY };
        const dist = distance(start, end);

        if (dist < 5) {
            // Small movement - just move directly
            pageMouse.move(targetX, targetY);
            pageMouse._lastX = targetX;
            pageMouse._lastY = targetY;
            if (callback) callback();
            return;
        }

        // Calculate number of steps based on distance
        const numSteps = Math.min(
            MOUSE_CONFIG.maxSteps,
            Math.max(MOUSE_CONFIG.minSteps, Math.floor(dist / 20))
        );

        // Generate Bezier control points
        const controlPoints = generateControlPoints(start, end);

        // Calculate timing for each step
        const baseTime = dist / 1000 * MOUSE_CONFIG.baseSpeed;
        const stepDelay = baseTime / numSteps;

        let currentStep = 0;

        function moveNextStep() {
            if (currentStep <= numSteps) {
                const t = currentStep / numSteps;
                const x = cubicBezier(t, controlPoints.p0.x, controlPoints.p1.x,
                                       controlPoints.p2.x, controlPoints.p3.x);
                const y = cubicBezier(t, controlPoints.p0.y, controlPoints.p1.y,
                                       controlPoints.p2.y, controlPoints.p3.y);

                pageMouse.move(Math.round(x), Math.round(y));
                pageMouse._lastX = Math.round(x);
                pageMouse._lastY = Math.round(y);

                currentStep++;

                // Add random pause
                let delay = stepDelay * 1000;
                if (Math.random() < MOUSE_CONFIG.pauseProbability) {
                    delay += MOUSE_CONFIG.pauseDuration.min +
                             Math.random() * (MOUSE_CONFIG.pauseDuration.max -
                             MOUSE_CONFIG.pauseDuration.min);
                }

                setTimeout(moveNextStep, delay + (Math.random() - 0.5) * stepDelay * 500);
            } else {
                pageMouse._lastX = targetX;
                pageMouse._lastY = targetY;
                if (callback) callback();
            }
        }

        moveNextStep();
    };

    // Override page.mouse with stealth version
    const originalMouse = null;

    console.log('[Stealth] Mouse trajectory module loaded');
})();
