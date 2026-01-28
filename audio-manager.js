/**
 * AudioManager - Singleton for managing Web Audio API Context
 * Solves iOS unlock issues by sharing a single context instance.
 */
class AudioManager {
    static _context = null;
    static _isUnlocked = false;

    // Get the shared AudioContext (Lazy Init)
    static getContext() {
        if (!this._context) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this._context = new AudioContext();
            }
        }
        return this._context;
    }

    // Unlock method - Must be called from a User Gesture (Click/TouchEnd)
    static async unlock() {
        const ctx = this.getContext();
        if (!ctx) return false;

        if (ctx.state === 'suspended') {
            try {
                await ctx.resume();
            } catch (e) {
                console.error("Audio resume failed:", e);
            }
        }

        // Play silent buffer to force iOS audio stack validation
        const buffer = ctx.createBuffer(1, 1, 22050);
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.start(0);

        this._isUnlocked = true;

        // Persist state for session
        localStorage.setItem('audioUnlocked', 'true');
        console.log("🔊 AudioManager: Context Unlocked & Resumed");

        return true;
    }

    static isUnlocked() {
        return this._isUnlocked || (this._context && this._context.state === 'running');
    }
}

// Expose globally
window.AudioManager = AudioManager;
