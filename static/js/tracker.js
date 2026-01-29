// Tracker.js - Session & Time Tracking

(function () {
    const API_BASE = '/api/track';

    // 1. Session Management
    function getSessionId() {
        let sid = localStorage.getItem('site_session_id');
        if (!sid) {
            sid = 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
            localStorage.setItem('site_session_id', sid);
        }
        return sid;
    }

    const sessionId = getSessionId();
    let startTime = Date.now();
    let path = window.location.pathname;

    // 2. Initialize Session / Page View
    function initSession() {
        fetch(`${API_BASE}/init`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                path: path,
                referrer: document.referrer
            })
        }).catch(err => console.error("Tracker Init Error:", err));
    }

    // 3. Heartbeat (Time Tracking)
    function sendHeartbeat() {
        const elapsed = (Date.now() - startTime) / 1000;

        // Use navigator.sendBeacon for reliability on page unload
        const data = new Blob([JSON.stringify({
            session_id: sessionId,
            path: path,
            duration: elapsed
        })], { type: 'application/json' });

        navigator.sendBeacon(`${API_BASE}/heartbeat`, data);
    }

    // Initialize
    initSession();

    // Send heartbeat every 5 seconds
    setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        fetch(`${API_BASE}/heartbeat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }, // keepalive is better but standard fetch works for interval
            keepalive: true,
            body: JSON.stringify({
                session_id: sessionId,
                path: path,
                duration: elapsed
            })
        }).catch(e => { });
    }, 5000);

    // Send final heartbeat on leave
    document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === 'hidden') {
            sendHeartbeat();
        }
    });

})();
