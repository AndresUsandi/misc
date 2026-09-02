import os
import sys
import json

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CATEGORIES_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "categories.json")
DATA_DIR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

TEST_SUITE_NAME = "Bookito Feature Design Benchmark v2"
TEST_SUITE_VERSION = "2.0"
PROMPTS_PER_FILE = 1000
PROMPTS_PER_CATEGORY = 20
TOTAL_CATEGORIES_EXPECTED = 54
START_FILE_INDEX = 1
END_FILE_INDEX = 99

DIFFICULTY_EASY = "Easy"
DIFFICULTY_MEDIUM = "Medium"
DIFFICULTY_HARD = "Hard"
DIFFICULTY_OPTIONS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]

PROMPT_ID_PREFIX = "FEATURE-"
FILE_NAME_PATTERN = "test_prompts_{start_id}-{end_id}.json"

DOMAINS_BY_CATEGORY = {
    "Software Feature": [
        "collaborative real-time canvas editing",
        "customizable audit logging with compliance exports",
        "role-based access control with dynamic permission rules",
        "dark mode and high-contrast accessibility themes",
        "multi-factor authentication with hardware security keys",
        "automated notification preference center",
        "in-app context-aware feature walkthroughs",
        "interactive data grid export to Excel and PDF",
        "saved search views and filter presets",
        "drag-and-drop workflow step builder"
    ],
    "Software System": [
        "distributed task scheduling engine",
        "centralized feature flag management platform",
        "multi-tenant identity and session management system",
        "automated software license entitlement engine",
        "enterprise document management and versioning system",
        "scalable API gateway and request routing system",
        "centralized configuration management platform",
        "asynchronous notification dispatch engine",
        "automated webhook subscription and delivery platform",
        "unified developer portal and catalog system"
    ],
    "Distributed System": [
        "distributed key-value store with raft consensus",
        "multi-region active-active distributed lock manager",
        "eventual consistency CRDT state replication engine",
        "distributed transaction coordinator using 2PC",
        "gossip-based node discovery and membership cluster",
        "partitioned vector index with distributed query routing",
        "distributed rate limiter across global edge locations",
        "geo-replicated distributed cache with read-through",
        "leaderless quorum-replicated storage engine",
        "distributed lease and coordinator election service"
    ],
    "Backend/API": [
        "high-performance GraphQL schema federation gateway",
        "idempotent payment processing API with webhooks",
        "RESTful inventory control API with optimistic locking",
        "gRPC microservice interface for order fulfillment",
        "event-driven API backend with async response polling",
        "bulk batch import API with partial failure recovery",
        "dynamic filter and aggregation query backend",
        "versioned external API with deprecation headers",
        "rate-limited third-party integration proxy API",
        "JWT token validation and refresh token backend"
    ],
    "Frontend/UI": [
        "virtualized data table component rendering 100k rows",
        "interactive real-time telemetry analytics dashboard",
        "drag-and-drop Kanban board with optimistic UI updates",
        "responsive multi-step checkout wizard with validation",
        "accessible rich text block editor with markdown import",
        "interactive topology chart visualizer using SVG/Canvas",
        "dynamic form schema renderer with conditional logic",
        "offline-first WebAssembly document editor UI",
        "real-time chat and notification panel widget",
        "themeable component library design token system"
    ],
    "Mobile Application": [
        "background location tracking with battery optimization",
        "offline data synchronization with conflict resolution",
        "biometric authentication and secure key storage",
        "push notification payload handler and deep-linking",
        "camera-based barcode and QR code scanner module",
        "BLE device discovery and telemetry streaming app",
        "on-device audio recorder with noise cancellation",
        "incremental media download manager with resume support",
        "augmented reality product placement view",
        "cross-platform React Native / Flutter bridge module"
    ],
    "Database/Data Storage": [
        "time-series metrics storage engine with downsampling",
        "partitioned LSM-tree key-value storage engine",
        "multi-version concurrency control (MVCC) transactional store",
        "append-only write-ahead log (WAL) storage subsystem",
        "columnar analytical database index for fast aggregations",
        "sharded document database with automatic rebalancing",
        "graph storage subsystem with fast adjacency traversal",
        "encrypted object storage bucket with lifecycle rules",
        "distributed spatial index using R-tree bounds",
        "in-memory snapshot and persistence journal store"
    ],
    "Data Pipeline": [
        "real-time streaming ETL pipeline processing Kafka events",
        "batch data lake ingestion pipeline with Spark/Flink",
        "change data capture (CDC) pipeline from PostgreSQL",
        "telemetry aggregation pipeline with sliding window analytics",
        "data deduplication and schema validation ingestion flow",
        "multi-stage enrichment pipeline for clickstream logs",
        "real-time anomaly detection pipeline on sensor data",
        "automated data masking and PII sanitization pipeline",
        "cross-cloud data replication pipeline with retry queues",
        "serverless data processing pipeline triggering on S3 events"
    ],
    "Search/Retrieval": [
        "hybrid BM25 and vector embedding search engine",
        "faceted e-commerce search with instant autocomplete",
        "semantic document search with passage reranking",
        "real-time log search engine with regex field filtering",
        "geo-spatial proximity search engine with radius bounds",
        "multilingual document indexing and search engine",
        "fuzzy typo-tolerant search index with n-gram tokens",
        "distributed inverted index with term frequency scoring",
        "personalized recommendation search engine using embeddings",
        "code search engine indexing AST nodes and symbols"
    ],
    "Messaging/Eventing": [
        "partitioned publish-subscribe message broker",
        "persistent event bus with replay capability",
        "dead-letter queue handler and automatic retry engine",
        "transactional outbox processor for microservice events",
        "message priority queue with strict ordering guarantees",
        "event schema registry with backward compatibility checks",
        "high-throughput WebSocket event distribution broker",
        "distributed queue with at-least-once delivery guarantee",
        "message deduplication and dedupe window manager",
        "cross-datacenter event mirror maker broker"
    ],
    "Networking": [
        "software-defined WAN (SD-WAN) path selection engine",
        "virtual private network (VPN) wireguard tunnel manager",
        "border gateway protocol (BGP) route reflector controller",
        "layer 4 load balancer with consistent hash routing",
        "DNS-over-HTTPS (DoH) recursive resolver service",
        "packet inspection and flow classification engine",
        "network topology discovery controller using LLDP",
        "IP address management (IPAM) subnet allocation system",
        "multicast traffic router for high-rate video streams",
        "network quality monitoring agent measuring jitter/loss"
    ],
    "Network Protocol": [
        "custom binary framing protocol for low-latency RPC",
        "multiplexed stream protocol over QUIC transport",
        "mesh routing protocol with dynamic link cost discovery",
        "secure peer-to-peer handshaking and key exchange protocol",
        "lightweight IoT telemetry framing protocol over UDP",
        "zero-copy packet serialization protocol for kernel bypass",
        "adaptive bitrate streaming control protocol",
        "heartbeat and health exchange protocol for clusters",
        "forward error correction (FEC) frame header protocol",
        "distributed clock synchronization protocol over PTP"
    ],
    "Cloud Infrastructure": [
        "multi-region cloud infrastructure for high availability",
        "automated Kubernetes cluster autoscaler and provisioner",
        "infrastructure-as-code terraform module architecture",
        "serverless function runtime container pool manager",
        "hybrid cloud cloudbursting controller for burst compute",
        "cloud egress bandwidth optimization proxy pool",
        "multi-cloud disaster recovery failover controller",
        "cloud spot instance allocation and migration engine",
        "zero-downtime VPC peering and transit gateway design",
        "cloud resource cost optimization and rightsizing engine"
    ],
    "Infrastructure/Platform": [
        "internal developer platform for microservice bootstrapping",
        "centralized secrets management vault integration",
        "shared service mesh control plane (Istio/Envoy)",
        "internal container registry with vulnerability scanning",
        "unified telemetry collection agent for host metrics",
        "platform multi-tenant workspace isolation manager",
        "ephemeral preview environment automation platform",
        "shared background job worker platform with queue priorities",
        "internal database-as-a-service provisioning platform",
        "platform compliance policy enforcement engine"
    ],
    "DevOps/CI-CD": [
        "autonomous CI/CD deployment pipeline with quality gates",
        "canary deployment deployment manager with automated rollback",
        "hermetic build container runner with artifact caching",
        "gitops deployment synchronizer monitoring repository state",
        "security static analysis (SAST) pipeline scanner integration",
        "automated database migration rollout pipeline",
        "parallel test execution orchestrator for large test suites",
        "blue/green deployment switcher with zero-downtime DNS",
        "multi-architecture container image builder pipeline",
        "release notes generation and changelog tag pipeline"
    ],
    "Observability/Monitoring": [
        "predictive anomaly detection engine for system metrics",
        "distributed tracing collector processing OpenTelemetry spans",
        "centralized log aggregation pipeline with field indexing",
        "real-time alerting rule engine with alert deduplication",
        "synthetic uptime monitoring runner with SLA reports",
        "application performance monitoring (APM) profiler agent",
        "high-cardinality metrics storage and querying system",
        "health status page generator with incident history",
        "cost allocation and resource utilization telemetry monitor",
        "root cause analysis correlation engine for outages"
    ],
    "Security": [
        "zero-trust microservice mutual TLS authentication system",
        "OAuth2 / OpenID Connect authorization server architecture",
        "hardware security module (HSM) key management subsystem",
        "database column-level field encryption engine with BYOK",
        "web application firewall (WAF) rule inspection engine",
        "runtime application self-protection (RASP) security agent",
        "automated vulnerability scanning and patch manager",
        "privileged access management (PAM) password vault",
        "security event and incident management (SIEM) ingestion platform",
        "threat detection engine monitoring behavior anomaly patterns"
    ],
    "Reliability/Fault Tolerance": [
        "multi-region automated database failover controller",
        "circuit breaker pattern library with adaptive trip thresholds",
        "graceful degradation engine under extreme resource load",
        "chaos engineering fault injection testing framework",
        "self-healing node recovery controller for cluster nodes",
        "replica state reconciliation engine after network partition",
        "disaster recovery backup and point-in-time restore system",
        "rate limiting and traffic shedding load governor",
        "immutable data snapshot backup verification service",
        "high-availability active/standby state machine replicator"
    ],
    "Performance/Scalability": [
        "high-throughput API platform supporting 1M req/sec",
        "low-latency sub-millisecond market data ingestion engine",
        "memory-efficient zero-copy data processing pipeline",
        "horizontal auto-scaling strategy based on queue depth",
        "CPU cache-friendly lock-free concurrent data structures",
        "database query optimization and index tuning architecture",
        "global content delivery network (CDN) edge cache architecture",
        "high-density connection multiplexer for 10M WebSockets",
        "asynchronous non-blocking I/O event loop optimization",
        "bulk processing pipeline with vectorized SIMD operations"
    ],
    "AI/ML Feature": [
        "AI code review assistant detecting security vulnerabilities",
        "smart autocomplete suggestion engine for user inputs",
        "automated document classification and tag extraction",
        "ai-powered search query intent expansion engine",
        "intelligent customer support ticket routing model",
        "personalized content recommendation feature",
        "ai-driven image background removal and enhancement",
        "automated speech-to-text transcript generator",
        "smart anomaly scoring feature for financial transactions",
        "ai summary generation feature for lengthy legal contracts"
    ],
    "LLM/Generative AI": [
        "retrieval-augmented generation (RAG) assistant for tech docs",
        "multi-agent orchestration framework with tool calling",
        "streaming LLM response token buffer with markdown parsing",
        "prompt caching and semantic vector deduplication layer",
        "LLM guardrails and safety filter subsystem",
        "fine-tuned LLM inference service with vLLM/TGI optimization",
        "long-context document chunking and vector embedding engine",
        "interactive AI pair programmer integration for IDEs",
        "autonomous AI agent memory store with episodic storage",
        "cost-optimized model routing engine switching LLMs dynamically"
    ],
    "ML Training": [
        "distributed multi-GPU model training pipeline using PyTorch",
        "LoRA fine-tuning pipeline for domain-specific LLMs",
        "automated dataset curation, deduplication, and labeling flow",
        "machine learning feature store with offline/online sync",
        "model hyperparameter tuning orchestrator with Ray/Optuna",
        "continuous model evaluation and drift detection pipeline",
        "synthetic training data generation pipeline using LLMs",
        "reinforcement learning from human feedback (RLHF) pipeline",
        "model checkpointing and distributed model storage engine",
        "onnx / tensorrt model quantization and export pipeline"
    ],
    "Embedded Software": [
        "uav flight controller firmware with real-time PID loops",
        "embedded RTOS task scheduler with deterministic priorities",
        "secure bootloader firmware with cryptographic signature validation",
        "low-power sensor node firmware with deep sleep cycles",
        "bare-metal SPI/I2C driver stack for hardware peripherals",
        "embedded flash file system (SPIFFS/LittleFS) wear leveling",
        "CAN bus message parser and diagnostic firmware",
        "embedded OTA firmware update manager with dual-bank flash",
        "motor driver control firmware with field-oriented control (FOC)",
        "watchdog timer and crash dump recovery subsystem"
    ],
    "Real-Time System": [
        "real-time flight stabilization control loop",
        "hard real-time industrial robotics motion controller",
        "low-latency audio digital signal processing engine",
        "real-time packet processing engine with DPDK",
        "deterministic real-time event dispatcher for embedded HW",
        "real-time telemetry processing with bounded deadline latency",
        "high-frequency trading order matching engine",
        "real-time video frame processing pipeline at 120 FPS",
        "time-triggered Ethernet protocol stack for automotive",
        "real-time closed-loop sensor feedback controller"
    ],
    "IoT System": [
        "remote management platform for 2 million IoT devices",
        "IoT device telemetry ingestion pipeline over MQTT",
        "zero-touch IoT device provisioning and certificate enrollment",
        "intermittent connectivity IoT data sync manager",
        "IoT device fleet firmware OTA update orchestrator",
        "edge compute device runtime running lightweight containers",
        "IoT device battery life optimization monitoring service",
        "geofencing alert system for mobile IoT asset trackers",
        "IoT gateway protocol translator (Modbus to MQTT)",
        "device shadow state synchronization manager"
    ],
    "PCB Design": [
        "high-speed SDR communications controller PCB design",
        "4-layer micro-controller board layout with impedance control",
        "power distribution network (PDN) decoupling capacitor placement",
        "rigid-flex PCB stackup for compact wearable devices",
        "RF microstrip line layout with controlled 50-ohm trace width",
        "high-density interconnect (HDI) PCB layout with microvias",
        "thermal pad ground plane layout for high-current MOSFETs",
        "differential pair signal routing for USB 3.0 / PCIe",
        "ESD protection diode layout near connector interfaces",
        "PCB manufacturing testpoint layout for automated ICT"
    ],
    "Digital Electronics": [
        "FPGA-based high-speed signal processing hardware",
        "RISC-V core microcontroller system-on-chip (SoC) design",
        "high-speed memory interface controller for DDR4 / DDR5",
        "SPI / I2C / UART digital logic bus arbiter module",
        "hardware pulse-width modulation (PWM) generator core",
        "digital phase-locked loop (DPLL) clock generator circuit",
        "hardware AES encryption accelerator logic module",
        "digital logic state machine for hardware handshake protocol",
        "direct memory access (DMA) bus master controller",
        "FPGA logic module for real-time video pattern generation"
    ],
    "Analog Electronics": [
        "low-noise analog front-end amplifier for high-res ADC",
        "precision active bandpass filter for sensor signal conditioning",
        "instrumentation amplifier circuit for strain gauge bridge",
        "current sensing amplifier circuit with high common-mode voltage",
        "analog phase detector circuit for RF signal processing",
        "low-distortion sine wave oscillator circuit design",
        "analog voltage reference buffer with minimal thermal drift",
        "photodiode transimpedance amplifier (TIA) for optical sensing",
        "analog audio preamplifier circuit with low total harmonic distortion",
        "analog peak detector circuit for fast pulse acquisition"
    ],
    "RF Feature": [
        "adaptive frequency hopping for drone communication links",
        "RF spectrum monitoring and interference detection feature",
        "automatic gain control (AGC) loop for dynamic signal range",
        "RF signal RSSI estimation and link quality monitoring",
        "radar target Doppler velocity extraction feature",
        "RF transmit power control algorithm based on link quality",
        "software-defined radio (SDR) waveform switching feature",
        "beamforming phased array steering angle control",
        "RF carrier frequency offset (CFO) compensation feature",
        "radio direction finding (RDF) angle-of-arrival estimation"
    ],
    "RF Hardware": [
        "2.4 GHz low-noise RF receiver front-end amplifier",
        "high-efficiency RF power amplifier circuit for 900 MHz",
        "double-balanced RF passive mixer circuit for upconversion",
        "RF surface acoustic wave (SAW) bandpass filter circuit",
        "voltage-controlled oscillator (VCO) circuit with low phase noise",
        "RF directional coupler circuit for power monitoring",
        "quadrature IQ modulator / demodulator RF frontend",
        "RF impedance matching network using LC components",
        "RF switch circuit for transmit/receive (T/R) switching",
        "broadband RF attenuator circuit with digital control"
    ],
    "Antenna System": [
        "airborne mesh-network node antenna system design",
        "phased array patch antenna array for 5G / SATCOM",
        "dual-band WiFi planar inverted-F antenna (PIFA) design",
        "ultra-wideband (UWB) monopole antenna for positioning",
        "circularly polarized helical antenna for satellite telemetry",
        "compact ceramic chip antenna integration for IoT devices",
        "monopole whip antenna matching circuit for 433 MHz",
        "directional Yagi-Uda antenna array for long-range UAV link",
        "conformal antenna array embedded in airframe structure",
        "antenna diversity switch architecture for multipath mitigation"
    ],
    "Signal Processing": [
        "Doppler radar signal processing for target detection",
        "fast Fourier transform (FFT) spectral analyzer module",
        "adaptive FIR filter for acoustic noise cancellation",
        "quadrature amplitude modulation (QAM) demodulator engine",
        "kalman filter algorithm for sensor fusion positioning",
        "wavelet transform decomposition for ECG signal analysis",
        "digital matched filter for radar pulse compression",
        "beamforming spatial filtering algorithm for microphone arrays",
        "signal envelope detection and peak extraction algorithm",
        "blind channel estimation algorithm for wireless links"
    ],
    "Wireless Communications": [
        "resilient air-to-air broadband data link between UAVs",
        "long-range LoRaWAN communication network architecture",
        "cellular LTE-M / NB-IoT connectivity subsystem",
        "custom OFDM physical layer waveform design",
        "mesh network routing for 5,000 wireless nodes",
        "satellite-to-ground telemetry broadband link architecture",
        "cognitive radio link with automatic spectrum sensing",
        "ultra-low latency wireless audio transmission link",
        "wireless channel equalizer for severe multipath fading",
        "secure encrypted RF telemetry transmission architecture"
    ],
    "Mechanical System": [
        "two-axis mechanical radar mounting and drive system",
        "rugged sealed enclosure for harsh outdoor environments (IP67)",
        "shock and vibration isolation mount for airborne camera",
        "robotic arm joint mechanical assembly with harmonic drive",
        "precision optical payload gimbal mechanical structure",
        "waterproof connectors and cable strain relief assembly",
        "modular rackmount chassis enclosure with airflow ducts",
        "drone landing gear deployment mechanical system",
        "heavy-load linear actuator mechanical drive assembly",
        "thermal expansion joint assembly for high-temp ducting"
    ],
    "Electromechanical System": [
        "automated antenna positioning system with motor drives",
        "stepper motor drive controller with encoder feedback",
        "electromechanical solenoid latching mechanism",
        "brushless DC (BLDC) motor gimbal stabilizer assembly",
        "automated valve actuator subsystem with position sensing",
        "linear encoder feedback position control system",
        "haptic feedback actuator system for handheld controller",
        "robotic gripper mechanism with force sensor feedback",
        "pan-tilt servo camera platform with optical encoders",
        "motorized cable winch system with tension control"
    ],
    "Power System": [
        "battery and power architecture for long-endurance UAV",
        "solar power management and MPPT charger system",
        "dual redundant hot-swappable power supply architecture",
        "uninterruptible power supply (UPS) controller with LiFePO4",
        "smart power distribution unit (PDU) with current monitoring",
        "high-voltage battery management system (BMS) with cell balancing",
        "fuel cell power integration for remote monitoring stations",
        "power budgeting and load shedding power supervisor",
        "ultra-capacitor pulse power buffer for high-current loads",
        "energy harvesting power circuit from thermoelectric generators"
    ],
    "Hardware/Software Integration": [
        "sdr radio integration with real-time processing software",
        "linux kernel device driver for custom PCIe FPGA card",
        "embedded HAL layer bridging MCU hardware and application",
        "camera sensor MIPI CSI-2 driver integration with OpenCV",
        "hardware acceleration engine driver interface for cryptography",
        "i2c sensor driver module with DMA background transfer",
        "hardware interrupt service routine (ISR) latency optimizer",
        "usb device controller stack integration (CDC/HID/MSC)",
        "can bus driver integration with AUTOSAR stack",
        "fpga register map C header generator and HAL driver"
    ],
    "System Integration": [
        "drone mesh-network subsystem with ground control station",
        "legacy ERP system integration with cloud microservices",
        "scada industrial control system integration with enterprise data lake",
        "radar sensor subsystem integration with combat management system",
        "electronic health record (EHR) integration with hospital API",
        "telemetry subsystem integration with third-party analytics",
        "payment gateway integration with POS hardware terminals",
        "automated warehouse robotics integration with WMS software",
        "fleet management GPS tracker integration with dispatch platform",
        "building management system (BMS) integration with HVAC controls"
    ],
    "Manufacturing/Test": [
        "automated production test fixture for newly made PCBs",
        "end-of-line functional test station for automotive ECUs",
        "automated optical inspection (AOI) verification pipeline",
        "flying probe PCB circuit continuity test procedure",
        "environmental stress screening (ESS) thermal burn-in chamber setup",
        "calibration fixture for precision analog sensor modules",
        "automated flashing and provisioning test rig for MCUs",
        "manufacturing assembly line traceability barcode scanner system",
        "rf automated test equipment (ATE) setup with spectrum analyzer",
        "battery pack capacity and internal resistance test station"
    ],
    "Migration/Modernization": [
        "monolithic backend migration to microservices architecture",
        "synchronous REST API migration to asynchronous event broker",
        "on-premise Oracle DB migration to PostgreSQL AWS Aurora",
        "legacy AngularJS application modernization to modern React",
        "bare-metal server deployment migration to Kubernetes containers",
        "soap web service API migration to RESTful OpenAPI standards",
        "legacy mainframe batch processing migration to Apache Spark",
        "python 2 legacy codebase migration to async Python 3.12",
        "self-hosted ElasticSearch migration to OpenSearch cluster",
        "manual deployment process migration to GitOps automated pipeline"
    ],
    "Aerospace/Airframe Design": [
        "vtol drone airframe capable of carrying 5 kg payload",
        "fixed-wing long-endurance composite airframe layout",
        "stealth low-RCS airframe geometry and wing root blend",
        "quadcopter carbon fiber frame structural optimization",
        "solar-powered high-altitude pseudo-satellite (HAPS) airframe",
        "folding wing mechanism for tube-launched UAV",
        "payload bay door geometry and structural latch design",
        "lightweight wing spar layup design using carbon fiber",
        "amphibious UAV hull and float hydrodynamic/aerodynamic design",
        "modular airframe nosecone replacement system for sensors"
    ],
    "Aerodynamics": [
        "fixed-wing UAV longitudinal stability and drag reduction",
        "high-lift low-Reynolds-number airfoil geometry selection",
        "propeller slipstream interaction on wing lift distribution",
        "computational fluid dynamics (CFD) drag analysis of payload pod",
        "active flow control surface for boundary layer separation",
        "transonic winglet design for high-speed UAV fuel efficiency",
        "rotor blade pitch angle optimization for multirotor thrust",
        "vortex generator placement to delay stall on heavy UAV",
        "wind tunnel test model design for aerodynamic force balance",
        "airframe drag polar estimation and gliding ratio optimizer"
    ],
    "Propulsion System": [
        "motor and propeller selection for long-endurance drone",
        "hybrid gas-electric propulsion powertrain for fixed-wing UAV",
        "high-efficiency electronic speed controller (ESC) design",
        "ducted fan propulsion system for indoor inspection drone",
        "turboprop engine integration for medium-altitude UAV",
        "propeller thrust test bench with dynamic load cell sensors",
        "contra-rotating dual propeller propulsion drive setup",
        "brushless motor thermal cooling jacket and heatsink setup",
        "engine starter-generator integration for hybrid UAV",
        "propeller pitch control mechanism for constant-speed drive"
    ],
    "Mechanical Mechanism": [
        "retractable antenna deployment mechanism for aircraft",
        "precision pan-tilt gimbal mechanism with zero backlash",
        "parachutes deployment ejection mechanism for UAV emergency recovery",
        "folding propeller blade mechanism for airborne gliding",
        "quick-release sensor payload mounting mechanism",
        "geneva drive mechanism for indexing mechanical test samples",
        "bistable mechanical latch for solar panel deployment",
        "cam-driven linear slider mechanism for automated testing",
        "harmonic drive gear reduction system for robot joints",
        "telescoping mast elevation mechanism for ground sensors"
    ],
    "Structural/Load-Bearing Design": [
        "lightweight electronics mount for sustained aircraft vibration",
        "high-g crashworthy chassis frame for automotive sensor box",
        "composite payload bay bulkhead structural FEA analysis",
        "vibration damping mount for sensitive optical cameras",
        "structural finite element analysis (FEA) of drone arms",
        "fatigue life estimation for aluminum airframe wing attachment",
        "shock absorption mount for rugged field equipment",
        "titanium load-bearing bracket for aerospace actuators",
        "honeycomb sandwich panel structural layout for satellite",
        "thermal expansion stress relief mount for hot exhaust duct"
    ],
    "Electrical Circuit Design": [
        "power and control circuitry for motorized antenna mount",
        "overvoltage and reverse polarity protection circuit",
        "battery charger circuit for multi-cell LiPo battery",
        "precision voltage reference and distribution circuit",
        "microcontroller pin breakout and ESD protection schematic",
        "solid-state relay drive circuit for high-power DC loads",
        "galvanic isolation circuit for industrial sensor signals",
        "analog signal conditioning schematic for strain gauge",
        "power-on reset (POR) and brownout detector circuit",
        "low-side current sense amplifier circuit schematic"
    ],
    "Power Electronics": [
        "high-efficiency 48 V to 12 V DC/DC buck converter for UAV",
        "three-phase inverter drive circuit for BLDC motors",
        "synchronous buck-boost converter for wide input batteries",
        "high-power MOSFET gate driver circuit with isolation",
        "bidirectional DC/DC converter for battery energy storage",
        "soft-start power switch circuit for high capacitive loads",
        "power factor correction (PFC) boost stage for AC/DC power supply",
        "resonant LLC converter circuit for high-efficiency power supply",
        "gallium nitride (GaN) FET power stage for high-frequency DC/DC",
        "active cell balancing circuit for lithium battery packs"
    ],
    "EMI/EMC/Noise Mitigation": [
        "switching regulator noise mitigation in sensitive RF receiver",
        "ground loop elimination and differential signal shielding",
        "common-mode choke selection for high-speed data lines",
        "ferrite bead filtering circuit for power supply rails",
        "conducted emissions filtering for MIL-STD-461 compliance",
        "radiated EMI shielding enclosure design with conductive gaskets",
        "pcb ground plane split and return path optimization",
        "esd transient voltage suppressor (TVS) diode array layout",
        "clock signal spread spectrum frequency modulation setup",
        "rf shielding can design for high-gain amplifier board"
    ],
    "Sensor/Instrumentation System": [
        "current, voltage, and temp monitoring subsystem for drone",
        "inertial measurement unit (IMU) sensor fusion subsystem",
        "high-precision RTK GPS receiver sensor integration",
        "optical flow velocity sensor for GPS-denied navigation",
        "barometric altimeter sensor conditioning and ADC setup",
        "multi-channel thermocouple temperature data logger",
        "lidar distance measurement sensor interface circuit",
        "piezoelectric vibration monitoring sensor system",
        "gas concentration sensor array with temperature calibration",
        "rotary optical encoder interface for precision motor sensing"
    ],
    "Thermal Management": [
        "cooling for 100 W RF amplifier in sealed enclosure",
        "heat pipe thermal dissipation system for high-power CPU",
        "phase-change material (PCM) heat sink for transient loads",
        "forced-air convection cooling duct layout for electronics",
        "liquid cooling cold plate design for high-density power FETs",
        "thermal interface material (TIM) selection for MOSFETs",
        "thermoelectric cooler (TEC) temperature controller circuit",
        "passive aluminum fin heatsink optimization for sealed boxes",
        "thermal modeling and CFD simulation of PCB components",
        "temperature-controlled fan speed regulator subsystem"
    ]
}

