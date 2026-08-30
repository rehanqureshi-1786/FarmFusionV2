// FarmFusion - Real-Time Animal Intrusion Detection Dashboard Logic (6x IR + 2x PIR)

class FarmFusionDashboard {
    constructor() {
        this.serverHost = localStorage.getItem("ff_server_host") || "127.0.0.1:8000";
        this.ws = null;
        this.reconnectTimer = null;
        this.syncTimer = null;
        this.isDeviceOnline = false;
        
        // Granular Per-Sensor State Tracking (8 Sensors)
        this.sensorsState = {
            "IR_1": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "IR_2": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "IR_3": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "IR_4": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "IR_5": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "IR_6": { status: "cleared", health: "online", sensor_type: "IR", last_seen: null },
            "PIR_1": { status: "cleared", health: "online", sensor_type: "PIR", last_seen: null },
            "PIR_2": { status: "cleared", health: "online", sensor_type: "PIR", last_seen: null }
        };

        // Cache last rendered state to prevent unnecessary DOM repaints/flickering
        this.lastRenderedCards = {};
        this.lastRenderedBanner = null;

        this.inputServerIp = document.getElementById("serverIpInput");
        this.btnReconnect = document.getElementById("reconnectBtn");
        this.btnRefreshHistory = document.getElementById("refreshHistoryBtn");
        
        this.chipBackend = document.getElementById("chipBackend");
        this.lblBackend = document.getElementById("lblBackend");
        
        this.chipWebsocket = document.getElementById("chipWebsocket");
        this.lblWebsocket = document.getElementById("lblWebsocket");
        
        this.chipDevice = document.getElementById("chipDevice");
        this.lblDevice = document.getElementById("lblDevice");

        this.overallCard = document.getElementById("overallStatusCard");
        this.overallIcon = document.getElementById("overallStatusIcon");
        this.overallText = document.getElementById("overallStatusText");
        this.overallDetail = document.getElementById("overallStatusDetail");

        this.alertContent = document.getElementById("alertContent");
        this.historyBody = document.getElementById("historyTableBody");

        this.init();
    }

    init() {
        this.inputServerIp.value = this.serverHost;
        
        this.btnReconnect.addEventListener("click", () => {
            this.serverHost = this.inputServerIp.value.trim();
            localStorage.setItem("ff_server_host", this.serverHost);
            this.connectAll();
        });

        this.btnRefreshHistory.addEventListener("click", () => {
            this.fetchHistory();
        });

        this.connectAll();
    }

    get httpBaseUrl() {
        const host = this.serverHost.replace(/^https?:\/\//, "");
        return `http://${host}`;
    }

    get wsBaseUrl() {
        const host = this.serverHost.replace(/^ws?:\/\//, "").replace(/^https?:\/\//, "");
        return `ws://${host}`;
    }

    connectAll() {
        this.fetchInitialState();
        this.fetchHistory();
        this.initWebSocket();

        // 1.5-second smooth polling reconciliation timer
        if (this.syncTimer) clearInterval(this.syncTimer);
        this.syncTimer = setInterval(() => this.fetchInitialState(), 1500);
    }

    async fetchInitialState() {
        try {
            const res = await fetch(`${this.httpBaseUrl}/api/v1/animal-detection/latest`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            
            this.updateBackendStatus(true);
            
            this.isDeviceOnline = (data.overall_status !== "NODE_OFFLINE");
            this.updateDeviceStatus(this.isDeviceOnline);

            if (data.sensors) {
                for (const [sName, sDetail] of Object.entries(data.sensors)) {
                    if (typeof sDetail === "object" && sDetail !== null) {
                        this.sensorsState[sName] = {
                            status: sDetail.status || "cleared",
                            health: this.isDeviceOnline ? "online" : "offline",
                            sensor_type: sDetail.sensor_type || (sName.startsWith("PIR") ? "PIR" : "IR"),
                            last_seen: sDetail.last_seen || null
                        };
                    }
                }
            }

            this.renderSensorsMatrix();
            this.updateOverallBanner(data.overall_status, data.detected_sensors || [], data.offline_sensors || []);
        } catch (err) {
            this.updateBackendStatus(false);
            this.updateDeviceStatus(false);
            this.renderSensorsMatrix();
            this.updateOverallBanner("NODE_OFFLINE");
        }
    }

    async fetchHistory() {
        try {
            const res = await fetch(`${this.httpBaseUrl}/api/v1/animal-detection/history?limit=50`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            this.renderHistory(data.events || []);
        } catch (err) {}
    }

    initWebSocket() {
        if (this.ws) this.ws.close();

        const wsUrl = `${this.wsBaseUrl}/api/v1/ws/animal-detection`;
        this.updateWebsocketStatus("CONNECTING...", "warning");

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.updateWebsocketStatus("CONNECTED", "online");
                if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
            };

            this.ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.event === "animal_detection" && msg.data) {
                        this.handleRealtimeDetection(msg.data);
                    } else if (msg.event === "sensor_telemetry" && msg.data) {
                        this.handleSensorTelemetry(msg.data);
                    }
                } catch (e) {}
            };

            this.ws.onclose = () => {
                this.updateWebsocketStatus("DISCONNECTED", "offline");
                this.scheduleReconnect();
            };

            this.ws.onerror = () => {
                this.updateWebsocketStatus("ERROR", "offline");
            };
        } catch (err) {
            this.updateWebsocketStatus("FAILED", "offline");
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
        this.reconnectTimer = setTimeout(() => this.initWebSocket(), 2000);
    }

