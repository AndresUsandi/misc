import os
import sys
import json
import random

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CATEGORIES_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "categories.json")
DATA_DIR_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

TEST_SUITE_NAME = "Bookito Feature Design Benchmark v2"
TEST_SUITE_VERSION = "2.0"
PROMPTS_PER_FILE = 1000
PROMPTS_PER_CATEGORY = 20
TOTAL_CATEGORIES_EXPECTED = 54

DIFFICULTY_EASY = "Easy"
DIFFICULTY_MEDIUM = "Medium"
DIFFICULTY_HARD = "Hard"
DIFFICULTY_OPTIONS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]

PROMPT_ID_PREFIX = "FEATURE-"
FILE_NAME_PATTERN = "test_prompts_{start_id}-{end_id}.json"

# ==============================================================================
# RICH HUMAN-LIKE GENERATOR DATA STRUCTURES
# ==============================================================================

OPENER_PATTERNS = [
    "We are building {scenario} for our production platform.",
    "Our team is currently tasked with designing {scenario}.",
    "I'm working on a design proposal for {scenario}.",
    "We're running into major challenges with our existing setup and need to build {scenario}.",
    "Can you help me architect {scenario}?",
    "We need a comprehensive feature design for {scenario}.",
    "Our production workload requires {scenario}.",
    "As part of our upcoming engineering roadmap, we need to implement {scenario}.",
    "We are modernizing our infrastructure and need to design {scenario}.",
    "Hey team, we need to put together an architectural design for {scenario}."
]

BACKGROUND_CONTEXTS = [
    "Currently, our system handles approximately {scale_num} requests per second across {region_num} AWS regions, but during peak load we experience significant performance degradation.",
    "Our legacy implementation was built as a monolithic service, but as traffic grew to {scale_num} active users, operational overhead became unmanageable.",
    "We are deploying this on Kubernetes across {region_num} geographic zones with strict sub-{latency_ms}ms latency SLAs.",
    "This component will run in an edge environment with limited memory ({mem_mb} MB) and intermittent network connectivity.",
    "Our organization manages over {scale_num} records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
    "We expect the system to scale to {scale_num} concurrent connections while maintaining zero-downtime availability.",
    "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
    "Safety and reliability are critical here—failures must be isolated quickly without corrupting state or impacting downstream microservices."
]

