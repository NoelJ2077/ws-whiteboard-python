let clientId = localStorage.getItem("clientId") || 
    (localStorage.setItem("clientId", crypto.randomUUID().replace(/-/g, "").slice(0,24)), localStorage.getItem("clientId"));

// DOM Init
document.getElementById('clientId').textContent = clientId;
document.getElementById('browser').textContent = navigator.userAgent;

// create ws
const ws = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
window.ws = ws;
const statusDiv = document.getElementById('backend-status');

ws.onopen = () => { statusDiv.textContent = 'Backend Connected'; statusDiv.style.backgroundColor = 'green'; };
ws.onerror = ws.onclose = () => { 
    statusDiv.textContent = 'Backend error'; 
    statusDiv.style.backgroundColor = 'red'; 
    statusDiv.style.fontWeight = 'bold'; 
    statusDiv.style.fontSize = '110%'; 
};

// msg types (for better GUI)
const msgTypes = {
    personal:       ["[Personal]", "#2e8b57"],
    p2p:            ["[P2P]", "#1e90ff"],
    group:          ["[Group]", "#ff8c00"],
    broadcast:      ["[Broadcast]", "#9370db"],
    set_email:      ["[setMail]", "#a319daff"],
    servercmd:      ["[ServerCMD]", "#20b2aa"],
    clientcmd:      ["[ClientCMD]", "#ffd700"],
    serveradmincmd: ["[ServerAdminCMD]", "#3db93dff"],
    server_infocmd: ["[Server-InfoCMD]", "#008b8b"],
    error:          ["[Error]", "#c73838"]
};

// create log
const log = (container, text, color = null) => {
    const li = document.createElement('li');
    li.textContent = text;
    if (color) li.style.color = color;
    container.appendChild(li);
    container.scrollTop = container.scrollHeight;
};

// ws receive from backend 
ws.onmessage = event => {
    const container = document.getElementById('messages');
    let data;
    try {
        data = JSON.parse(event.data);
    } catch(e) {
        console.warn("Non-JSON WS message ignored: ", event.data);
        return;
    }
    
    if (data.type === "admin_status") {
        const newAdmin = data.curr_admin;
        localStorage.setItem("currAdmin", newAdmin);
        document.getElementById("curr_admin").textContent = newAdmin;
        return;
    }
    
    if (data.type === "servercmd" && data.message?.includes("E-Mail gesetzt")) {
        const email = data.message.match(/[\w.-]+@[\w.-]+\.\w+/);
        email && window.aliasManager?.confirmEmailSuccess(email[0]);
    }

    // START (Task 2) -> die neuen befehle sind Speziell z.b. bei @serveradmin ist das input direkt die message, es braucht somit kein Funktionsname extra im inputfeld. 
    // Bei @server-info wird ein objekt erwartet. 
    if (data.type === "serveradmincmd") {
        log(document.getElementById('msgtoadminonly'), data.message, msgTypes.serveradmincmd[1]);
        return;
    }
    if (data.type === "server_infocmd") {
        const li = document.createElement('li');
        li.style.cssText = "border:1px solid #008b8b;border-radius:6px;background:#e0f7f7;color:#008b8b;padding:8px;";
        
        if (typeof data.message === "object") {
            const start = new Date(data.message.start_time.split(".")[0] + "Z")
                .toLocaleString('de-CH', {day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false});
            li.innerHTML = `<strong>[Server-InfoCMD]</strong><br>
                <div><strong>Clients:</strong> ${data.message.clients}</div>
                <div><strong>Start:</strong> ${start}</div>
                <div><strong>Uptime:</strong> ${data.message.uptime}</div>
                <div><strong>Admin:</strong> ${data.message.admin}</div>`;
        } else {
            li.textContent = `[Server-InfoCMD]: ${data.message}`;
        }
        container.appendChild(li);
        container.scrollTop = container.scrollHeight;
        return;
    }
    // END (Task 2)

    // stdandard: (@Server, @Client)
    const [label, color] = msgTypes[data.type] || ["[Unknown]", null];
    log(container, `${label} ${data.message}`, color);
};