CONSTRAINTS_LIST = [
    "Explicitly address backward compatibility, incremental rollout, and observability.",
    "Explicitly address operational simplicity, clear failure recovery, and future extensibility.",
    "Explicitly address regional failure tolerance, sub-second latency, and data consistency.",
    "Explicitly address local autonomy, recovery after reconnect, and bandwidth efficiency.",
    "Explicitly address low operational burden, incremental adoption, and cost constraints.",
    "Explicitly address fault detection, safe fallback behavior, and high testability.",
    "Explicitly address backpressure, horizontal scaling, and capacity planning.",
    "Explicitly address zero-trust security boundaries, encryption at rest, and audit logging.",
    "Explicitly address deterministic execution deadlines, low jitter, and real-time bounds.",
    "Explicitly address automated regression testing, CI/CD safety gates, and canary rollouts."
]

EXPECTATIONS_LIST = [
    "Identify assumptions and unresolved technical questions, compare at least two credible implementation approaches with pros and cons, and include failure modes, validation strategy, and rollout plans.",
    "Produce a complete feature design document with functional and non-functional requirements, recommended architecture, high-level diagrams, conceptual components, data models, tradeoff analysis, and next steps.",
    "Detail the architectural blueprint, data flow diagrams, API interfaces, failure scenarios, performance benchmarks, and deployment strategy.",
    "Provide a rigorous technical evaluation, system component design, security model, data retention policy, and operational runbook outlines.",
    "Deliver a comprehensive design specification covering domain modeling, communication protocols, fault recovery mechanisms, and scaling limits."
]

