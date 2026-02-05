(function () {
    // Exclusion Check: Do NOT run on final payment confirmation pages
    if (window.location.href.includes('payment_mbway') || window.location.href.includes('payment_multibanco')) {
        return;
    }

    const notifications = [
        { name: "Maria S.", action: "resgatou um Kit Sephora", time: "há 2 minutos" },
        { name: "Joana P.", action: "finalizou o pagamento", time: "agora mesmo" },
        { name: "Ana C.", action: "ganhou um prémio", time: "há 5 minutos" },
        { name: "Beatriz M.", action: "resgatou um Kit Sephora", time: "há 1 minuto" },
        { name: "Sofia L.", action: "está a preencher os dados", time: "agora mesmo" },
        { name: "Carolina R.", action: "finalizou o envio", time: "há 30 segundos" },
        { name: "Inês T.", action: "ganhou um Kit Ícones do Luxo", time: "há 10 minutos" },
        { name: "Mariana V.", action: "resgatou um prémio", time: "agora mesmo" },
        { name: "Diana F.", action: "escolheu MB WAY", time: "há 45 segundos" },
        { name: "Lara G.", action: "finalizou o pagamento", time: "há 3 minutos" },
        { name: "Rita N.", action: "recebeu o código de rastreio", time: "há 15 minutos" },
        { name: "Cláudia S.", action: "resgatou um Kit Sephora", time: "há 20 segundos" }
    ];

    // Create Notification Container
    const container = document.createElement('div');
    container.id = 'social-proof-container';
    container.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: #fff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 15px;
        z-index: 9999;
        transform: translateY(150%);
        transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border-left: 4px solid #00b67a;
        max-width: 300px;
        font-family: 'Inter', sans-serif;
    `;

    // Inner HTML Structure
    container.innerHTML = `
        <div style="background: #00b67a; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        </div>
        <div>
            <div id="sp-name" style="font-weight: 700; font-size: 13px; color: #000;"></div>
            <div id="sp-action" style="font-size: 12px; color: #555; margin-top: 2px;"></div>
            <div id="sp-time" style="font-size: 10px; color: #999; margin-top: 4px; font-weight: 500;"></div>
        </div>
        <div style="position: absolute; top: 5px; right: 5px; cursor: pointer; color: #ccc;" onclick="this.parentElement.style.transform='translateY(150%)'">&times;</div>
    `;

    document.body.appendChild(container);

    const nameEl = container.querySelector('#sp-name');
    const actionEl = container.querySelector('#sp-action');
    const timeEl = container.querySelector('#sp-time');

    let index = 0;

    function showNotification() {
        const data = notifications[index];
        nameEl.textContent = data.name;
        actionEl.textContent = data.action;
        timeEl.textContent = data.time;

        // Slide In
        container.style.transform = 'translateY(0)';

        // Slide Out after 4 seconds
        setTimeout(() => {
            container.style.transform = 'translateY(150%)';
        }, 4000);

        // Next index
        index = (index + 1) % notifications.length;
    }

    // Start loop
    // Initial delay 2s, then every 7s
    setTimeout(() => {
        showNotification();
        setInterval(showNotification, 7000);
    }, 2000);

})();