SPECIFIC_SCENARIOS_BY_CATEGORY = {
    "Software Feature": [
        "a real-time collaborative document editing tool with conflict resolution",
        "an automated user activity audit log system with searchable exports",
        "a dynamic role-based access control (RBAC) permission management interface",
        "a contextual in-app user onboarding and feature walkthrough system",
        "an interactive data table component supporting virtualization for 50,000 rows",
        "a customizable user notification center with multi-channel preference routing",
        "a dark mode and accessibility theme switcher with design token persistence",
        "a drag-and-drop workflow visualizer for pipeline step configuration"
    ],
    "Software System": [
        "a distributed background task execution engine with priority queues",
        "a centralized feature flag management and evaluation service",
        "a multi-tenant identity, authentication, and session management system",
        "an automated software license entitlement and usage tracking platform",
        "a enterprise file management platform with version control and deduplication",
        "a high-throughput API gateway with dynamic request routing and rate limiting"
    ],
    "Distributed System": [
        "a distributed key-value storage engine using the Raft consensus protocol",
        "a multi-region active-active distributed locking service",
        "an eventual consistency state replication system using Conflict-Free Replicated Data Types (CRDTs)",
        "a distributed transaction coordinator implementing two-phase commit (2PC)",
        "a gossip-based cluster membership and node failure detection service",
        "a geo-replicated cache cluster with read-through and write-behind policies"
    ],
    "Backend/API": [
        "a high-performance GraphQL schema federation gateway for microservices",
        "an idempotent payment processing API integration with webhook callbacks",
        "a RESTful inventory management API using optimistic concurrency control",
        "a gRPC microservice interface for real-time order fulfillment processing",
        "an event-driven API backend with asynchronous task status polling",
        "a bulk data import API supporting partial success and failure reporting"
    ],
    "Frontend/UI": [
        "a virtualized data grid component rendering 100,000 real-time rows smoothly",
        "an interactive telemetry dashboard with live chart streaming and zooming",
        "a drag-and-drop Kanban board with optimistic UI updates and undo history",
        "a responsive multi-step checkout wizard with complex form field validation",
        "an offline-first WebAssembly rich text editor with Markdown export",
        "an interactive network topology visualizer using Canvas/SVG"
    ],
    "Mobile Application": [
        "a background location tracking service optimized for minimal battery drain",
        "an offline-first mobile synchronization engine with local SQLite caching",
        "a biometric authentication helper module integrating Secure Enclave storage",
        "a push notification handling framework supporting deep links and rich payloads",
        "a high-speed camera barcode and QR code scanning module for inventory",
        "a Bluetooth Low Energy (BLE) sensor telemetry ingestion application"
    ],
    "Database/Data Storage": [
        "a time-series metrics storage engine supporting automatic downsampling and retention policies",
        "a partitioned Log-Structured Merge (LSM) tree key-value storage engine",
        "a multi-version concurrency control (MVCC) relational storage engine",
        "an append-only write-ahead log (WAL) persistence manager",
        "a high-performance columnar storage index for analytical aggregations",
        "a sharded document store with automatic partition rebalancing"
    ],
    "Data Pipeline": [
        "a real-time streaming ETL pipeline processing Kafka event topics",
        "a batch data lake ingestion pipeline using Apache Spark and Parquet storage",
        "a Change Data Capture (CDC) streaming pipeline from PostgreSQL to OpenSearch",
        "a telemetry aggregation pipeline processing sliding-window sensor metrics",
        "an automated PII data masking and sanitization pipeline for analytics"
    ],
    "Search/Retrieval": [
        "a hybrid search engine combining BM25 keyword matching and vector embeddings",
        "a faceted e-commerce search engine with instant prefix autocomplete",
        "a semantic document search engine with two-stage passage reranking",
        "a real-time log search service supporting regex filtering and structured queries",
        "a geo-spatial proximity search index supporting bounding box queries"
    ],
    "Messaging/Eventing": [
        "a partitioned publish-subscribe message broker with persistent disk storage",
        "an event bus supporting event replay, deduplication, and schema validation",
        "a dead-letter queue processor with exponential backoff retry policies",
        "a transactional outbox relay service for microservice database events",
        "a high-throughput WebSocket distribution server for live updates"
    ],
    "Networking": [
        "a software-defined WAN (SD-WAN) dynamic path selection controller",
        "a WireGuard VPN tunnel orchestration and key management service",
        "a Layer 4 load balancer using consistent hashing for connection distribution",
        "a DNS-over-HTTPS (DoH) recursive resolver with caching and filtering",
        "a network packet inspection and traffic flow classification engine"
    ],
    "Network Protocol": [
        "a custom binary framing protocol for ultra-low-latency RPC communications",
        "a multiplexed stream control protocol running over QUIC transport",
        "a dynamic mesh routing protocol with link-quality cost estimation",
        "a lightweight telemetry framing protocol optimized for UDP transport",
        "a zero-copy packet serialization protocol for kernel bypass networking"
    ],
    "Cloud Infrastructure": [
        "a multi-region active-active cloud infrastructure deployment design",
        "an automated Kubernetes cluster autoscaling and node pool manager",
        "a modular Infrastructure-as-Code Terraform architecture for multi-cloud",
        "a serverless container execution engine with rapid cold-start mitigation",
        "a multi-cloud disaster recovery failover automation framework"
    ],
    "Infrastructure/Platform": [
        "an internal developer platform (IDP) for microservice scaffolding and provisioning",
        "a centralized secrets management vault integration framework",
        "a service mesh control plane setup managing Istio / Envoy proxies",
        "an internal container registry with automated vulnerability gate checks",
        "an ephemeral preview environment controller for pull requests"
    ],
    "DevOps/CI-CD": [
        "an autonomous CI/CD deployment pipeline with automated quality gates",
        "a canary deployment orchestrator with real-time metric analysis and auto-rollback",
        "a hermetic container build runner with distributed layer caching",
        "a GitOps state synchronizer enforcing cluster configuration consistency",
        "a parallelized test execution runner for large test suites"
    ],
    "Observability/Monitoring": [
        "a predictive anomaly detection engine for high-cardinality system metrics",
        "a distributed tracing collector processing OpenTelemetry trace spans",
        "a centralized log aggregation pipeline with structured field indexing",
        "a real-time alerting system with intelligent alert deduplication and grouping",
        "an application performance monitoring (APM) profiler agent"
    ],
    "Security": [
        "a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere",
        "an OAuth2 and OpenID Connect (OIDC) identity provider server design",
        "a hardware security module (HSM) interface for cryptographic key management",
        "a database column-level encryption system supporting Bring-Your-Own-Key (BYOK)",
        "a web application firewall (WAF) rule evaluation engine"
    ],
    "Reliability/Fault Tolerance": [
        "an automated multi-region database failover and replica promotion engine",
        "a circuit breaker pattern library with adaptive failure rate trip thresholds",
        "a graceful degradation controller for shedding load under extreme traffic",
        "a chaos engineering fault injection platform for testing microservices",
        "a self-healing cluster node recovery and task migration controller"
    ],
    "Performance/Scalability": [
        "a high-throughput API platform capable of processing 1,000,000 requests per second",
        "a sub-millisecond market data ingestion engine with zero memory allocations",
        "a memory-efficient lock-free concurrent queue for high-rate event processing",
        "a global content delivery network (CDN) edge caching architecture",
        "an asynchronous non-blocking I/O event loop optimization framework"
    ],
    "AI/ML Feature": [
        "an automated AI code review assistant that flags security and performance bugs",
        "a smart autocomplete suggestion engine powered by an inline language model",
        "an intelligent customer support ticket categorization and routing model",
        "an AI-driven search query expansion system for technical documentation",
        "a personalized content recommendation feature based on embedding similarity"
    ],
    "LLM/Generative AI": [
        "a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries",
        "a multi-agent LLM orchestration framework supporting dynamic tool calling",
        "a prompt caching and vector semantic deduplication layer for LLM API calls",
        "an LLM safety guardrails and input/output filtering subsystem",
        "a cost-optimized LLM router switching between fast and complex models"
    ],
    "ML Training": [
        "a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel",
        "a LoRA fine-tuning pipeline for domain-specific technical language models",
        "an automated dataset curation, deduplication, and quality filtering pipeline",
        "a machine learning feature store with synchronized online and offline tables",
        "a hyperparameter optimization orchestrator supporting distributed trials"
    ],
    "Embedded Software": [
        "a UAV flight controller firmware implementing real-time PID feedback loops",
        "an embedded RTOS task scheduler enforcing deterministic task priorities",
        "a secure bootloader firmware validating signed micro-code images",
        "a low-power IoT sensor node firmware supporting deep sleep power modes",
        "an embedded Flash file system driver with wear leveling logic"
    ],
    "Real-Time System": [
        "a real-time flight stabilization control loop running at 1000 Hz",
        "a hard real-time industrial robotics motion controller",
        "a low-latency digital signal processing (DSP) engine for live audio",
        "a real-time network packet processing pipeline using DPDK",
        "a deterministic event dispatcher for time-critical embedded hardware"
    ],
    "IoT System": [
        "a remote device management platform monitoring 2,000,000 IoT endpoints",
        "an IoT telemetry ingestion pipeline receiving high-rate MQTT messages",
        "a zero-touch IoT device provisioning and X.509 certificate enrollment system",
        "an offline IoT data synchronization manager handling spotty connectivity",
        "an IoT device fleet firmware OTA update orchestrator"
    ],
    "PCB Design": [
        "a 6-layer high-speed SDR controller PCB layout with controlled impedance traces",
        "a compact microcontroller PCB design with optimized decoupling capacitor placement",
        "a rigid-flex PCB stackup designed for wearable medical devices",
        "an RF microstrip line PCB layout with 50-ohm characteristic impedance",
        "a high-density interconnect (HDI) PCB layout utilizing microvias"
    ],
    "Digital Electronics": [
        "an FPGA-based digital logic block for high-speed signal processing",
        "a RISC-V microcontroller core System-on-Chip (SoC) peripheral bus design",
        "a high-speed memory interface controller for DDR4/DDR5 SDRAM",
        "a hardware SPI / I2C / UART bus arbiter logic module",
        "a Direct Memory Access (DMA) bus master controller core for FPGAs"
    ],
    "Analog Electronics": [
        "a low-noise analog front-end amplifier for a 24-bit high-resolution ADC",
        "a precision active bandpass filter circuit for sensor signal conditioning",
        "an instrumentation amplifier circuit design for strain gauge bridge measurement",
        "a high-side current sensing circuit with high common-mode voltage rejection",
        "a photodiode transimpedance amplifier (TIA) for optical signal detection"
    ],
    "RF Feature": [
        "an adaptive frequency hopping subsystem for drone communication links",
        "an RF spectrum monitoring and interference detection feature",
        "an automatic gain control (AGC) loop algorithm for dynamic RF signals",
        "a radar Doppler velocity extraction signal processing feature",
        "an RF transmit power control algorithm maintaining target link quality"
    ],
    "RF Hardware": [
        "a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit",
        "a high-efficiency RF power amplifier circuit for 900 MHz transmitters",
        "a double-balanced RF passive mixer circuit for frequency upconversion",
        "a voltage-controlled oscillator (VCO) circuit with minimal phase noise",
        "an RF transmit/receive (T/R) switch circuit for antenna sharing"
    ],
    "Antenna System": [
        "an airborne mesh-network node antenna system design",
        "a phased array patch antenna layout for 5G millimeter wave communications",
        "a dual-band WiFi planar inverted-F antenna (PIFA) design",
        "a circularly polarized helical antenna for satellite ground stations",
        "a directional Yagi-Uda antenna array for long-range UAV links"
    ],
    "Signal Processing": [
        "a Doppler radar signal processing pipeline for target velocity estimation",
        "a Fast Fourier Transform (FFT) spectral analysis module for real-time signals",
        "an adaptive FIR filter module for acoustic noise cancellation",
        "a Kalman filter state estimator for multi-sensor positioning fusion",
        "a digital pulse compression matched filter for radar receivers"
    ],
    "Wireless Communications": [
        "a resilient air-to-air broadband data link between autonomous UAVs",
        "a long-range LoRaWAN communication gateway network architecture",
        "a cellular LTE-M / NB-IoT connectivity subsystem for remote telemetry",
        "a custom OFDM physical layer modulation waveform implementation",
        "a multi-hop wireless mesh routing protocol for 5,000 nodes"
    ],
    "Mechanical System": [
        "a two-axis mechanical radar antenna mounting and drive assembly",
        "an IP67 ruggedized sealed enclosure for harsh outdoor environments",
        "a vibration and shock isolation mounting structure for airborne cameras",
        "a robotic joint mechanical actuator assembly using harmonic gearing",
        "a lightweight carbon fiber frame structure for industrial drones"
    ],
    "Electromechanical System": [
        "an automated antenna positioning system driven by stepper motors",
        "a brushless DC (BLDC) motor gimbal stabilizer assembly",
        "an automated valve actuator subsystem with optical position encoders",
        "a haptic feedback actuator system for handheld controllers",
        "a motorized cable winch system with active tension monitoring"
    ],
    "Power System": [
        "a complete electrical power and battery architecture for long-endurance UAVs",
        "a solar power management system with Maximum Power Point Tracking (MPPT)",
        "a dual redundant hot-swappable DC power supply architecture",
        "a high-voltage battery management system (BMS) with cell balancing logic",
        "a smart power distribution unit (PDU) with per-port current monitoring"
    ],
    "Hardware/Software Integration": [
        "a Software-Defined Radio (SDR) integration bridging hardware and DSP code",
        "a custom PCIe FPGA board Linux device driver and DMA buffer manager",
        "an embedded Hardware Abstraction Layer (HAL) bridging MCUs and applications",
        "a MIPI CSI-2 camera sensor driver integration with image processing software",
        "a hardware crypto-accelerator driver interface for TLS operations"
    ],
    "System Integration": [
        "a drone mesh-network subsystem integrated with ground control stations",
        "a legacy enterprise ERP system integration with cloud microservices",
        "a SCADA industrial control system integration with a data lake",
        "a radar sensor subsystem integration with naval tactical software",
        "an automated warehouse robotics subsystem integrated with WMS software"
    ],
    "Manufacturing/Test": [
        "an automated production test fixture for populated circuit board assemblies",
        "an end-of-line functional test station for automotive electronic control units (ECUs)",
        "an Automated Optical Inspection (AOI) pipeline for PCB quality verification",
        "an Environmental Stress Screening (ESS) thermal burn-in chamber control system",
        "an automated flashing and provisioning test rig for microcontrollers"
    ],
    "Migration/Modernization": [
        "a monolithic application migration to a microservices-based architecture",
        "a synchronous REST API platform migration to event-driven messaging",
        "an on-premise relational database migration to AWS Aurora PostgreSQL",
        "a legacy desktop application modernization to a cloud-native web application",
        "a manual deployment process migration to automated GitOps pipelines"
    ],
    "Aerospace/Airframe Design": [
        "a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload",
        "a fixed-wing composite airframe optimized for long-endurance flight",
        "a low-radar-cross-section (low-RCS) airframe geometry design",
        "a solar-powered high-altitude pseudo-satellite (HAPS) airframe structure",
        "a folding wing mechanism for tube-launched unmanned aerial vehicles"
    ],
    "Aerodynamics": [
        "a fixed-wing UAV drag reduction and longitudinal stability design",
        "a high-lift low-Reynolds-number airfoil selection for endurance UAVs",
        "a Computational Fluid Dynamics (CFD) drag analysis of external sensor pods",
        "an active flow control system for delaying boundary layer separation",
        "a transonic winglet design for high-speed UAV fuel efficiency"
    ],
    "Propulsion System": [
        "a motor and propeller selection optimization for long-endurance quadcopters",
        "a hybrid gas-electric propulsion powertrain for fixed-wing UAVs",
        "a high-efficiency Electronic Speed Controller (ESC) circuit design",
        "a ducted fan propulsion unit for indoor inspection drones",
        "a contra-rotating dual propeller propulsion system drive"
    ],
    "Mechanical Mechanism": [
        "a retractable antenna deployment mechanism for aircraft enclosures",
        "a precision pan-tilt gimbal mechanism with zero backlash gearing",
        "an emergency parachute deployment ejection mechanism for UAVs",
        "a quick-release sensor payload mounting mechanism for field use",
        "a bistable mechanical latching mechanism for deployable solar panels"
    ],
    "Structural/Load-Bearing Design": [
        "a lightweight electronics mount engineered for high-vibration aircraft",
        "a high-G crashworthy chassis frame for automotive telemetry boxes",
        "a structural Finite Element Analysis (FEA) of composite UAV wing spars",
        "a vibration isolation camera mount for aerial mapping payloads",
        "a titanium load-bearing bracket for heavy-duty flight control actuators"
    ],
    "Electrical Circuit Design": [
        "the power and control circuitry for a motorized antenna mount",
        "an overvoltage and reverse-polarity protection input circuit",
        "a multi-cell LiPo battery charging and monitoring circuit schematic",
        "a precision voltage reference and low-noise power distribution schematic",
        "a solid-state relay drive circuit for high-current industrial DC loads"
    ],
    "Power Electronics": [
        "a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics",
        "a three-phase motor inverter drive circuit for BLDC motors",
        "a synchronous buck-boost DC/DC converter for wide-range battery operation",
        "a high-power MOSFET gate driver circuit with galvanic isolation",
        "a bidirectional DC/DC converter circuit for energy storage management"
    ],
    "EMI/EMC/Noise Mitigation": [
        "a switching regulator noise mitigation strategy for sensitive RF receivers",
        "a ground loop elimination and differential signal shielding architecture",
        "a conducted emissions filter design for MIL-STD-461 compliance",
        "a radiated EMI shielding enclosure design using conductive gaskets",
        "a PCB ground plane partitioning strategy for mixed-signal boards"
    ],
    "Sensor/Instrumentation System": [
        "a current, voltage, and temperature monitoring subsystem for drone power",
        "an Inertial Measurement Unit (IMU) sensor fusion positioning subsystem",
        "a high-precision RTK GPS receiver sensor integration interface",
        "an optical flow velocity measurement sensor for GPS-denied navigation",
        "a multi-channel thermocouple temperature data logger subsystem"
    ],
    "Thermal Management": [
        "a cooling system for a 100 W RF power amplifier inside a sealed enclosure",
        "a heat pipe thermal dissipation assembly for high-density processors",
        "a forced-air convection cooling duct layout for compact avionics",
        "a liquid cooling cold plate design for high-power MOSFET modules",
        "a passive aluminum heatsink layout optimized for sealed outdoor boxes"
    ]
}

