/**
 * FarmFusion Kisan Mitra Calling Agent Dashboard Logic
 * Coordinates Vobiz outbound call triggers, live transcript display, and interactive orchestrator simulation.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const callForm = document.getElementById("callForm");
    const farmerPhone = document.getElementById("farmerPhone");
    const farmerName = document.getElementById("farmerName");
    const farmLocation = document.getElementById("farmLocation");
    const callLanguage = document.getElementById("callLanguage");
    const callType = document.getElementById("callType");
    const agentInstruction = document.getElementById("agentInstruction");
    const bypassCooldown = document.getElementById("bypassCooldown");
    const btnInitiateCall = document.getElementById("btnInitiateCall");
    const btnUseDemoPhone = document.getElementById("btnUseDemoPhone");

    const callStatePill = document.getElementById("callStatePill");
    const callTimer = document.getElementById("callTimer");
    const btnEndCall = document.getElementById("btnEndCall");
    const audioWave = document.getElementById("audioWaveVisualizer");
    const transcriptContainer = document.getElementById("transcriptContainer");
    const btnClearTranscript = document.getElementById("btnClearTranscript");

    const simUserInput = document.getElementById("simUserInput");
    const btnSendSimQuery = document.getElementById("btnSendSimQuery");
    const quickChips = document.querySelectorAll(".btn-chip");

    const btnTriggerMandi = document.getElementById("btnTriggerMandi");
    const btnTriggerWeather = document.getElementById("btnTriggerWeather");
    const btnTriggerAdvisory = document.getElementById("btnTriggerAdvisory");

    const callsTableBody = document.getElementById("callsTableBody");
    const btnRefreshCalls = document.getElementById("btnRefreshCalls");
    const toastContainer = document.getElementById("toastContainer");

    let activeCallInterval = null;
    let callSeconds = 0;
    let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);

    // 1. Toast Notification Helper
    function showToast(message, type = "success") {
        const toast = document.createElement("div");
        toast.className = "toast";
        if (type === "error") {
            toast.style.borderColor = "var(--accent-red)";
        }
        toast.innerHTML = `<span>${type === "error" ? "⚠️" : "✅"}</span> <span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(20px)";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // 2. Format E.164 Phone Helper
    function cleanPhone(raw) {
        let clean = raw.replace(/[\s\-()]/g, "");
        if (!clean.startsWith("+")) {
            if (/^[6-9]\d{9}$/.test(clean)) {
                clean = "+91" + clean;
            }
        }
        return clean;
    }

    // 3. Demo Phone Quick-Fill
    btnUseDemoPhone.addEventListener("click", () => {
        farmerPhone.value = "+919876543210";
        farmerName.value = "सुरेश कुमार";
        farmLocation.value = "Udaipur";
        showToast("Demo phone number loaded (+919876543210)");
    });

    // 4. Timer Controls
    function startTimer() {
        clearInterval(activeCallInterval);
        callSeconds = 0;
        callTimer.textContent = "00:00";
        activeCallInterval = setInterval(() => {
            callSeconds++;
            const mins = String(Math.floor(callSeconds / 60)).padStart(2, "0");
            const secs = String(callSeconds % 60).padStart(2, "0");
            callTimer.textContent = `${mins}:${secs}`;
        }, 1000);
    }

    function stopTimer() {
        clearInterval(activeCallInterval);
        callTimer.textContent = "00:00";
    }

    // 5. Append Message to Transcript Container
    function appendTranscriptTurn(speaker, text, isAi = false) {
        const turn = document.createElement("div");
        turn.className = `transcript-turn ${isAi ? "turn-ai" : "turn-farmer"}`;

        const avatar = isAi ? "🤖" : "👨‍🌾";
        const speakerLabel = isAi ? "Kisan Mitra (Orchestrator)" : (farmerName.value || "Farmer");

        turn.innerHTML = `
            <div class="speaker-avatar">${avatar}</div>
            <div class="turn-content">
                <span class="speaker-name">${speakerLabel}</span>
                <div class="bubble">${text}</div>
            </div>
        `;
        transcriptContainer.appendChild(turn);
        transcriptContainer.scrollTop = transcriptContainer.scrollHeight;
    }

    // 6. Handle Outbound Call Submission
    callForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const phone = cleanPhone(farmerPhone.value);
        if (!phone.startsWith("+91") || phone.length < 13) {
            showToast("Please enter a valid Indian mobile number (+91 followed by 10 digits).", "error");
            farmerPhone.focus();
            return;
        }

        const name = farmerName.value.trim() || "Farmer";
        const location = farmLocation.value.trim() || "India";
        const lang = callLanguage.value;
        const type = callType.value;
        const instruction = agentInstruction.value.trim() || null;
        const bypass = bypassCooldown.checked;

        btnInitiateCall.disabled = true;
        btnInitiateCall.innerHTML = `<span>⏳</span> Dialing Vobiz...`;
        callStatePill.className = "call-state-pill state-dialing";
        callStatePill.textContent = "DIALING (+91...)";

        try {
            const payload = {
                phone: phone,
                farmer_name: name,
                call_type: type,
                language: lang,
                location: location,
                agent_instruction: instruction,
                bypass_cooldown: bypass
            };

            const resp = await fetch("/api/v1/calling/call", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await resp.json();

            if (!resp.ok) {
                throw new Error(data.detail || "Failed to initiate call.");
            }

            // Successfully dispatched call to Vobiz
            showToast(`Call initiated to ${name} (${phone})! Call ID: ${data.call_id}`);
            callStatePill.className = "call-state-pill state-connected";
            callStatePill.textContent = "CALL ACTIVE (VOBIZ)";
            btnEndCall.style.display = "inline-block";
            audioWave.classList.add("active");
            startTimer();

            // Append initial greeting turn to transcript
            const greeting = lang === "hi" 
                ? `नमस्ते ${name} जी! फार्मफ्यूजन किसान मित्र में आपका स्वागत है। कॉल कनेक्ट हो गई है।`
                : `Hello ${name}! Welcome to FarmFusion Kisan Mitra. Your call is now connected.`;
            appendTranscriptTurn("Kisan Mitra", greeting, true);

            // Refresh recent calls
            fetchRecentCalls();

        } catch (err) {
            showToast(err.message, "error");
            callStatePill.className = "call-state-pill state-idle";
            callStatePill.textContent = "IDLE / STANDBY";
        } finally {
            btnInitiateCall.disabled = false;
            btnInitiateCall.innerHTML = `<span>📞</span> Call Me Now`;
        }
    });

    // 7. Hang Up Button
    btnEndCall.addEventListener("click", () => {
        stopTimer();
        audioWave.classList.remove("active");
        callStatePill.className = "call-state-pill state-idle";
        callStatePill.textContent = "CALL ENDED";
        btnEndCall.style.display = "none";
        appendTranscriptTurn("Kisan Mitra", "कॉल समाप्त हो गई है। फार्मफ्यूजन का उपयोग करने के लिए धन्यवाद!", true);
        showToast("Call session finished.");
        setTimeout(() => {
            callStatePill.textContent = "IDLE / STANDBY";
        }, 3000);
        fetchRecentCalls();
    });

    // 8. Clear Transcript
    btnClearTranscript.addEventListener("click", () => {
        transcriptContainer.innerHTML = "";
    });

    // 9. Interactive Dialogue Simulator
    async function sendSimulationQuery(queryText) {
        const query = (queryText || simUserInput.value).trim();
        if (!query) return;

        appendTranscriptTurn(farmerName.value || "Farmer", query, false);
        simUserInput.value = "";
        btnSendSimQuery.disabled = true;
        btnSendSimQuery.textContent = "...";
        audioWave.classList.add("active");

        try {
            const resp = await fetch("/api/v1/calling/simulate-turn", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_input: query,
                    farmer_name: farmerName.value.trim() || "सुरेश कुमार",
                    location: farmLocation.value.trim() || "Udaipur",
                    language: callLanguage.value || "hi",
                    session_id: currentSessionId
                })
            });

            const data = await resp.json();
            if (!resp.ok) {
                throw new Error(data.detail || "Simulation failed.");
            }

            appendTranscriptTurn("Kisan Mitra", data.response_text, true);

        } catch (err) {
            showToast("Simulation error: " + err.message, "error");
            appendTranscriptTurn("Kisan Mitra", "माफ़ कीजियेगा, जानकारी प्राप्त करने में समस्या आई।", true);
        } finally {
            btnSendSimQuery.disabled = false;
            btnSendSimQuery.textContent = "Send";
            setTimeout(() => {
                if (callStatePill.textContent.indexOf("ACTIVE") === -1) {
                    audioWave.classList.remove("active");
                }
            }, 1200);
        }
    }

    btnSendSimQuery.addEventListener("click", () => sendSimulationQuery());
    simUserInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendSimulationQuery();
    });

    quickChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const q = chip.getAttribute("data-query");
            sendSimulationQuery(q);
        });
    });

    // 10. Quick-Fire Scenario Buttons
    btnTriggerMandi.addEventListener("click", () => {
        callType.value = "mandi_price_alert";
        agentInstruction.value = "Notify that Kota Mandi wheat price reached ₹2,500/quintal. Ask if they want to book sale.";
        showToast("Loaded Kota Wheat Mandi Alert Scenario. Click 'Call Me Now'!");
    });

    btnTriggerWeather.addEventListener("click", () => {
        callType.value = "weather_warning";
        agentInstruction.value = "Severe thunderstorm and 80% heavy rainfall expected in Udaipur. Advise draining field water.";
        showToast("Loaded Udaipur Heavy Rainfall Alert Scenario. Click 'Call Me Now'!");
    });

    btnTriggerAdvisory.addEventListener("click", () => {
        callType.value = "general_advisory";
        agentInstruction.value = "Check soil moisture status and advise on irrigation scheduling for current crop.";
        showToast("Loaded Irrigation Advisory Scenario. Click 'Call Me Now'!");
    });

    // 11. Fetch Recent Calls
    async function fetchRecentCalls() {
        try {
            const resp = await fetch("/api/v1/calling/recent");
            if (!resp.ok) return;
            const data = await resp.json();

            // Update Phone Number if returned
            if (data.vobiz_number) {
                document.getElementById("headerPhoneNumber").textContent = data.vobiz_number;
                document.getElementById("statPhoneNumber").textContent = data.vobiz_number;
                document.getElementById("bannerPhoneNumber").textContent = data.vobiz_number;
            }

            const calls = data.calls || [];
            if (calls.length === 0) {
                callsTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;">No calls placed yet. Click "Call Me Now" to start!</td></tr>`;
                return;
            }

            callsTableBody.innerHTML = calls.map(c => `
                <tr>
                    <td><code style="color: #6EE7B7; font-size: 11px;">${(c.call_id || "N/A").substring(0, 8)}...</code></td>
                    <td>${c.formatted_time || "Just now"}</td>
                    <td><strong>${c.farmer_name || "Farmer"}</strong></td>
                    <td>${c.phone || "N/A"}</td>
                    <td><span style="font-size: 11px; text-transform: capitalize;">${(c.call_type || "general").replace(/_/g, " ")}</span></td>
                    <td><span class="status-pill status-${c.status || "initiated"}">${c.status || "initiated"}</span></td>
                </tr>
            `).join("");

        } catch (e) {
            console.warn("fetchRecentCalls failed", e);
        }
    }

    btnRefreshCalls.addEventListener("click", () => {
        fetchRecentCalls();
        showToast("Call logs refreshed.");
    });

    // Initial load and periodic refresh every 10 seconds
    fetchRecentCalls();
    setInterval(fetchRecentCalls, 10000);
});
