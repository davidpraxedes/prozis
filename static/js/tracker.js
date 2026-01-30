// Tracker.js - Session & Time Tracking

(function () {
    const API_BASE = '/api/track';

    // 1. Session & Source Management
    function getSessionId() {
        let sid = localStorage.getItem('site_session_id');
        if (!sid) {
            sid = 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
            localStorage.setItem('site_session_id', sid);
        }
        return sid;
    }

    function getTrafficSource() {
        // 1. Check URL Params (Strongest signal)
        const params = new URLSearchParams(window.location.search);
        if (params.has('fbclid')) return 'Facebook Ads';
        if (params.has('gclid')) return 'Google Ads';
        if (params.has('ttclid')) return 'TikTok Ads';
        if (params.has('utm_source')) return params.get('utm_source');

        // 2. Check Referrer
        const ref = document.referrer;
        if (ref) {
            if (ref.includes('facebook.com')) return 'Facebook Organic';
            if (ref.includes('instagram.com')) return 'Instagram Organic';
            if (ref.includes('google.com')) return 'Google Organic';
            if (ref.includes('tiktok.com')) return 'TikTok Organic';
        }

        // 3. Return stored source or Direct
        return localStorage.getItem('traffic_source') || 'Direct';
    }

    // Capture and Store Source on first visit (or if new campaign params found)
    const currentSource = getTrafficSource();
    if (currentSource !== 'Direct' && currentSource !== localStorage.getItem('traffic_source')) {
        localStorage.setItem('traffic_source', currentSource);
    }
    const finalSource = localStorage.getItem('traffic_source') || 'Direct';

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
                referrer: document.referrer,
                traffic_source: finalSource
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