FORMAT_STYLES = [
    # Style 1: Bulleted requirements list
    "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",

    # Style 2: Conversational narrative inquiry
    "Can you walk me through the design? Specifically, I'd like to understand the component boundaries, how failure recovery works, what tradeoffs we're making, and how we should roll this out incrementally to production.",

    # Style 3: Formally structured RFC request
    "We need a complete RFC document covering:\n1. Problem Statement & Motivation\n2. System Architecture & Component Interaction\n3. Data Schema & Protocol Definitions\n4. Performance & Scalability Considerations\n5. Reliability, Security, and Operational Considerations\n6. Alternative Approaches Evaluated",

    # Style 4: Question & trade-off focus
    "What is the best architecture for this setup? Please compare at least two credible design options, highlight their pros and cons, explain how we achieve high availability and low latency, and outline the recommended implementation plan.",

    # Style 5: Concise scenario specification
    "Generate a feature design document detailing the system architecture, API endpoints, persistence strategy, error handling, performance characteristics, and deployment approach."
]

def generate_varied_human_prompt(cat_name: str, prompt_id: str, difficulty: str) -> str:
    seed_val = int(hash(prompt_id)) & 0xffffffff
    rng = random.Random(seed_val)

    scenarios = SPECIFIC_SCENARIOS_BY_CATEGORY.get(cat_name, [f"a {cat_name.lower()} subsystem"])
    scenario = rng.choice(scenarios)

    opener = rng.choice(OPENER_PATTERNS).format(scenario=scenario)
    context_template = rng.choice(BACKGROUND_CONTEXTS)
    
    scale_num = rng.choice(["5,000", "50,000", "500,000", "2,000,000", "10,000,000"])
    region_num = rng.choice(["2", "3", "5", "12"])
    latency_ms = rng.choice(["5", "10", "20", "50"])
    mem_mb = rng.choice(["128", "256", "512", "1024"])
    
    context = context_template.format(
        scale_num=scale_num,
        region_num=region_num,
        latency_ms=latency_ms,
        mem_mb=mem_mb
    )

    format_style = rng.choice(FORMAT_STYLES)

    # Vary sentence flow and line breaks
    if rng.random() > 0.5:
        prompt_text = f"{opener} {context}\n\n{format_style}"
    else:
        prompt_text = f"{opener}\n\n{context}\n\n{format_style}"

    return prompt_text