// Send Message
function sendMessage() {
    const input = document.getElementById('msgInput');
    const type = document.getElementById('msgTypeSelect')?.value || "Nonecmd";
    let msg = input?.value.trim();
    if (!msg || !input) return;

    const payload = { type, message: msg };

    // Optional IDs
    if (type === "group") payload.group_id = document.getElementById('groupInput')?.value.trim() || "default_group";
    if (type === "p2p") payload.client_id = document.getElementById('clientInput')?.value.trim();
    // START (Task 2) -> Funktion überarbeitet und neue inputmöglichkeiten gemäss Auftrag hinzugefügt. 
    // Command Prefixes
    const prefixes = { servercmd: "@server", clientcmd: "@client", serveradmincmd: "@serveradmin", server_infocmd: "@server_info" };
    const prefix = prefixes[type];
    if (prefix && !msg.startsWith(prefix.split(" ")[0])) payload.message = `${prefix.split(" ")[0]} ${msg}`;

    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload));
        //console.log("Gesendet:", payload);
        input.value = "";
    } else alert("WebSocket nicht verbunden");
} // END (Task 2)

// QR Code & Groups not done. 
const get_addgroup_qrcode = id => new QRCode(document.getElementById("qrCodeContainer"), {text:id, width:150, height:150});
const fillGroupInput = id => document.getElementById("joinGroupInput").value = id;

async function loadClientGroups(id) {
    const data = await (await fetch(`/api/client/${id}/groups`)).json();
    const container = document.getElementById("client-groups");
    container.innerHTML = data.groups.map(g => `<div>${g.wb_name} (${g.wb_id})</div>`).join("");
}

// navi
const openChat = () => location.href = `/chat.html?clientId=${clientId}`;
const openServerConsole = () => location.href = `/serverconsole.html?clientId=${clientId}`;

// set_mail manager
class AliasManager {
    constructor() {
        this.spans = document.querySelectorAll('.alias');
        this.pending = null;
        this.init();
        this.load();
    }
    init() {
        document.querySelectorAll('.setmail').forEach(box => {
            const input = box.querySelector('input');
            const btn = box.querySelector('.setmail-btn');
            if (!input || !btn) return;
            input.addEventListener('keypress', e => e.key === 'Enter' && this.save(input.value));
            btn.addEventListener('click', () => this.save(input.value));
        });
    }
    validate(email) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email); }
    save(email) {
        email = email.trim();
        if (!email) return void(this.clear());
        if (!this.validate(email)) return void this.fb('Ungültige E-Mail', 'error');

        localStorage.setItem('userEmail', email);
        this.update(email);
        this.fb('Sende...', 'loading');

        if (ws.readyState === WebSocket.OPEN) {
            this.pending = email;
            ws.send(JSON.stringify({ type: 'set_email', message: email }));
            setTimeout(() => this.pending === email && this.fb('Timeout', 'warning'), 5000);
        } else this.fb('Keine Verbindung', 'error');
    }
    confirmEmailSuccess(email) {
        if (this.pending === email) this.fb('E-Mail gesetzt!', 'success'), this.pending = null;
    }
    clear() { localStorage.removeItem('userEmail'); this.update('kein Alias'); this.fb('Gelöscht', 'info'); }
    update(text) { this.spans.forEach(s => { s.textContent = text; s.style.color = text === 'kein Alias' ? '#888' : '#2e8b57'; }); }
    load() { this.update(localStorage.getItem('userEmail') || 'kein Alias'); }
    fb(msg, type='info') {
        let el = document.getElementById('email-feedback') || (() => {
            const e = document.createElement('div'); e.id = 'email-feedback';
            e.style.cssText = 'position:fixed;bottom:20px;right:20px;padding:10px 20px;border-radius:6px;color:#fff;z-index:1000;opacity:1;transition:opacity .3s;';
            document.body.appendChild(e); return e;
        })();
        el.textContent = msg;
        el.style.background = {success:'#2e8b57',error:'#c73838',warning:'#ff8c00',loading:'#9370db'}[type] || '#1e90ff';
        clearTimeout(this.to); this.to = setTimeout(() => el.style.opacity = '0', 3000);
    }
}

// init
document.addEventListener('DOMContentLoaded', () => window.aliasManager = new AliasManager());
