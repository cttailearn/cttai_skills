/**
 * Stealth Core - Core anti-detection measures
 * Hides automation indicators and randomizes fingerprints
 */

(function() {
    'use strict';

    // 1. Hide navigator.webdriver
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });

    // 2. Canvas fingerprint randomization
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, ...args) {
        const context = this.getContext('2d');
        if (context) {
            const imageData = context.getImageData(0, 0, this.width, this.height);
            for (let i = 0; i < imageData.data.length; i += 4) {
                // Add small random noise to RGB values
                imageData.data[i] += Math.floor(Math.random() * 2);
                imageData.data[i + 1] += Math.floor(Math.random() * 2);
                imageData.data[i + 2] += Math.floor(Math.random() * 2);
            }
            context.putImageData(imageData, 0, 0);
        }
        return originalToDataURL.call(this, type, ...args);
    };

    // 3. WebGL fingerprint randomization
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(param) {
        // Hide SwiftShader renderer
        if (param === 37445) { // UNMASKED_RENDERER_WEBGL
            return 'Intel Iris OpenGL Engine';
        }
        if (param === 37446) { // UNMASKED_VENDOR_WEBGL
            return 'Intel Inc.';
        }
        return getParameter.call(this, param);
    };

    // Also handle WebGL2 context
    if (typeof WebGL2RenderingContext !== 'undefined') {
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Iris OpenGL Engine';
            if (param === 37446) return 'Intel Inc.';
            return getParameter2.call(this, param);
        };
    }

    // 4. AudioContext fingerprint randomization
    const originalCreateDynamicsCompressor = AudioContext.prototype.createDynamicsCompressor;
    AudioContext.prototype.createDynamicsCompressor = function() {
        const compressor = originalCreateDynamicsCompressor.call(this);
        // Add slight random modifications
        const randomOffset = () => (Math.random() - 0.5) * 0.01;
        const originalGetValue = compressor.threshold.getValue.bind(compressor.threshold);
        compressor.threshold.getValue = function() {
            return originalGetValue() + randomOffset();
        };
        return compressor;
    };

    // 5. Remove automation-related properties
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    delete window.__webdriver_evaluate;
    delete window.__selenium_evaluate;
    delete window.__webdriver_script_function;
    delete window.__webdriver_script_func;
    delete window.__webdriver_script_fn;
    delete window.__fxdriver_evaluate;
    delete window.__driver_unwrapped;
    delete window.__webdriver_unwrapped;
    delete window.__debugger_bypass;

    // 6. Override chrome runtime to look normal
    if (window.chrome) {
        window.chrome.runtime = {
            connect: function() {},
            sendMessage: function() {}
        };
    }

    // 7. Randomize screen dimensions slightly
    const originalWidth = screen.width;
    const originalHeight = screen.height;
    Object.defineProperty(screen, 'width', {
        get: () => originalWidth + Math.floor(Math.random() * 10) - 5,
        configurable: true
    });
    Object.defineProperty(screen, 'height', {
        get: () => originalHeight + Math.floor(Math.random() * 10) - 5,
        configurable: true
    });

    // 8. Navigator properties
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' }
        ],
        configurable: true
    });

    console.log('[Stealth] Core anti-detection applied');
})();