def generate_prompt_text(cat_name: str, topic: str, prompt_id: str, difficulty: str) -> str:
    constraint = CONSTRAINTS_LIST[hash(prompt_id) % len(CONSTRAINTS_LIST)]
    expectation = EXPECTATIONS_LIST[hash(prompt_id) % len(EXPECTATIONS_LIST)]

    lines = [
        f"We need to design and implement a {topic} in our engineering platform.",
        f"This system is categorized under {cat_name} and represents a {difficulty.lower()} difficulty architectural challenge.",
        "",
        "Key constraints and expectations:",
        f"- {constraint}",
        "",
        expectation
    ]
    return "\n".join(lines)

def build_single_json_file(file_index: int, categories_meta: list):
    start_id = file_index * PROMPTS_PER_FILE + 1
    end_id = (file_index + 1) * PROMPTS_PER_FILE
    file_name = FILE_NAME_PATTERN.format(start_id=start_id, end_id=end_id)
    file_path = os.path.join(DATA_DIR_PATH, file_name)

    prompts_list = []
    current_prompt_num = start_id

    # Generate 20 prompts per category = 1000 prompts total
    for cat in categories_meta:
        cat_name = cat["name"]
        topics = DOMAINS_BY_CATEGORY.get(cat_name, [f"{cat_name} subsystem solution"])

        for i in range(PROMPTS_PER_CATEGORY):
            prompt_id = f"{PROMPT_ID_PREFIX}{current_prompt_num}"
            topic = topics[i % len(topics)]
            difficulty = DIFFICULTY_OPTIONS[(current_prompt_num + i) % len(DIFFICULTY_OPTIONS)]
            prompt_text = generate_prompt_text(cat_name, topic, prompt_id, difficulty)

            prompts_list.append({
                "id": prompt_id,
                "primaryCategory": cat_name,
                "difficulty": difficulty,
                "prompt": prompt_text
            })
            current_prompt_num += 1

    file_data = {
        "testSuite": TEST_SUITE_NAME,
        "version": TEST_SUITE_VERSION,
        "promptCount": PROMPTS_PER_FILE,
        "categoryCount": TOTAL_CATEGORIES_EXPECTED,
        "promptsPerCategory": PROMPTS_PER_CATEGORY,
        "prompts": prompts_list
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

def main():
    if not os.path.exists(CATEGORIES_FILE_PATH):
        print(f"Error: {CATEGORIES_FILE_PATH} does not exist.")
        sys.exit(1)

    with open(CATEGORIES_FILE_PATH, "r", encoding="utf-8") as f:
        cat_data = json.load(f)

    raw_categories = cat_data.get("categories", [])
    categories_meta = []
    for c in raw_categories:
        categories_meta.append({
            "name": c["name"],
            "description": c.get("description", ""),
            "promptCount": PROMPTS_PER_CATEGORY
        })

    print(f"Loaded {len(categories_meta)} categories from {CATEGORIES_FILE_PATH}.")
    print(f"Generating 99 dataset files from test_prompts_1001-2000.json to test_prompts_99001-100000.json...")

    for file_index in range(START_FILE_INDEX, END_FILE_INDEX + 1):
        build_single_json_file(file_index, categories_meta)
        if file_index % 10 == 0 or file_index == END_FILE_INDEX:
            print(f"Generated up to file index {file_index} ({file_index * PROMPTS_PER_FILE + 1}-{(file_index + 1) * PROMPTS_PER_FILE})...")

    print("Generation complete! All 99 files successfully created in data/.")

if __name__ == "__main__":
    main()