def build_single_json_file(file_index: int, categories_meta: list):
    start_id = file_index * PROMPTS_PER_FILE + 1
    end_id = (file_index + 1) * PROMPTS_PER_FILE
    file_name = FILE_NAME_PATTERN.format(start_id=start_id, end_id=end_id)
    file_path = os.path.join(DATA_DIR_PATH, file_name)

    prompts_list = []
    current_prompt_num = start_id

    for cat in categories_meta:
        cat_name = cat["name"]

        for i in range(PROMPTS_PER_CATEGORY):
            if current_prompt_num <= 1000:
                prompt_id = f"{PROMPT_ID_PREFIX}{current_prompt_num:04d}"
            else:
                prompt_id = f"{PROMPT_ID_PREFIX}{current_prompt_num}"

            difficulty = DIFFICULTY_OPTIONS[(current_prompt_num + i) % len(DIFFICULTY_OPTIONS)]
            prompt_text = generate_varied_human_prompt(cat_name, prompt_id, difficulty)

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
    print(f"Generating 100 dataset files (test_prompts_1-1000.json to test_prompts_99001-100000.json)...")

    # File 0: 1 to 1000 (test_prompts_1-1000.json)
    # File 1..99: 1001..100000 (test_prompts_1001-2000.json ... test_prompts_99001-100000.json)
    for file_index in range(0, 100):
        build_single_json_file(file_index, categories_meta)
        if file_index % 10 == 0 or file_index == 99:
            print(f"Generated up to file index {file_index}...")

    print("Generation complete! All 100 files successfully created with high-variance human-like prompts.")

if __name__ == "__main__":
    main()
