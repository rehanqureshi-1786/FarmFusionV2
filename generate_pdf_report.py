import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#424242"))
        
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 760, "FARMFUSION — ARCHITECTURE, MODELS, DATASETS & AGENT SYSTEM SPECIFICATION")
            self.drawRightString(572, 760, "PRODUCTION V2.4 | TECHNICAL AUDIT")
            self.setStrokeColor(colors.HexColor("#2E7D32"))
            self.setLineWidth(0.8)
            self.line(40, 754, 572, 754)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(40, 32, 572, 32)
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#616161"))
        footer_left = "Confidential Technical Specification | FarmFusion Multilingual AI Agricultural Copilot"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(40, 22, footer_left)
        self.drawRightString(572, 22, footer_right)
        self.restoreState()

def build_pdf(filename="FarmFusion_Complete_System_Architecture_and_Models_Report.pdf"):
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    # 612 x 792 letter size with 40 pt margins -> 532 pt printable width, 712 pt printable height
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#1B5E20")    # Deep Forest Green
    c_secondary = colors.HexColor("#2E7D32")  # Leaf Green
    c_dark = colors.HexColor("#212121")       # Dark Charcoal
    c_muted = colors.HexColor("#616161")      # Slate Gray

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=23,
        textColor=c_primary,
        alignment=1,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=c_secondary,
        alignment=1,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_muted,
        alignment=1,
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_primary,
        spaceBefore=5,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=c_secondary,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark,
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_dark,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.0,
        leading=8.8,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=8.8,
        textColor=c_dark
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.0,
        textColor=colors.white
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#0D47A1")
    )

    story = []

    # =========================================================================
    # PAGE 1: EXECUTIVE OVERVIEW & ARCHITECTURAL FOUNDATIONS
    # =========================================================================
    story.append(Paragraph("FarmFusion: Complete System Architecture & Blueprint", title_style))
    story.append(Paragraph("Multilingual AI Copilot — Working, AI/ML Models, Datasets & Agent Ecosystem", subtitle_style))
    story.append(Paragraph("Target Profile: B.Tech AI/ML Engineering & Production Agritech | Stack: Kotlin Android + FastAPI Async + pgvector + Redis", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.0, color=c_primary, spaceBefore=0, spaceAfter=5))

    exec_summary_html = (
        "<b>Executive Summary:</b> FarmFusion is a production-grade, multilingual AI agricultural copilot engineered for Indian smallholder farmers. "
        "The system operates across a native Kotlin Android frontend and an asynchronous FastAPI backend (Python 3.13, PostgreSQL 16 + pgvector, Redis). "
        "Architecturally, FarmFusion enforces a strict three-tier separation: (1) <b>Stateful Multi-Turn Agents</b> for conversational orchestration and telephony; "
        "(2) <b>Deterministic ML Workflows</b> for high-stakes decisions (crop disease detection, crop recommendation, mandi price forecasting); and "
        "(3) <b>Deterministic Tools</b> for external ground-truth APIs (live weather, mandi prices, soil moisture, and government schemes). "
        "<b>Core Design Rule: Zero Data Fabrication.</b> Neural LLMs never estimate weather metrics or invent mandi prices; they only synthesize verified ML/API outputs."
    )
    callout_data = [[Paragraph(exec_summary_html, callout_style)]]
    callout_table = Table(callout_data, colWidths=[532])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E8EAF6")),
        ('BORDER', (0,0), (-1,-1), 0.8, colors.HexColor("#7986CB")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. System Working & High-Level Architecture", h1_style))
    arch_points = [
        "<b>Frontend Client (Kotlin / Jetpack Compose):</b> Native Android application using Jetpack Compose, Retrofit HTTP/WebSocket client, and Navigation Component. Communicates via REST APIs on port 8000 and full-duplex WebSockets for real-time telephony voice calls and IoT intrusion push alerts.",
        "<b>Asynchronous Backend (FastAPI / Python 3.13):</b> Non-blocking async execution using AsyncIO, SQLAlchemy 2.0 async engine, Pydantic v2 validation, and structlog JSON structured logging. Powers the LangGraph state machine, telephony audio pipes, and ML model workers.",
        "<b>Hybrid Database (PostgreSQL 16 + pgvector):</b> Relational tables store farmer profiles, crop histories, price alerts, and IoT events. pgvector HNSW indexing (1024-dimensional) indexes chunked ICAR crop guidelines and central/state government schemes.",
        "<b>In-Memory Caching & Session Store (Redis):</b> Ephemeral session checkpoints, 15-minute weather TTL caches, 12-hour mandi forecast caches, and 24-hour multilingual neural audio voice cache keys (<font face='Courier'>tts:{lang}:{hash}</font>).",
        "<b>Strict Architectural Distinction:</b> The platform distinguishes between an <i>Agent</i> (stateful, dynamic multi-step goal planning), a <i>Workflow</i> (fixed-step ML + RAG + LLM pipeline with zero branching ambiguity), and a <i>Tool</i> (single-call, deterministic async function)."
    ]
    for pt in arch_points:
        story.append(Paragraph(f"• {pt}", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("System Component Classification Matrix", h2_style))

    matrix_data = [
        [Paragraph("Category", table_cell_header), Paragraph("Component Name", table_cell_header), Paragraph("Primary Engine / Tech", table_cell_header), Paragraph("Role & Execution Boundary", table_cell_header)],
        [Paragraph("Agent", table_cell_bold), Paragraph("Main Multilingual Orchestrator", table_cell), Paragraph("LangGraph StateGraph + Gemma 3 12B", table_cell), Paragraph("Stateful multi-turn dialogue, intent extraction, slot filling, tool routing.", table_cell)],
        [Paragraph("Agent", table_cell_bold), Paragraph("Kisan Calling Agent", table_cell), Paragraph("Telephony WebSocket + STT/TTS + LLM", table_cell), Paragraph("Full-duplex outbound phone calls for market alerts, weather warnings.", table_cell)],
        [Paragraph("Agent / Tool", table_cell_bold), Paragraph("Weather Intelligence Agent", table_cell), Paragraph("Open-Meteo API + TTL Cache", table_cell), Paragraph("Live/forecast meteorology, soil moisture profiles, smart irrigation schedules.", table_cell)],
        [Paragraph("Workflow", table_cell_bold), Paragraph("Crop Disease Detection", table_cell), Paragraph("EfficientNet-B3 (PyTorch) + ICAR RAG", table_cell), Paragraph("Leaf gatekeeper check, 38-class classification, confidence tiering, treatment.", table_cell)],
        [Paragraph("Workflow", table_cell_bold), Paragraph("Crop Recommendation", table_cell), Paragraph("XGBoost 22-Class + Regional Rules", table_cell), Paragraph("Soil test NPK/pH + historical ERA5 rain + state agronomic re-ranking.", table_cell)],
        [Paragraph("Workflow", table_cell_bold), Paragraph("Mandi Price Forecaster", table_cell), Paragraph("Meta Prophet + LightGBM Ensemble", table_cell), Paragraph("7-day modal price forecast, 95% CI bands, Sell-vs-Wait decision logic.", table_cell)],
        [Paragraph("Tool", table_cell_bold), Paragraph("Disaster Risk Predictor", table_cell), Paragraph("4-Model Soft Voting Ensemble", table_cell), Paragraph("12-feature thermodynamic physical analysis for Drought, Flood, Cyclone.", table_cell)],
        [Paragraph("Tool", table_cell_bold), Paragraph("RAG Scheme Search", table_cell), Paragraph("BGE-M3 Embeddings + pgvector HNSW", table_cell), Paragraph("Vector retrieval of authentic central/state agricultural subsidies.", table_cell)],
        [Paragraph("Hardware Edge", table_cell_bold), Paragraph("IoT Animal Intrusion", table_cell), Paragraph("ESP32 C++ + 6 IR + 2 PIR Sensors", table_cell), Paragraph("Real-time crop perimeter breach detection, deterrence buzzer, push alert.", table_cell)]
    ]
    t_matrix = Table(matrix_data, colWidths=[65, 125, 140, 202])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FBE7")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DCE775")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_matrix)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: AGENT & WORKFLOW DEEP DIVE (PART 1: 2.1 to 2.5)
    # =========================================================================
    story.append(Paragraph("2. Deep-Dive: Every Agent, Workflow & Tool Breakdown (Part 1)", h1_style))
    story.append(Paragraph(
        "Each subsystem enforces strict deterministic bounds. Below is the operational specification of components 2.1 through 2.5:",
        body_style
    ))

    # 2.1 ORCHESTRATOR
    story.append(Paragraph("2.1 Main Multilingual Orchestrator (LangGraph Stateful Agent)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/orchestrator/</font> (<font face='Courier'>graph.py, state.py, nodes/</font>)<br/>"
        "<b>Architecture:</b> LangGraph <font face='Courier'>StateGraph</font> with <font face='Courier'>MemorySaver</font> checkpointer for multi-turn session persistence.<br/>"
        "<b>Operational Flow:</b> Executes a 3-node directed acyclic graph on every user turn: "
        "<br/>1. <b>Intent Classification Node:</b> Analyzes natural language input (voice transcription or text) across 9 canonical intents "
        "(<font face='Courier'>weather, mandi_prices, crop_recommendation, disease_detection, disaster_risk, scheme_info, navigation, smalltalk, unknown</font>). "
        "Extracts semantic entity slots (crop name, mandi/district, soil NPK values, state). If intent confidence &lt; 0.60 or critical slots are missing, "
        "it branches directly to clarification: sets <font face='Courier'>requires_clarification = True</font> and synthesizes a clarifying question without calling tools. "
        "<br/>2. <b>Tool Router Node:</b> Dispatches validated intents to asynchronous single-call functions in <font face='Courier'>ToolRegistry</font>. Aggregates structured tool outputs. "
        "<br/>3. <b>Response Synthesizer Node:</b> Prompts Gemma 3 12B (fallback: Qwen2.5-7B) via OpenRouter. Enforces strict rural-friendly constraints: "
        "short 2–3 sentence responses, dominant language matching (Tier 1/2/3), zero fabricated numbers, and practical agricultural action points.",
        body_style
    ))

    # 2.2 KISAN CALLING AGENT
    story.append(Paragraph("2.2 Kisan Calling Agent (Telephony Voice Agent)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/calling_agent/</font> (<font face='Courier'>orchestrator.py, service.py, stt.py, tts.py, prompts.py</font>)<br/>"
        "<b>Architecture:</b> Full-duplex WebSocket Telephony Orchestrator (<font face='Courier'>KisanVoiceOrchestrator</font>).<br/>"
        "<b>Operational Flow:</b> Manages automated inbound/outbound telephone calls with farmers for critical farm events (severe weather warnings, "
        "target mandi price alerts, pest outbreak advisories). Streams raw 8kHz/16kHz PCM audio over WebSockets, executes streaming Voice Activity Detection (VAD) "
        "with energy thresholds, runs Telephony STT, streams token completions from Groq / OpenRouter with &lt;800ms latency, and serializes synthesized audio packets "
        "via Telephony TTS back to the phone line. Handles real-time farmer barge-in interruption seamlessly.",
        body_style
    ))

    # 2.3 WEATHER AGENT
    story.append(Paragraph("2.3 Weather Intelligence Agent & Agronomic Advisor", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/agents/weather_agent.py</font> & <font face='Courier'>app/tools/weather_tool.py</font><br/>"
        "<b>Operational Flow:</b> Queries Open-Meteo High-Resolution Forecast and Historical Reanalysis APIs. Maintains an in-memory 15-minute TTL cache "
        "to guarantee low latency and prevent rate limits. Key modules: "
        "<br/>• <b>Dynamic Reverse-Geocoding:</b> Automatically maps raw GPS coordinates into recognized district/mandi names across India. "
        "<br/>• <b>Smart Irrigation Advisor:</b> Retrieves multi-depth soil moisture data (0–1cm, 1–3cm, 3–9cm, 9–27cm) and reference evapotranspiration (ET0) "
        "to compute water deficits, explicitly alerting against unnecessary irrigation when heavy rain is forecast. "
        "<br/>• <b>Deterministic Agronomic Rules:</b> Programmatically evaluates pesticide spray windows (wind &lt; 15 km/h, humidity &lt; 85%, no rain next 6 hrs), "
        "frost warnings (temp &lt; 4°C), and crop heat stress conditions.",
        body_style
    ))

    # 2.4 CROP RECOMMENDATION WORKFLOW
    story.append(Paragraph("2.4 Crop Recommendation Workflow (Hybrid ML + Regional Re-ranking)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/workflows/crop_recommendation.py</font><br/>"
        "<b>Operational Flow:</b> Executes a 4-stage deterministic decision pipeline: "
        "<br/>1. <b>Soil Report Ingestion:</b> Ingests laboratory Soil Health Card parameters (N, P, K in kg/ha, pH 0–14) via OCR or user confirmation. Never fabricated. "
        "<br/>2. <b>Climatic Augmentation:</b> Queries Open-Meteo ERA5-Land for historical cumulative annual rainfall and current temperature/humidity for the farm's location. "
        "<br/>3. <b>XGBoost Classifier:</b> Runs the 10-feature gradient-boosted decision tree model to produce softmax probability distributions across 22 crops. "
        "<br/>4. <b>Regional Validation:</b> Cross-references ML outputs against state-level ICAR agro-climatic crop suitability databases. Agronomically impossible crops "
        "(e.g. coconut in Punjab rabi) are penalized and replaced with the top regionally validated alternative.",
        body_style
    ))

    # 2.5 CROP DISEASE DETECTION WORKFLOW
    story.append(Paragraph("2.5 Crop Disease Detection Workflow (Vision CNN + Knowledge Base)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/workflows/disease_workflow.py</font><br/>"
        "<b>Operational Flow:</b> Guards crop leaf diagnostics through a verified multi-layer pipeline: "
        "<br/>1. <b>Plant Foliage Gatekeeper:</b> Validates that the uploaded image contains plant tissue before executing neural inference. "
        "<br/>2. <b>EfficientNet-B3 Inference:</b> Evaluates 300x300 normalized image tensors across 38 crop disease classes spanning 14 agricultural species. "
        "<br/>3. <b>Confidence Tier Assignment:</b> Categorizes output into High (&ge;0.75), Medium (0.45–0.74), Low (0.30–0.44), or Unclear (&lt;0.30). "
        "<br/>4. <b>ICAR Knowledge Retrieval:</b> Retrieves biological controls (e.g. Neem oil, Trichoderma viride) and CIBRC chemical treatments. "
        "<b>Safety Guard:</b> If confidence is Low or Unclear, chemical fungicide dosages are strictly withheld to avoid toxic misuse.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: AGENT & WORKFLOW DEEP DIVE (PART 2: 2.6 to 2.10)
    # =========================================================================
    story.append(Paragraph("2. Deep-Dive: Every Agent, Workflow & Tool Breakdown (Part 2)", h1_style))
    story.append(Paragraph(
        "Operational specification of components 2.6 through 2.10:",
        body_style
    ))

    # 2.6 MANDI FORECASTER
    story.append(Paragraph("2.6 Mandi / Market Intelligence Workflow (Prophet + LightGBM Ensemble)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/ml/market/forecaster.py</font> & <font face='Courier'>app/services/mandi_intelligence.py</font><br/>"
        "<b>Operational Flow:</b> Combines tabular government market data, geodesic geometry, and dual ML algorithms: "
        "<br/>• <b>Geodesic Distance Scoring:</b> Applies the Haversine trigonometric formula to calculate distance between farmer GPS and regional APMC mandis. "
        "Computes a practical composite score: <font face='Courier'>Score = 0.50 * Price_Norm + 0.35 * Distance_Score + 0.15 * Freshness_Score</font>. "
        "<br/>• <b>Dual ML Forecasting Ensemble:</b> Integrates Meta Prophet (for Fourier annual/weekly seasonal cycles) and LightGBM (for autoregressive lag features) "
        "via a 60/40 weighted average to forecast 7-day daily modal prices with 95% confidence intervals. "
        "<br/>• <b>Deterministic Sell vs Wait Advisory:</b> If expected 7-day price delta &gt; +2.5%, issues 'HOLD'; if &lt; -2.5%, issues 'SELL NOW'; "
        "otherwise advises 'STABLE MARKET'. Zero LLM price hallucination.",
        body_style
    ))

    # 2.7 DISASTER PREDICTOR
    story.append(Paragraph("2.7 Disaster Risk Prediction Tool (4-Model Soft-Voting Ensemble)", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/ml/disaster/</font> (<font face='Courier'>inference.py, artifacts/</font>)<br/>"
        "<b>Operational Flow:</b> Transforms 5 primary weather readings (temperature, relative humidity, 24-hr rainfall, wind speed, atmospheric pressure) "
        "into 12 thermodynamic indices (Wind-Rain Interaction, Rain Intensity, Heat Stress, Atmospheric Instability, Pressure Anomaly). "
        "Executes a soft-voting ensemble comprising Random Forest, Gradient Boosting, Extra Trees, and XGBoost (25% weight each). "
        "Predicts 4 multi-hazard categories: Cyclone Risk, Drought Risk, Flood Risk, and Low Risk with calibrated probability distributions.",
        body_style
    ))

    # 2.8 IOT ANIMAL INTRUSION
    story.append(Paragraph("2.8 IoT Perimeter Animal Intrusion Detection Subsystem", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/animal_detection/</font> & <font face='Courier'>esp32/animal_detection/animal_detection.ino</font><br/>"
        "<b>Operational Flow:</b> Protects standing crops from wild animal raiding (boars, nilgai, elephants). An ESP32 microcontroller deployed at farm boundaries "
        "monitors 6 Infrared (IR) beam-break sensors and 2 Passive Infrared (PIR) motion sensors. On perimeter breach, the firmware triggers local acoustic/light "
        "deterrents and transmits sub-second telemetry over WiFi/HTTP to the backend. The backend persists the state-change in PostgreSQL and broadcasts "
        "instant WebSocket push notifications to the farmer's Android device specifying the breached boundary (North, South, East, West).",
        body_style
    ))

    # 2.9 UNIVERSAL VOICE & MULTILINGUAL SYSTEM
    story.append(Paragraph("2.9 Universal Voice & Multilingual Localization Engine", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/voice/</font> (<font face='Courier'>provider_router.py, profiles.py, bhashini.py, local/</font>)<br/>"
        "<b>Operational Flow:</b> Natively supports 22+ Indian languages across 3 operational tiers: "
        "<br/>• <b>Tier 1 (Full Pipeline):</b> Hindi, English, Bengali, Gujarati, Marathi, Punjabi, Tamil, Telugu, Kannada, Malayalam. "
        "<br/>• <b>Tier 2 (Partial Pipeline):</b> Odia, Assamese, Maithili, Santali. "
        "<br/>• <b>Tier 3 (Dialects):</b> Mewari, Marwari, Bhojpuri, Awadhi, Haryanvi, Rajasthani. "
        "<br/>• <b>Provider Cascading:</b> Prioritizes genuine local ONNX neural TTS models (e.g. Piper Hindi) when installed on the host. If missing, seamlessly "
        "cascades to the Government of India Bhashini API. Implements a 24-hour Redis caching layer for repeated speech phrases to ensure instantaneous playback.",
        body_style
    ))

    # 2.10 RAG & SCHEMES ENGINE
    story.append(Paragraph("2.10 RAG Knowledge Base & Government Scheme Retrieval", h2_style))
    story.append(Paragraph(
        "<b>Code Path:</b> <font face='Courier'>backend/app/rag/</font> (<font face='Courier'>embedder.py, retriever.py, ingestion.py</font>)<br/>"
        "<b>Operational Flow:</b> Indexes verified agricultural guidelines and welfare schemes (PM-KISAN, PMFBY crop insurance, Kisan Credit Card, PKVY organic farming). "
        "Text is ingested, chunked into 512-token segments, and transformed into 1024-dimensional dense vectors using BAAI/BGE-M3. "
        "At query time, the retriever executes cosine distance search (<font face='Courier'>&lt;=&gt;</font>) against a PostgreSQL pgvector HNSW index. "
        "Retrieved chunks are passed to the synthesizer node as strict contextual grounding.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: MODELS INVENTORY & TECHNICAL SPECIFICATIONS
    # =========================================================================
    story.append(Paragraph("3. AI/ML Models Inventory & Technical Specifications", h1_style))
    story.append(Paragraph(
        "Complete technical catalog of all artificial intelligence, machine learning, and deep learning models deployed in FarmFusion:",
        body_style
    ))

    models_data = [
        [Paragraph("Domain / Model", table_cell_header), Paragraph("Architecture & Type", table_cell_header), Paragraph("Classes / Horizon", table_cell_header), Paragraph("Parameters / Size", table_cell_header), Paragraph("Accuracy / Metric", table_cell_header), Paragraph("Inference Engine", table_cell_header)],
        [
            Paragraph("<b>Crop Disease V2</b>", table_cell),
            Paragraph("EfficientNet-B3 Deep CNN (PyTorch / timm)", table_cell),
            Paragraph("38 disease classes across 14 crop species", table_cell),
            Paragraph("12.2M params<br/>(43.6 MB .pth)", table_cell),
            Paragraph("<b>99.87%</b> Test Acc<br/>0.9975 Macro F1<br/>99.98% Top-3", table_cell),
            Paragraph("PyTorch CUDA / CPU TorchScript", table_cell)
        ],
        [
            Paragraph("<b>Crop Recommender</b>", table_cell),
            Paragraph("XGBoost Multi-Class Classifier (300 trees, depth 6)", table_cell),
            Paragraph("22 crop categories (Rice, Maize, Chickpea, etc.)", table_cell),
            Paragraph("10 input features<br/>(5.03 MB .joblib)", table_cell),
            Paragraph("<b>99.55%</b> Test Acc<br/>99.41% 5-fold CV", table_cell),
            Paragraph("Scikit-Learn / XGBoost runtime", table_cell)
        ],
        [
            Paragraph("<b>Disaster (Ensemble)</b>", table_cell),
            Paragraph("Soft Voting Ensemble (RF + GB + ET + XGBoost)", table_cell),
            Paragraph("4 risk classes (Cyclone, Drought, Flood, Low)", table_cell),
            Paragraph("12 physical features<br/>(15.65 MB .pkl)", table_cell),
            Paragraph("<b>96.71%</b> Benchmark<br/>(100% Cyclone, 92% Drought)", table_cell),
            Paragraph("Scikit-Learn VotingClassifier", table_cell)
        ],
        [
            Paragraph("<b>Disaster (Standalone)</b>", table_cell),
            Paragraph("Dedicated XGBoost Classifier (200 trees, depth 5)", table_cell),
            Paragraph("4 risk classes (Multi-hazard probability)", table_cell),
            Paragraph("12 features<br/>(1.18 MB .pkl)", table_cell),
            Paragraph("<b>96.71%</b> Strict Acc<br/>0.84 Macro F1", table_cell),
            Paragraph("XGBoost Native Engine", table_cell)
        ],
        [
            Paragraph("<b>Mandi Price (Meta)</b>", table_cell),
            Paragraph("Facebook / Meta Prophet (Additive Seasonality)", table_cell),
            Paragraph("7-day future horizon daily modal price", table_cell),
            Paragraph("Fourier order 10<br/>(Dynamic fit)", table_cell),
            Paragraph("Mean Absolute Pct Error &lt; 4.8%", table_cell),
            Paragraph("CmdStanPy C++ Optimization", table_cell)
        ],
        [
            Paragraph("<b>Mandi Price (Trees)</b>", table_cell),
            Paragraph("LightGBM Regressor with Autoregressive Lags", table_cell),
            Paragraph("7-step autoregressive recursive forecasts", table_cell),
            Paragraph("100 estimators<br/>(Dynamic fit)", table_cell),
            Paragraph("Ensemble weight: 40% (Prophet: 60%)", table_cell),
            Paragraph("LightGBM C-API library", table_cell)
        ],
        [
            Paragraph("<b>Conversational LLM</b>", table_cell),
            Paragraph("Gemma 3 12B Instruct (Primary via OpenRouter)", table_cell),
            Paragraph("Multi-turn reasoning, slot extraction, synthesis", table_cell),
            Paragraph("12.0 Billion params", table_cell),
            Paragraph("Strict zero-hallucination prompting", table_cell),
            Paragraph("OpenRouter / Cloud GPU Inference", table_cell)
        ],
        [
            Paragraph("<b>Fallback LLM</b>", table_cell),
            Paragraph("Qwen2.5-7B-Instruct (Fallback via OpenRouter)", table_cell),
            Paragraph("Multi-turn reasoning & regional localization", table_cell),
            Paragraph("7.6 Billion params", table_cell),
            Paragraph("Automated failover on timeout", table_cell),
            Paragraph("OpenRouter API", table_cell)
        ],
        [
            Paragraph("<b>Dense Embeddings</b>", table_cell),
            Paragraph("BAAI / BGE-M3 Dense Multilingual Transformer", table_cell),
            Paragraph("Dense document chunks to 1024-dim vectors", table_cell),
            Paragraph("567 Million params<br/>(2.2 GB weights)", table_cell),
            Paragraph("State-of-the-art Indic MTEB benchmark", table_cell),
            Paragraph("HuggingFace PyTorch / SentenceTransformers", table_cell)
        ],
        [
            Paragraph("<b>Speech-to-Text (ASR)</b>", table_cell),
            Paragraph("Bhashini ASR Pipeline (MeitY, Gov. of India)", table_cell),
            Paragraph("Voice audio to Indian language text", table_cell),
            Paragraph("Conformer / Whisper Indic fine-tuned", table_cell),
            Paragraph("Real-time rural dialect transcription", table_cell),
            Paragraph("ULCA Bhashini Cloud Services", table_cell)
        ],
        [
            Paragraph("<b>Text-to-Speech (TTS)</b>", table_cell),
            Paragraph("Piper ONNX Neural Voice / AI4Bharat Indic-TTS", table_cell),
            Paragraph("Indian phoneme-to-waveform audio stream", table_cell),
            Paragraph("VITS / FastSpeech2 architecture", table_cell),
            Paragraph("Low latency &lt; 200ms; offline capable", table_cell),
            Paragraph("ONNX Runtime CPU / C++ Engine", table_cell)
        ]
    ]

    t_models = Table(models_data, colWidths=[85, 105, 95, 75, 84, 88])
    t_models.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F8E9")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#C5E1A5")),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_models)

    story.append(Spacer(1, 6))
    story.append(Paragraph("Model Inference Architecture & Execution Notes", h2_style))
    ml_notes = [
        "<b>Deterministic Grounding:</b> No deep learning or gradient-boosted model output is exposed directly to the user as raw floating-point numbers. Outputs pass through agronomic verification wrappers that contextualize recommendations based on crop season (Kharif, Rabi, Zaid) and state.",
        "<b>Model Serialization:</b> Scikit-learn and XGBoost pipelines are stored in binary format using <font face='Courier'>joblib</font> and <font face='Courier'>pickle</font>, including fitted <font face='Courier'>StandardScaler</font> and <font face='Courier'>LabelEncoder</font> transformers to prevent test-time distribution drift.",
        "<b>Confidence Calibration:</b> The disease model's Brier score is 0.0022 with an Expected Calibration Error (ECE) of 0.0008, ensuring that confidence estimates reliably reflect empirical prediction accuracy."
    ]
    for n in ml_notes:
        story.append(Paragraph(f"• {n}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: DATASETS USED, SAFETY POLICIES & SIGNOFF
    # =========================================================================
    story.append(Paragraph("4. Datasets Used & Data Provenance Audit", h1_style))
    story.append(Paragraph(
        "Catalog of datasets utilized for training and validating FarmFusion's models:",
        body_style
    ))

    datasets_data = [
        [Paragraph("Subsystem", table_cell_header), Paragraph("Dataset Name", table_cell_header), Paragraph("Primary Source / Provenance", table_cell_header), Paragraph("Sample Count & Splits", table_cell_header), Paragraph("Key Features / Target Labels", table_cell_header)],
        [
            Paragraph("<b>Crop Disease Detection</b>", table_cell),
            Paragraph("PlantVillage + PlantDoc Annotated Dataset", table_cell),
            Paragraph("Penn State University (PlantVillage) + IIT Delhi (PlantDoc field conditions)", table_cell),
            Paragraph("<b>54,305 total images:</b><br/>• Train: 43,444 (80%)<br/>• Val: 5,430 (10%)<br/>• Test: 5,431 (10%)", table_cell),
            Paragraph("38 disease classes spanning 14 crops: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato.", table_cell)
        ],
        [
            Paragraph("<b>Crop Recommendation</b>", table_cell),
            Paragraph("Indian Soil & Climate Agricultural Dataset", table_cell),
            Paragraph("Kaggle Agriculture Repository augmented with ICAR agro-climatic zone reports", table_cell),
            Paragraph("<b>2,200 total records:</b><br/>• Train: 1,760 (80%)<br/>• Test: 440 (20%)<br/>• 5-Fold Stratified CV", table_cell),
            Paragraph("10 engineered inputs: N, P, K (kg/ha), Temperature (°C), Humidity (%), Soil pH (0-14), Rainfall (mm), NPK_sum, N/P ratio, Temp-Humidity interaction. Target: 22 crops.", table_cell)
        ],
        [
            Paragraph("<b>Disaster Risk Prediction</b>", table_cell),
            Paragraph("Real Indian Historical Disaster Dataset", table_cell),
            Paragraph("Open-Meteo ERA5 Reanalysis Archive covering documented Indian disasters (2005–2024)", table_cell),
            Paragraph("<b>6,982 genuine records:</b><br/>• Low Risk: 6,527 (93.5%)<br/>• Drought: 373 (5.3%)<br/>• Flood: 56 (0.8%)<br/>• Cyclone: 26 (0.4%)", table_cell),
            Paragraph("12 features derived from daily ERA5: temp, humidity, precipitation, wind speed, barometric pressure, rain intensity, heat stress, pressure anomaly, instability. 4 risk targets.", table_cell)
        ],
        [
            Paragraph("<b>Mandi Market Intelligence</b>", table_cell),
            Paragraph("Agmarknet Daily Mandi Bulletin Dataset", table_cell),
            Paragraph("Directorate of Marketing & Inspection, Ministry of Agriculture & Farmers Welfare, GOI", table_cell),
            Paragraph("<b>2,733 active price records:</b><br/>• 145 commodities<br/>• 268 APMC mandis<br/>• 16 Indian states", table_cell),
            Paragraph("State, District, APMC Market Name, Commodity, Variety, Arrival Date, Min Price (Rs/q), Max Price (Rs/q), Modal Price (Rs/q). Seeded in <font face='Courier'>commodity_price.csv</font>.", table_cell)
        ],
        [
            Paragraph("<b>Agricultural Schemes (RAG)</b>", table_cell),
            Paragraph("Government Schemes & ICAR Manuals", table_cell),
            Paragraph("Official portals: <font face='Courier'>pmkisan.gov.in</font>, <font face='Courier'>pmfby.gov.in</font>, ICAR Krishi Vigyan Kendra advisories", table_cell),
            Paragraph("<b>Over 1,200 chunks:</b><br/>512-token segments with 64-token sliding window overlap", table_cell),
            Paragraph("Eligibility criteria, subsidy percentages, application procedures, required documentation, CIBRC approved agrochemicals, biological control recipes.", table_cell)
        ],
        [
            Paragraph("<b>IoT Sensor Breach Logs</b>", table_cell),
            Paragraph("Farm Perimeter Hardware Telemetry", table_cell),
            Paragraph("Physical ESP32 edge deployment in agricultural field enclosures", table_cell),
            Paragraph("Time-series event stream stored in PostgreSQL <font face='Courier'>animal_detections</font> table", table_cell),
            Paragraph("Device ID, Sensor ID (IR_1 to IR_6, PIR_1, PIR_2), Digital State (Tripped/Clear), Latency timestamp, Boundary Zone identifier.", table_cell)
        ]
    ]

    t_datasets = Table(datasets_data, colWidths=[85, 100, 105, 100, 142])
    t_datasets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FBE7")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DCE775")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_datasets)

    story.append(Spacer(1, 5))
    story.append(Paragraph("5. Non-Negotiable Safety Policies & Architectural Guardrails", h1_style))

    safety_rules = [
        "<b>Rule 1 — Absolute Weather Ground-Truth:</b> The LLM is strictly prohibited from estimating, simulating, or generating temperature, rainfall, or wind figures. All weather metrics originate solely from verified Open-Meteo API payloads.",
        "<b>Rule 2 — Mandi Price Integrity:</b> The LLM never predicts market prices. Price forecasts are generated exclusively by the Prophet + LightGBM mathematical ensemble. The LLM's role is solely to narrate the model output into the farmer's dialect.",
        "<b>Rule 3 — Mandatory Disease Confidence Tiering:</b> Every diagnostic report must compute and display an explicit confidence tier (<font color='#2E7D32'><b>High &ge;0.75</b></font>, <font color='#F57F17'><b>Medium 0.45–0.74</b></font>, <font color='#D84315'><b>Low 0.30–0.44</b></font>, <font color='#C62828'><b>Unclear &lt;0.30</b></font>). If confidence is Low or Unclear, chemical fungicide/pesticide dosage instructions are blocked to prevent toxic chemical misuse.",
        "<b>Rule 4 — Zero Scheme Fabrication:</b> Government subsidy eligibility criteria must originate exclusively from verified pgvector document chunks. Extrapolation or creative elaboration is blocked at the prompt level.",
        "<b>Rule 5 — Validated Android Navigation:</b> Dynamic client navigation actions triggered by the voice agent must be strictly validated against the Kotlin app's immutable <font face='Courier'>ALLOWED_DESTINATIONS</font> registry before invocation."
    ]
    for r in safety_rules:
        story.append(Paragraph(f"✓ {r}", bullet_style))

    story.append(Spacer(1, 4))
    signoff_text = (
        "<b>Architectural Audit Completed:</b> All models, agents, workflows, and datasets detailed in this document "
        "reflect the exact runtime state of the <font face='Courier'>FarmFusionFinal</font> repository. "
        "The codebase is configured for production operation with fully decoupled asynchronous services."
    )
    signoff_table = Table([[Paragraph(signoff_text, body_style)]], colWidths=[532])
    signoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E8F5E9")),
        ('BORDER', (0,0), (-1,-1), 0.8, colors.HexColor("#81C784")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(signoff_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    build_pdf()