    handleRealtimeDetection(data) {
        this.isDeviceOnline = true;
        this.updateDeviceStatus(true);

        this.sensorsState[data.sensor] = {
            status: data.status,
            health: "online",
            sensor_type: data.sensor_type,
            last_seen: data.timestamp
        };

        this.renderSensorsMatrix();
        this.updateOverallStatusFromState();

        if (data.status === "detected") {
            this.renderLiveAlert(data);
        }
        this.prependHistoryRow(data);
    }

    handleSensorTelemetry(data) {
        this.isDeviceOnline = true;
        this.updateDeviceStatus(true);

        if (!this.sensorsState[data.sensor]) {
            this.sensorsState[data.sensor] = {};
        }
        this.sensorsState[data.sensor].health = "online";
        this.sensorsState[data.sensor].status = data.status;
        this.sensorsState[data.sensor].last_seen = data.timestamp;

        this.renderSensorsMatrix();
        this.updateOverallStatusFromState();
    }

    updateBackendStatus(isOnline) {
        const dot = this.chipBackend.querySelector(".dot");
        const text = isOnline ? "ONLINE" : "OFFLINE";
        if (this.lblBackend.textContent !== text) {
            dot.className = isOnline ? "dot dot-online" : "dot dot-offline";
            this.lblBackend.textContent = text;
        }
    }

    updateWebsocketStatus(text, state) {
        const dot = this.chipWebsocket.querySelector(".dot");
        if (this.lblWebsocket.textContent !== text) {
            this.lblWebsocket.textContent = text;
            if (state === "online") dot.className = "dot dot-online";
            else if (state === "warning") dot.className = "dot dot-warning";
            else dot.className = "dot dot-offline";
        }
    }

    updateDeviceStatus(isOnline) {
        this.isDeviceOnline = isOnline;
        const dot = this.chipDevice.querySelector(".dot");
        const text = isOnline ? "ONLINE" : "OFFLINE";
        if (this.lblDevice.textContent !== text) {
            dot.className = isOnline ? "dot dot-online" : "dot dot-offline";
            this.lblDevice.textContent = text;
        }
    }

    renderSensorsMatrix() {
        for (const [sensor, detail] of Object.entries(this.sensorsState)) {
            const card = document.getElementById(`card-${sensor}`);
            if (!card) continue;

            const statusEl = card.querySelector(".sensor-status");
            let targetCardClass = "sensor-card";
            let targetStatusClass = "sensor-status status-text-detecting";
            let targetText = "🟢 DETECTING";

            // State Evaluation:
            if (!this.isDeviceOnline) {
                targetCardClass = "sensor-card is-offline";
                targetStatusClass = "sensor-status status-text-offline";
                targetText = "⚪ NODE OFFLINE";
            } else if (detail.status === "detected") {
                targetCardClass = "sensor-card is-detected";
                targetStatusClass = "sensor-status status-text-detected";
                targetText = "🔴 DETECTED";
            } else {
                targetCardClass = "sensor-card";
                targetStatusClass = "sensor-status status-text-detecting";
                targetText = "🟢 DETECTING";
            }

            // Smooth DOM Diffing: Update ONLY if changed to prevent screen flicker
            const cardKey = `${targetCardClass}|${targetStatusClass}|${targetText}`;
            if (this.lastRenderedCards[sensor] !== cardKey) {
                this.lastRenderedCards[sensor] = cardKey;
                card.className = targetCardClass;
                statusEl.className = targetStatusClass;
                statusEl.textContent = targetText;
            }
        }
    }

    updateOverallStatusFromState() {
        if (!this.isDeviceOnline) {
            this.updateOverallBanner("NODE_OFFLINE");
            return;
        }

        const detectedList = Object.entries(this.sensorsState)
            .filter(([_, d]) => d.status === "detected")
            .map(([s, _]) => s);

        if (detectedList.length > 0) {
            this.updateOverallBanner("INTRUSION_DETECTED", detectedList);
        } else {
            this.updateOverallBanner("AREA_CLEAR");
        }
    }

    updateOverallBanner(overallStatus, detectedList = [], offlineList = []) {
        let cardClass = "overall-status-card status-clear";
        let icon = "🟢";
        let title = "ACTIVELY DETECTING";
        let detail = "All active sensors online and actively monitoring the area.";

        if (overallStatus === "NODE_OFFLINE" || !this.isDeviceOnline) {
            cardClass = "overall-status-card status-node-offline";
            icon = "⚪";
            title = "ESP32 NODE DISCONNECTED";
            detail = "Hardware node is offline. Waiting for Wi-Fi or power connection...";
        } else if (overallStatus === "INTRUSION_DETECTED" || detectedList.length > 0) {
            cardClass = "overall-status-card status-detected";
            icon = "🔴";
            title = "ANIMAL INTRUSION DETECTED";
            detail = `Active intrusion detected on: ${detectedList.join(" + ")}`;
        }

        // Smooth DOM Diffing: Update ONLY if changed
        const bannerKey = `${cardClass}|${icon}|${title}|${detail}`;
        if (this.lastRenderedBanner !== bannerKey) {
            this.lastRenderedBanner = bannerKey;
            this.overallCard.className = cardClass;
            this.overallIcon.textContent = icon;
            this.overallText.textContent = title;
            this.overallDetail.textContent = detail;
        }
    }

    renderLiveAlert(data) {
        const timeFormatted = this.formatTime(data.timestamp);
        this.alertContent.innerHTML = `
            <div class="alert-active">
                <div class="alert-title">🔴 ANIMAL INTRUSION DETECTED</div>
                <div class="alert-meta">
                    <div class="alert-meta-item"><strong>Sensor:</strong> ${data.sensor}</div>
                    <div class="alert-meta-item"><strong>Type:</strong> ${data.sensor_type}</div>
                    <div class="alert-meta-item"><strong>Device:</strong> ${data.device_id}</div>
                    <div class="alert-meta-item"><strong>Time:</strong> ${timeFormatted}</div>
                </div>
            </div>
        `;
    }

    renderHistory(events) {
        if (!events || events.length === 0) {
            this.historyBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="5">No events logged yet. Waiting for hardware events...</td>
                </tr>
            `;
            return;
        }

        this.historyBody.innerHTML = events.map(evt => this.createHistoryRowHtml(evt)).join("");
    }

    prependHistoryRow(evt) {
        const emptyRow = this.historyBody.querySelector(".empty-row");
        if (emptyRow) emptyRow.remove();

        const tr = document.createElement("tr");
        tr.className = "new-row";
        tr.innerHTML = `
            <td>${this.formatTime(evt.timestamp)}</td>
            <td>${evt.device_id}</td>
            <td><strong>${evt.sensor}</strong></td>
            <td>${evt.sensor_type}</td>
            <td><span class="badge-status ${evt.status === "detected" ? "badge-detected" : "badge-detecting"}">${evt.status === "detected" ? "DETECTED" : "DETECTING"}</span></td>
        `;

        this.historyBody.insertBefore(tr, this.historyBody.firstChild);
    }

    createHistoryRowHtml(evt) {
        return `
            <tr>
                <td>${this.formatTime(evt.timestamp)}</td>
                <td>${evt.device_id}</td>
                <td><strong>${evt.sensor}</strong></td>
                <td>${evt.sensor_type}</td>
                <td><span class="badge-status ${evt.status === "detected" ? "badge-detected" : "badge-detecting"}">${evt.status === "detected" ? "DETECTED" : "DETECTING"}</span></td>
            </tr>
        `;
    }

    formatTime(timestampStr) {
        if (!timestampStr) return "N/A";
        try {
            const date = new Date(timestampStr);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch {
            return timestampStr;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.app = new FarmFusionDashboard();
});
