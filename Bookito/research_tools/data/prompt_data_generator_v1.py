# ============================================================================
# Bookito Feature Design Benchmark - Typed Template Knowledge Base (v2.1)
# Fine-Grained Architectural Paradigms & Syntactic Rephrasings (Option B)
# ============================================================================

TYPED_TEMPLATE_SLOTS = {
    "microservice_architecture": [
        "prior microservice deployment strategy",
        "distributed service mesh",
        "Kubernetes pod cluster",
        "event-driven microservices topology",
        "decentralized worker fleet",
        "federated microservice infrastructure"
    ],
    "monolith_architecture": [
        "legacy monolithic service",
        "tightly coupled backend monolith",
        "centralized single-tier architecture",
        "legacy multi-tier monolithic backend"
    ],
    "serverless_architecture": [
        "fragmented serverless functions",
        "stateless cloud functions",
        "ephemeral compute micro-tasks",
        "event-driven lambda triggers"
    ],
    "mainframe_architecture": [
        "aging mainframe",
        "legacy central batch mainframe",
        "on-premise central mainframe host"
    ],
    "person_role": [
        "lead engineer",
        "principal architect",
        "staff engineer",
        "systems designer",
        "technical lead",
        "infrastructure specialist",
        "domain architect"
    ],
    "target_audience": [
        "principal engineering group",
        "junior engineers who will be tasked with implementation",
        "non-technical stakeholders and executive leadership",
        "security and compliance review board",
        "new developers joining the team",
        "the architectural review board",
        "senior engineering leadership"
    ],
    "deliverable_purpose": [
        "primary onboarding guide",
        "foundational technical blueprint",
        "standard reference document",
        "core engineering guide",
        "architectural specification reference"
    ],
    "target_team": [
        "new developers joining the team",
        "the core infrastructure team",
        "the product engineering squad",
        "external audit contractors",
        "cross-functional platform engineers"
    ],
    "document_type": [
        "comprehensive RFC",
        "technical design document",
        "detailed architectural specification",
        "system blueprint",
        "structured engineering design doc",
        "system architecture proposal"
    ],
    "design_aspect_1": [
        "system design",
        "architecture overview",
        "component topology",
        "high-level architecture",
        "system decomposition"
    ],
    "design_aspect_2": [
        "API contracts",
        "data schemas",
        "communication protocols",
        "service interfaces",
        "state management protocols"
    ],
    "design_aspect_3": [
        "database schemas",
        "failure mitigation strategies",
        "deployment stages",
        "data consistency models",
        "operational rollback procedures"
    ],
    "output_format_style": [
        "standard AWS Well-Architected Framework",
        "formal IEEE software architecture document",
        "Google-style technical design doc",
        "RFC-2119 specification standard",
        "production readiness checklist"
    ],
    "markup_format": [
        "markdown format",
        "structured GitHub Markdown",
        "clean technical Markdown format"
    ],
    "list_format": [
        "bulleted checklist",
        "numbered technical breakdown",
        "hierarchical outline"
    ],
    "diagram_format": [
        "Mermaid.js sequence diagrams",
        "Mermaid.js architecture diagrams",
        "data flow diagrams"
    ],
    "structure_format": [
        "narrative explanation",
        "structured RFC proposal",
        "modular technical brief"
    ],
    "guide_format": [
        "step-by-step implementation guide",
        "practical engineering handbook",
        "walkthrough specification"
    ],
    "frontend_stack": [
        "React",
        "Vue.js",
        "Next.js",
        "SvelteKit",
        "Angular"
    ],
    "backend_stack": [
        "Node.js",
        "Go Gin",
        "FastAPI",
        "Spring Boot",
        "Rust Axum"
    ],
    "database_choice": [
        "single PostgreSQL",
        "sharded MySQL",
        "replicated CockroachDB",
        "high-availability PostgreSQL"
    ],
    "service_count": [
        "500",
        "250",
        "150",
        "350",
        "600"
    ],
    "protocol_choice": [
        "REST over HTTPS",
        "gRPC and Protocol Buffers",
        "asynchronous message queues",
        "GraphQL federation"
    ],
    "batch_frequency": [
        "nightly batch processing",
        "hourly micro-batch transformations",
        "daily ETL consolidation",
        "nightly synchronization jobs"
    ],
    "cloud_environment": [
        "AWS shop",
        "GCP shop",
        "Azure-centric organization",
        "hybrid cloud environment",
        "multi-cloud deployment"
    ],
    "container_orchestration": [
        "Kubernetes",
        "Amazon ECS",
        "Nomad",
        "containerized workloads",
        "managed K8s clusters"
    ],
    "cloud_provider": [
        "Google Cloud Platform",
        "Amazon Web Services",
        "Microsoft Azure"
    ],
    "analytics_platform": [
        "BigQuery",
        "Snowflake",
        "ClickHouse",
        "Amazon Redshift",
        "Apache Iceberg"
    ],
    "required_stack": [
        "Python, FastAPI, and Redis",
        "Go, gRPC, and PostgreSQL",
        "Rust, Tokio, and SQLite",
        "TypeScript, Next.js, and Node.js",
        "C++, Boost.Asio, and RocksDB"
    ],
    "disallowed_tech": [
        "Java",
        "PHP",
        "Ruby",
        "monolithic frameworks",
        "untyped scripting languages"
    ],
    "neutral_stack": [
        "Kafka and PostgreSQL",
        "RabbitMQ and ScyllaDB",
        "Redis and ClickHouse",
        "NATS and RocksDB"
    ],
    "codebase_languages": [
        "primarily Go and Rust",
        "primarily Python and TypeScript",
        "primarily C++ and Rust",
        "primarily Go and Java"
    ],
    "service_protocol": [
        "gRPC",
        "Apache Thrift",
        "QUIC streams",
        "internal REST APIs"
    ],
    "traffic_event": [
        "the holiday rush",
        "our seasonal Black Friday spike",
        "unexpected flash-sale traffic",
        "a rapid surge in concurrent user onboarding",
        "our annual peak marketing campaign"
    ],
    "failure_symptom": [
        "frequent gateway timeouts",
        "severe tail-latency degradation",
        "connection pool exhaustion",
        "cascading queue backpressure",
        "thread deadlock spikes"
    ],
    "business_impact": [
        "lost transactions and unfulfilled orders",
        "failed customer checkout sessions",
        "dropped real-time event payloads",
        "degraded user experience and session drops"
    ],
    "timeframe_deadline": [
        "hard deadline of 3 months",
        "strict 6-week MVP timeline",
        "tight 2-quarter delivery schedule",
        "strict 4-month release deadline",
        "fixed 90-day delivery window"
    ],
    "hardware_constraint": [
        "only 256MB of RAM and intermittent connectivity",
        "512MB RAM and a single-core Cortex-M4 CPU",
        "1GB memory envelope in a fanless enclosure",
        "strictly battery-powered operation with periodic sleep cycles"
    ],
    "team_constraint": [
        "very small DevOps team",
        "lean engineering squad",
        "two-person infrastructure team",
        "tight-knit platform squad"
    ],
    "infrastructure_goal": [
        "entirely self-healing",
        "zero-touch and automated",
        "fully self-managed",
        "resilient to unannounced restarts"
    ],
    "optimization_goal": [
        "low resource consumption",
        "minimal memory footprint",
        "optimal CPU utilization",
        "cost-effective operational overhead"
    ],
    "compliance_standard": [
        "strict SOC2 and GDPR security requirements",
        "HIPAA and ISO-27001 compliance standards",
        "PCI-DSS Level 1 compliance rules",
        "strict data sovereignty laws",
        "defense-grade security policies"
    ],
    "processing_location": [
        "strictly on-premise without touching the public internet",
        "within an isolated private VPC",
        "inside air-gapped secure enclaves",
        "within local edge processing nodes"
    ],
    "scale_users": [
        "200,000 active users",
        "2,000,000 monthly active users",
        "50,000 daily users",
        "1,000,000 registered accounts"
    ],
    "scale_throughput": [
        "200,000 requests per second across 3 AWS regions",
        "50,000 events per second across multi-region clusters",
        "100,000 RPS peak load across availability zones",
        "500,000 messages per minute"
    ],
    "scale_data": [
        "200,000 records",
        "50 million records",
        "10 TB of telemetry logs",
        "5 TB time-series dataset"
    ],
    "concurrent_scale": [
        "200,000 concurrent connections",
        "500,000 active sessions",
        "1,000,000 simultaneous clients",
        "50,000 real-time streams"
    ],
    "latency_target": [
        "10ms",
        "25ms",
        "5ms",
        "50ms"
    ],
    "batch_window_target": [
        "within a 2-hour window instead of 8 hours",
        "within 45 minutes instead of 4 hours",
        "in under 30 minutes instead of overnight"
    ],
    "availability_percentage": [
        "99.999%",
        "99.99%",
        "99.9%"
    ],
    "availability_goal": [
        "zero-downtime availability",
        "high resilience under spike loads",
        "deterministic tail latency"
    ],
    "disaster_scenario": [
        "complete availability zone outage",
        "regional network partition",
        "primary database node failure",
        "cascading link disruption"
    ],
    "domain_market_type": [
        "real-time financial market",
        "high-frequency analytics market",
        "enterprise trading ecosystem",
        "competitive consumer application space"
    ],
    "funding_event": [
        "Series B funding",
        "Series A funding",
        "new enterprise funding",
        "strategic growth capital"
    ],
    "infrastructure_scope": [
        "internal systems",
        "core infrastructure",
        "backend platform",
        "service infrastructure"
    ],
    "expansion_goal": [
        "an aggressive European market expansion",
        "a global enterprise rollout",
        "high-volume customer onboarding",
        "rapid geographic expansion"
    ],
    "technical_debt_level": [
        "severe technical debt",
        "escalating operational overhead",
        "fragile legacy couplings"
    ],
    "efficiency_issue": [
        "inefficient resource utilization",
        "unoptimized memory allocation loops",
        "excessive thread contention"
    ],
    "concurrency_issue": [
        "race conditions",
        "deadlock hazards",
        "lock contention on shared state"
    ],
    "analytics_workload": [
        "daily heavy aggregation queries",
        "unindexed full-table scans",
        "complex historical OLAP transformations"
    ],
    "resource_pressure": [
        "memory pressure",
        "CPU throttle limits",
        "file descriptor starvation"
    ],
    "network_condition": [
        "intermittent connectivity drops",
        "transient packet loss and high jitter",
        "asymmetric network partitions"
    ],
    "security_risk": [
        "data exfiltration",
        "unauthorized privilege escalation",
        "cross-tenant data leakage"
    ],
    "api_version": [
        "V1",
        "legacy v1.2",
        "existing REST"
    ],
    "trust_model": [
        "trusted and isolated",
        "perimeter-secured",
        "internal private-network bounded"
    ],
    "auth_gateway": [
        "API gateway",
        "central authentication proxy",
        "identity provider gateway"
    ],
    "storage_assumption": [
        "infinite storage capacity",
        "abundant SSD scratch space",
        "scalable object storage availability"
    ],
    "payload_size": [
        "small, roughly 2 KB",
        "medium, roughly 15 KB",
        "compact, under 1 KB"
    ],
    "rejected_approach": [
        "pure serverless approach",
        "synchronous REST polling pipeline",
        "monolithic shared database topology"
    ],
    "rejection_reason": [
        "cold start latency and unpredictable tail latencies",
        "excessive network egress and coupling",
        "unacceptable scaling bottlenecks"
    ],
    "rejected_pattern": [
        "polling architecture",
        "centralized message broker single-point",
        "two-phase commit across all microservices"
    ],
    "rejected_outcome": [
        "unacceptable delays and degraded user experience",
        "cascading retry storms",
        "severe throughput collapse"
    ],
    "rejected_db_tech": [
        "NoSQL database",
        "document store",
        "key-value store"
    ],
    "evaluated_db": [
        "MongoDB",
        "DynamoDB",
        "Couchbase"
    ],
    "data_model_need": [
        "relational data model and strict foreign key integrity",
        "complex multi-table join requirements",
        "strict ACID transactional guarantees"
    ],
    "rejected_queue_tech": [
        "message queue",
        "simple pub/sub bus",
        "FIFO topic partition"
    ],
    "rejected_graph_tech": [
        "graph database",
        "distributed graph engine",
        "specialized triplestore"
    ]
}

CATEGORY_DOMAIN_PROJECTS = {
    "Software Feature": [
        "real-time collaborative document editing tool with conflict resolution",
        "multi-tenant role-based access control permission subsystem",
        "interactive live dashboard with real-time WebSocket updates",
        "in-app search and filtering engine with auto-complete indexing",
        "automated notification dispatch engine with retry mechanisms"
    ],
    "Software System": [
        "distributed background task execution engine with priority queues",
        "centralized audit logging and compliance event store",
        "multi-region billing and subscription lifecycle management platform",
        "scalable API gateway with dynamic rate limiting and token bucket filtering",
        "distributed workflow orchestration engine with state machine persistence"
    ],
    "Distributed System": [
        "distributed key-value storage engine using the Raft consensus protocol",
        "globally distributed cache cluster with multi-region replication",
        "distributed lock manager with lease expiration and fencing tokens",
        "distributed consensus coordination subsystem for clustered nodes",
        "partitioned vector storage engine with decentralized index replication"
    ],
    "Backend/API": [
        "high-performance GraphQL schema federation gateway for microservices",
        "RESTful checkout and payment processing API supporting idempotency keys",
        "webhook delivery and event subscription service with exponential backoff",
        "high-throughput user authentication and OAuth2 token management API",
        "internal microservice mesh coordinator with dynamic routing"
    ],
    "Frontend/UI": [
        "virtualized data grid component rendering 100,000 real-time rows smoothly",
        "modular micro-frontend container architecture with sandboxed routing",
        "drag-and-drop workflow canvas UI with undo/redo historical state stack",
        "accessible, themeable component design system library compliant with WCAG 2.1 AA",
        "high-performance interactive canvas for large-scale node-graph visualization"
    ],
    "Mobile Application": [
        "background location tracking service optimized for minimal battery drain",
        "offline-first SQLite synchronizer with bidirectional conflict resolution",
        "biometric authentication and encrypted local key-vault subsystem",
        "push notification caching and badge management background handler",
        "peer-to-peer device discovery and local synchronization engine"
    ],
    "Database/Data Storage": [
        "multi-region database failover and replica promotion engine",
        "high-performance LSM-Tree time-series storage engine with compaction",
        "distributed document store with tunable consistency and vector search",
        "immutable append-only financial ledger storage with cryptographic verification",
        "distributed columnar store optimized for high-ingestion analytical queries"
    ],
    "Data Pipeline": [
        "real-time clickstream ingestion and aggregation pipeline using Apache Flink",
        "change-data-capture (CDC) streaming ETL pipeline from transactional databases",
        "high-throughput telemetry event ingestion pipeline processing millions of events/sec",
        "distributed batch data transformation workflow with automatic backfill recovery",
        "lakehouse delta table compaction and historical data retention worker"
    ],
    "Search/Retrieval": [
        "hybrid BM25 and dense neural vector search retrieval service",
        "incremental inverted index builder for large-scale document collections",
        "distributed semantic search ranking engine with multi-stage reranking",
        "real-time faceted filtering and query spelling correction subsystem",
        "high-scale document similarity search index with sub-10ms query latency"
    ],
    "Messaging/Eventing": [
        "high-throughput distributed publish-subscribe message broker",
        "event bus routing engine with dead-letter queue and replay capabilities",
        "partitioned event stream consumer group coordinator",
        "low-latency message serialization and framing transport protocol",
        "distributed transactional outbox event dispatcher"
    ],
    "Networking": [
        "dynamic path selection controller for software-defined WAN (SD-WAN)",
        "zero-trust software defined perimeter overlay network",
        "high-throughput network load balancer with eBPF kernel packet steering",
        "WireGuard mesh VPN overlay orchestrator with dynamic peer peering",
        "DNS-over-HTTPS (DoH) recursive resolver with edge caching and threat filtering"
    ],
    "Network Protocol": [
        "zero-copy packet serialization protocol for kernel bypass networking",
        "lightweight binary telemetry framing protocol optimized for UDP transport",
        "multiplexed stream control protocol running over QUIC transport",
        "peer discovery and peer-state gossip protocol for decentralized clusters",
        "reliable unordered datagram delivery protocol with selective acknowledgments"
    ],
    "Cloud Infrastructure": [
        "multi-region cloud infrastructure capable of zero-downtime failover",
        "automated multi-cloud Kubernetes cluster provisioning and lifecycle manager",
        "cross-region network peering mesh with transit gateway route optimization",
        "cloud cost optimization daemon for auto-scaling spot instance fleets",
        "declarative infrastructure-as-code state synchronization pipeline"
    ],
    "Infrastructure/Platform": [
        "internal developer platform (IDP) with self-service environment provisioning",
        "centralized secrets management and automated certificate rotation system",
        "multi-tenant container runtime isolation environment with gVisor sandboxing",
        "organization-wide service discovery and service catalog platform",
        "ephemeral sandbox test environment manager for automated pull request previews"
    ],
    "DevOps/CI-CD": [
        "autonomous deployment pipeline with automated canary analysis and rollback",
        "ephemeral CI runner cluster with dynamic resource scaling and image caching",
        "GitOps declarative configuration synchronization agent with drift detection",
        "multi-architecture container image builder with cross-compilation caching",
        "secure artifact supply-chain signing and provenance verification gate"
    ],
    "Observability/Monitoring": [
        "high-cardinality distributed metrics ingestion and alerting platform",
        "predictive anomaly detection engine for infrastructure health signals",
        "distributed tracing collection agent with dynamic adaptive sampling",
        "centralized log aggregation and full-text search cluster with cold tiering",
        "synthetic end-to-end user journey monitoring and alerting service"
    ],
    "Security/Auth": [
        "zero-trust microservice mutual TLS (mTLS) certificate issuance authority",
        "continuous authentication and risk-based adaptive session management engine",
        "fine-grained attribute-based access control (ABAC) policy evaluation engine",
        "hardware security module (HSM) key management and cryptographic signing API",
        "real-time security event log analyzer and automated threat response pipeline"
    ],
    "Machine Learning System": [
        "distributed neural model training orchestration engine across multi-GPU clusters",
        "real-time low-latency feature store with streaming backfill and caching",
        "automated model deployment platform with shadow testing and drift monitoring",
        "high-throughput model inference server with dynamic batching and GPU optimization",
        "distributed vector embedding generator for catalog semantic representations"
    ],
    "LLM Application": [
        "retrieval-augmented generation (RAG) agent with hybrid vector ranking",
        "multi-agent collaborative reasoning supervisor with memory persistence",
        "context compression and semantic chunking engine for long-document processing",
        "real-time streaming LLM response guardrail and safety moderation pipeline",
        "fine-tuning orchestration pipeline with dataset curation and evaluation gates"
    ],
    "Computer Vision Pipeline": [
        "real-time edge object detection and tracking pipeline with TensorRT acceleration",
        "multi-camera video stream ingestion and temporal feature aggregation service",
        "automated visual defect classification system for manufacturing quality control",
        "low-latency facial recognition and anti-spoofing verification engine",
        "satellite imagery tile processing and feature segmentation pipeline"
    ],
    "NLP Pipeline": [
        "multi-lingual document categorization and entity extraction pipeline",
        "real-time intent classification and slot-filling engine for conversational agents",
        "large-scale sentiment analysis and topic modeling stream processing service",
        "abstractive document summarization engine with domain-specific vocabulary tuning",
        "automated technical terminology and acronym disambiguation system"
    ],
    "Recommendation System": [
        "two-tower neural candidate retrieval and ranking engine for personalized feeds",
        "real-time user engagement graph and graph convolutional ranking pipeline",
        "contextual multi-armed bandit exploration service for content discovery",
        "real-time session-based collaborative filtering recommendation engine",
        "cold-start item recommendation subsystem using multimodal embeddings"
    ],
    "Autonomous Agent Architecture": [
        "autonomous task planning and tool-calling execution agent with replanning",
        "hierarchical multi-agent coordinator for complex domain decomposition",
        "long-term episodic memory storage and memory consolidation agent",
        "self-reflective agent execution loop with error diagnosis and self-correction",
        "human-in-the-loop permission gateway for autonomous action confirmation"
    ],
    "Embedded System": [
        "ultra-low-power environmental sensor node firmware with deep-sleep scheduling",
        "hard real-time motor control firmware with hardware timer capture/compare",
        "secure bootloader with cryptographic firmware verification and rollback",
        "interrupt-driven multi-channel analog signal acquisition firmware",
        "CAN bus automotive telemetry gateway running on Cortex-M microcontrollers"
    ],
    "IoT System": [
        "fleet-scale IoT device management and delta-OTA firmware update orchestrator",
        "edge IoT telemetry aggregation gateway with MQTT protocol translation",
        "low-power wide-area network (LoRaWAN) sensor communication gateway",
        "digital twin synchronization engine for industrial machinery telemetry",
        "edge rule-evaluation engine for disconnected autonomous anomaly alerting"
    ],
    "Robotics/Autonomous System": [
        "real-time robot trajectory planner and obstacle avoidance controller",
        "multi-sensor SLAM (Simultaneous Localization and Mapping) fusion pipeline",
        "ROS2 hardware abstraction layer and motor driver controller",
        "autonomous mobile robot (AMR) fleet dispatch and corridor routing manager",
        "robotic arm inverse kinematics and force-torque feedback controller"
    ],
    "Sensor/Instrumentation System": [
        "precision 24-bit multi-channel data acquisition (DAQ) instrumentation unit",
        "optical spectrometer signal conditioning and baseline drift calibration circuit",
        "piezoelectric vibration sensor signal processing pipeline for machine diagnostics",
        "high-speed strain gauge bridge amplifier with active temperature compensation",
        "electrochemical gas sensor interface with dynamic baseline correction"
    ],
    "Power Electronics": [
        "high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics",
        "bidirectional battery charger and inverter power stage for electric vehicles",
        "resonant LLC half-bridge DC-DC converter with synchronous rectification",
        "isolated flyback auxiliary power supply with wide input voltage range",
        "active power factor correction (PFC) boost stage with digital control loop"
    ],
    "PCB Design": [
        "high-speed 12-layer PCB layout for multi-gigabit PCIe and DDR4 routing",
        "mixed-signal PCB design with isolated analog and digital ground planes",
        "dense multi-layer motherboard PCB layout with microvias and impedance control",
        "rigid-flex PCB assembly for compact wearable biomedical instrumentation",
        "high-current power distribution PCB with optimized thermal copper planes"
    ],
    "FPGA/ASIC": [
        "pipelined hardware packet parsing and filtering engine implemented in Verilog",
        "high-speed FFT hardware accelerator IP core for radar signal processing",
        "custom RISC-V SoC architecture with memory-mapped hardware crypto accelerator",
        "ultra-low-latency financial trade execution matching engine on FPGA",
        "ASIC digital front-end for multi-channel neural recording interfaces"
    ],
    "Thermal Management": [
        "active liquid cooling thermal regulation loop for high-density GPU server chassis",
        "phase-change material heat sink assembly for transient power spike dissipation",
        "variable-speed fan control matrix with multi-zone thermal sensor feedback",
        "thermoelectric cooler (TEC) precision temperature stabilization loop for laser diodes",
        "heat pipe thermal distribution network for sealed fanless avionics enclosures"
    ],
    "RF/Microwave Design": [
        "5.8 GHz low-noise amplifier (LNA) with integrated input impedance matching",
        "X-band radar transmitter power amplifier stage with Gallium Nitride (GaN) HEMTs",
        "microstrip bandpass filter for satellite communications telemetry receiver",
        "voltage-controlled oscillator (VCO) with ultra-low phase noise for RF synthesizers",
        "bidirectional RF front-end module with integrated transmit/receive switch"
    ],
    "Antenna Design": [
        "phased array beamforming antenna array for satellite communications",
        "wideband planar inverted-F antenna (PIFA) for compact mobile handsets",
        "dual-polarized microstrip patch antenna array for 5G millimeter-wave radar",
        "circularly polarized helical antenna for telemetry reception on sounding rockets",
        "conformal broadband slot antenna for aerodynamic UAV wing integration"
    ],
    "Signal Integrity": [
        "differential pair routing and jitter budget analysis for 25 Gbps SERDES links",
        "power distribution network (PDN) impedance optimization and decoupling analysis",
        "eye diagram margin validation and crosstalk suppression on high-speed memory buses",
        "via stub elimination and backdrilling optimization for backplane connectors",
        "electromigration and thermal relief analysis for high-current copper planes"
    ],
    "EMI/EMC/Noise Mitigation": [
        "common-mode choke and differential EMI filter stage for industrial motor drives",
        "conducted emissions suppression circuit for switched-mode power supplies (SMPS)",
        "faraday cage shielding and gasket design for high-frequency RF enclosures",
        "ground loop mitigation and isolation topology for sensitive biomedical amplifiers",
        "radiated immunity hardening for automotive electronics compliant with CISPR 25"
    ],
    "Hardware/Software Integration": [
        "hardware-in-the-loop (HIL) automated test bench for flight controller validation",
        "DMA-driven circular buffer kernel driver for high-speed ADC data streaming",
        "FPGA-to-Host PCIe DMA transfer engine with zero-copy userspace memory mapping",
        "I2C/SPI sensor device tree driver with interrupt-driven asynchronous event queue",
        "firmware calibration harness for multi-axis inertial measurement units (IMUs)"
    ],
    "Microcontroller Firmware": [
        "bare-metal interrupt-driven state machine for industrial valve actuation",
        "FreeRTOS multi-threaded firmware for portable medical infusion pumps",
        "low-power Cortex-M0+ firmware with periodic sleep-and-sample duty cycling",
        "USB composite device firmware implementing HID and virtual COM interfaces",
        "dual-bank firmware update manager with flash partition swap and integrity checking"
    ],
    "Operating System Component": [
        "custom virtual memory page-fault handler and demand-paging subsystem",
        "preemptive priority-based thread scheduler with real-time deadline guarantees",
        "lockless circular ring buffer IPC (inter-process communication) mechanism",
        "in-memory virtual file system (VFS) with unified block-device abstraction",
        "userspace asynchronous I/O engine modeled on Linux io_uring"
    ],
    "Storage Engine": [
        "log-structured merge-tree (LSM) storage engine with tiered compaction strategies",
        "copy-on-write B-tree indexing engine for crash-consistent file systems",
        "direct-I/O append-only commit log with NVMe hardware flush optimization",
        "in-memory columnar storage chunk manager with dictionary compression",
        "zero-copy block caching engine with adaptive replacement cache (ARC) policy"
    ],
    "High-Performance Computing": [
        "MPI-distributed parallel matrix multiplication engine with non-blocking transfers",
        "heterogeneous CUDA/OpenCL parallel reduction kernel with shared-memory tiling",
        "lock-free work-stealing task threadpool for multi-socket NUMA architectures",
        "SIMD-vectorized floating-point signal processing library using AVX-512",
        "distributed parallel mesh decomposition solver for computational fluid dynamics"
    ],
    "Distributed Consensus": [
        "Multi-Paxos replicated state machine with active leader leases and pipelining",
        "Byzantine fault-tolerant (BFT) consensus protocol for untrusted validator nodes",
        "Raft log replication engine with dynamic cluster membership changes",
        "asynchronous distributed snapshot and barrier synchronization protocol",
        "causal broadcast ordering engine with vector clock timestamping"
    ],
    "Compiler/Runtime Engine": [
        "just-in-time (JIT) compiler tier with SSA-based dead code elimination and inlining",
        "generational garbage collector with concurrent mark-and-sweep phases",
        "bytecode virtual machine interpreter with direct threaded code dispatch",
        "LLVM-based optimization pass for automated loop unrolling and auto-vectorization",
        "static type inference and escape analysis engine for stack allocation optimization"
    ],
    "Real-Time System": [
        "hard real-time avionics mission computer with guaranteed sub-millisecond jitter",
        "deterministic priority-inheritance mutex library for preventing priority inversion",
        "cyclic executive task scheduler for critical flight surface actuation",
        "time-triggered Ethernet (TTEthernet) protocol handler for aerospace telemetry",
        "real-time telemetry logging engine with guaranteed non-blocking writes"
    ],
    "Audio Signal Processing": [
        "real-time multi-channel acoustic echo cancellation (AEC) DSP pipeline",
        "low-latency psychoacoustic spatial 3D audio rendering and HRTF convolution engine",
        "active noise cancellation (ANC) adaptive FIR filter with sub-millisecond latency",
        "real-time parametric equalizer and multiband dynamic range compressor",
        "neural speech enhancement and background noise suppression stream processor"
    ],
    "Video Streaming/Encoding": [
        "low-latency WebRTC live video encoding pipeline with dynamic bitrate scaling",
        "distributed HLS/DASH video segment packaging and CDN origin distribution service",
        "hardware-accelerated HEVC/AV1 video transcode farm with adaptive resolution ladders",
        "real-time video frame compositor with overlay rendering and alpha blending",
        "video perceptual quality evaluation engine running real-time VMAF analysis"
    ],
    "AR/VR System": [
        "six-degree-of-freedom (6DoF) optical head-tracking and pose prediction pipeline",
        "asynchronous timewarp (ATW) and reprojection rendering compositor for VR headsets",
        "spatial audio rendering and room impulse response modeling pipeline",
        "real-time eye-tracking and foveated rendering graphics pipeline",
        "hand-tracking mesh deformation and gesture recognition subsystem"
    ],
    "Blockchain/Web3": [
        "EVM-compatible smart contract execution virtual machine with gas accounting",
        "cryptographic zero-knowledge rollup proof generator for transaction batching",
        "decentralized peer-to-peer state validation node with cryptographic Merkle trees",
        "multi-signature threshold key management and automated transaction relayer",
        "decentralized order-book matching engine with deterministic state transitions"
    ],
    "Simulation Engine": [
        "high-performance physics collision detection engine using bounding volume hierarchies (BVH)",
        "multi-body rigid dynamics simulation solver with iterative impulse constraints",
        "large-scale discrete-event traffic simulation engine with dynamic agent routing",
        "computational electromagnetic field solver for high-frequency antenna simulation",
        "real-time atmospheric weather particle simulation and fluid dynamics solver"
    ],
    "Gaming Engine/Subsystem": [
        "entity-component-system (ECS) architecture with cache-friendly contiguous memory layout",
        "client-side prediction and server reconciliation netcode for competitive multiplayer",
        "dynamic level-of-detail (LOD) asset streaming and geometry culling system",
        "spatial audio propagation and occlusion query system for dynamic environments",
        "procedural world generation pipeline with voxel terrain meshing"
    ],
    "Safety-Critical System": [
        "dual-channel fail-operational voting controller for fly-by-wire flight control",
        "ISO 26262 ASIL-D compliant electronic braking control system architecture",
        "independent hardware safety watchdog with redundant power and clock monitoring",
        "nuclear reactor primary coolant monitoring and automatic trip actuation system",
        "IEC 61508 SIL-3 certified emergency shutdown (ESD) logic solver architecture"
    ],
    "Automotive Software": [
        "AUTOSAR Classic adaptive platform gateway for CAN-FD and Automotive Ethernet",
        "advanced driver-assistance system (ADAS) sensor fusion and emergency braking controller",
        "electric vehicle battery management system (BMS) with cell balancing and SOC estimation",
        "vehicle-to-everything (V2X) communication stack for cooperative collision warning",
        "OTA software update manager compliant with UN ECE R156 cybersecurity regulations"
    ],
    "Avionics Software": [
        "DO-178C Level A certified primary flight display (PFD) graphics rendering engine",
        "ARINC 429 and ARINC 653 integrated modular avionics (IMA) partition manager",
        "aircraft flight management system (FMS) route navigation and fuel optimization engine",
        "terrain awareness and warning system (TAWS) with real-time altitude clearance checks",
        "dual-redundant flight control law execution computer with synchronous lockstep"
    ],
    "Bioinformatics Pipeline": [
        "distributed genomic sequence alignment and variant calling pipeline using Burrows-Wheeler",
        "single-cell RNA-sequencing data normalization and dimensionality reduction pipeline",
        "protein tertiary structure folding prediction pipeline using deep learning models",
        "high-throughput mass spectrometry proteomics spectral matching and identification engine",
        "phylogenetic tree construction and multiple sequence alignment pipeline"
    ],
    "Medical Device Software": [
        "IEC 62304 Class C compliant patient-ventilator closed-loop pressure control software",
        "continuous glucose monitoring (CGM) sensor signal processing and trend prediction algorithm",
        "digital electrocardiogram (ECG) QRS-complex detection and arrhythmia classification engine",
        "robotic surgical tool position tracking and virtual fixture force-feedback controller",
        "automated external defibrillator (AED) ECG rhythm analysis and shock advisory system"
    ]
}

TEMPLATED_CATEGORY_PARAGRAPHS = {
    "Software Feature": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Software System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Distributed System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Backend/API": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Frontend/UI": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Mobile Application": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Database/Data Storage": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Data Pipeline": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Search/Retrieval": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Messaging/Eventing": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Networking": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Network Protocol": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Cloud Infrastructure": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Infrastructure/Platform": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "DevOps/CI-CD": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Observability/Monitoring": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Security/Auth": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Machine Learning System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "LLM Application": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Computer Vision Pipeline": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "NLP Pipeline": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Recommendation System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Autonomous Agent Architecture": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Embedded System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "IoT System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Robotics/Autonomous System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Sensor/Instrumentation System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Power Electronics": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "PCB Design": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "FPGA/ASIC": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Thermal Management": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "RF/Microwave Design": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Antenna Design": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Signal Integrity": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "EMI/EMC/Noise Mitigation": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Hardware/Software Integration": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Microcontroller Firmware": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Operating System Component": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Storage Engine": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "High-Performance Computing": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Distributed Consensus": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Compiler/Runtime Engine": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Real-Time System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Audio Signal Processing": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Video Streaming/Encoding": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "AR/VR System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Blockchain/Web3": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Simulation Engine": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Gaming Engine/Subsystem": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Safety-Critical System": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Automotive Software": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Avionics Software": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Bioinformatics Pipeline": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    },
    "Medical Device Software": {
        "specific_project_details": [
            "Our team is tasked with designing a {domain_project_concept}.",
            "We have been assigned the responsibility of implementing a {domain_project_concept}.",
            "The architectural committee requested a technical blueprint for a {domain_project_concept}.",
            "I am the {person_role} responsible for prototyping a {domain_project_concept}.",
            "We are kicking off a new sprint dedicated entirely to building a {domain_project_concept}."
        ],
        "background_project_info": [
            "Our {microservice_architecture} failed to scale during {traffic_event}, leading to {failure_symptom} and {business_impact}.",
            "During {traffic_event}, our {microservice_architecture} suffered {failure_symptom}, resulting in {business_impact}.",
            "We experienced {business_impact} after our {microservice_architecture} was overwhelmed by {traffic_event}.",
            "Our {monolith_architecture} was unable to keep pace as traffic reached {scale_users}, creating unsustainable operational overhead.",
            "As active demand grew to {scale_users}, our {monolith_architecture} exhibited severe latency degradation in the {domain_market_type}.",
            "We recently secured {funding_event} and need to overhaul our {infrastructure_scope} to prepare for {expansion_goal}.",
            "Following our {funding_event}, we are overhauling our {infrastructure_scope} to accelerate {expansion_goal}.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with {technical_debt_level}.",
            "Having originated as a rapid prototype, our current implementation now carries {technical_debt_level} across critical production paths."
        ],
        "problem_overview": [
            "Currently, our system handles approximately {scale_throughput}, but during peak load we experience significant performance degradation.",
            "Under peak load conditions with {scale_throughput}, our system experiences severe performance bottlenecks.",
            "System throughput has plateaued while hardware costs are rising exponentially due to {efficiency_issue}.",
            "Due to {efficiency_issue}, hardware operating costs are escalating rapidly while system throughput remains flat.",
            "We are seeing a high rate of data inconsistency and {concurrency_issue} during concurrent user operations.",
            "Under concurrent user load, critical data flows are compromised by {concurrency_issue} and state inconsistency.",
            "Our database locks up entirely whenever the analytics team runs their {analytics_workload}.",
            "Whenever the analytics team triggers their {analytics_workload}, our transactional database encounters severe lock contention.",
            "The application crashes silently under {resource_pressure}, causing us to manually restart the pods multiple times a day.",
            "Under intense {resource_pressure}, our application crashes without warning, requiring emergency service restarts."
        ],
        "caveats_and_considerations": [
            "Our organization manages over {scale_data} and needs to ensure compliance with {compliance_standard}.",
            "To safeguard over {scale_data}, full compliance with {compliance_standard} is strictly mandatory.",
            "The solution must be fully backwards-compatible with our {api_version} API clients to avoid breaking legacy integrations.",
            "Maintaining seamless backwards-compatibility with {api_version} clients is essential to prevent legacy partner disruptions.",
            "We cannot rely on third-party SaaS vendors for this component due to {compliance_standard}.",
            "Due to {compliance_standard}, relying on third-party SaaS providers is strictly prohibited.",
            "The system must gracefully handle {network_condition} without data loss or corruption.",
            "In the presence of {network_condition}, the system must remain resilient with zero data loss or state corruption.",
            "Security is our absolute highest priority; any potential for {security_risk} is a hard failure.",
            "Preventing {security_risk} is a hard requirement, as security remains our paramount engineering constraint."
        ],
        "the_request": [
            "Please provide a {document_type} including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows\n- Key APIs and interfaces\n- Failure modes and mitigation strategies\n- Tradeoffs, operational risks, and recommended next steps.",
            "I need you to draft a {document_type} outlining the {design_aspect_1}, {design_aspect_2}, and {design_aspect_3}.",
            "Could you generate a {document_type} detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a {person_role} and present a {document_type} to solve this.",
            "Generate a {document_type} covering the system architecture, required components, and deployment steps.",
            "As a {person_role}, please produce a {document_type} detailing the end-to-end design and operational considerations."
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for {optimization_goal} and minimal maintenance burden.",
            "Given strict budget limitations, minimizing operational overhead and targeting {optimization_goal} are essential.",
            "We have a {timeframe_deadline} to deliver this MVP, so we cannot afford to build everything from scratch.",
            "With a {timeframe_deadline} for this MVP, building bespoke infrastructure from scratch is out of the question.",
            "The hardware environment is highly constrained, limited to {hardware_constraint}.",
            "Operating within {hardware_constraint}, the system must remain strictly lightweight and efficient.",
            "We are limited to a {team_constraint}, meaning the infrastructure must be {infrastructure_goal}.",
            "Because we operate with a {team_constraint}, the proposed infrastructure must be {infrastructure_goal}.",
            "Due to regulatory compliance, all data processing must occur {processing_location}.",
            "All data transformations and storage must be handled {processing_location} to satisfy regulatory mandates."
        ],
        "current_architecture": [
            "We currently rely on a {monolith_architecture} that is reaching its end of life.",
            "Our current core system is a {monolith_architecture}, which has reached the end of its maintainable lifecycle.",
            "Our stack consists of a {frontend_stack} frontend talking to a {backend_stack} backend, backed by a {database_choice} database.",
            "The application layer currently connects a {frontend_stack} client to a {backend_stack} service over a {database_choice} database.",
            "We operate a sprawling mesh of over {service_count} microservices communicating synchronously via {protocol_choice}.",
            "Our infrastructure currently comprises over {service_count} microservices linked synchronously through {protocol_choice}.",
            "The system is currently composed of heavily {serverless_architecture} that are difficult to orchestrate.",
            "Our workload is presently partitioned across {serverless_architecture}, introducing severe orchestration complexities.",
            "Our legacy architecture relies on an {mainframe_architecture} doing {batch_frequency} to a data warehouse.",
            "Data synchronization is currently tied to an {mainframe_architecture} executing {batch_frequency}."
        ],
        "target_audience": [
            "This design document will be reviewed by the {target_audience}.",
            "The primary audience for this RFC consists of {target_audience}.",
            "Keep in mind this document will be presented to {target_audience}.",
            "This proposal is intended for the {target_audience}.",
            "The document will serve as the {deliverable_purpose} for {target_team}.",
            "Our goal is for this document to function as the {deliverable_purpose} for {target_team}."
        ],
        "success_criteria": [
            "We expect the system to scale to {concurrent_scale} while maintaining {availability_goal}.",
            "Supporting {concurrent_scale} while guaranteeing {availability_goal} defines the core success metric.",
            "The project will be considered successful if we reduce p99 response times to under {latency_target}.",
            "Achieving a p99 latency threshold of under {latency_target} is our principal benchmark for success.",
            "Success means handling the daily batch processing load {batch_window_target}.",
            "We will consider this project a success if the daily batch workload completes {batch_window_target}.",
            "We need to achieve {availability_percentage} availability even in the event of a {disaster_scenario}.",
            "Maintaining {availability_percentage} operational uptime during a {disaster_scenario} is a non-negotiable target.",
            "The feature must support a sustained throughput of {scale_throughput} with zero data loss.",
            "Sustaining {scale_throughput} with verifiable zero data loss is our definitive performance target."
        ],
        "tech_stack": [
            "We are an {cloud_environment} and heavily rely on {container_orchestration}.",
            "Operating as an {cloud_environment}, our workloads are standardly deployed across {container_orchestration}.",
            "The implementation must exclusively use {required_stack}. Do not suggest {disallowed_tech}.",
            "All proposed components must be strictly written using {required_stack}; avoid proposing {disallowed_tech}.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like {neutral_stack}.",
            "We have a strong organizational mandate towards vendor-neutral open-source tools such as {neutral_stack}.",
            "We use {cloud_provider} for compute, and {analytics_platform} for data warehousing.",
            "Our infrastructure pairs {cloud_provider} for compute capacity with {analytics_platform} for analytical storage.",
            "The codebase is {codebase_languages}, and we use {service_protocol} for internal service communication.",
            "Our existing software is written {codebase_languages}, leveraging {service_protocol} for inter-service communication."
        ],
        "expected_output_format": [
            "Please output the design in {markup_format} with appropriate headers.",
            "Format your response strictly as a {list_format} accompanied by {diagram_format}.",
            "I expect a {structure_format} broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a {output_format_style} review.",
            "Provide the output as a {guide_format} with code snippets for the core interfaces.",
            "Present your findings as a {structure_format} structured with clear section headers and {diagram_format}."
        ],
        "assumptions": [
            "Assume that all internal network traffic is {trust_model} and unencrypted.",
            "You may assume internal network communications are {trust_model} without transport-level encryption.",
            "You can assume that user authentication is already handled upstream by our {auth_gateway}.",
            "Assume authentication and token verification have already occurred upstream via our {auth_gateway}.",
            "For this design, assume we have {storage_assumption} and prioritize read speeds.",
            "You can design under the assumption of {storage_assumption}, optimizing primarily for read throughput.",
            "Assume that the average payload size is {payload_size} per request.",
            "Payload volume can be assumed to average {payload_size} per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose."
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a {rejected_approach} due to {rejection_reason}.",
            "A {rejected_approach} was evaluated and rejected specifically due to {rejection_reason}.",
            "We previously attempted a {rejected_pattern}, but it resulted in {rejected_outcome}.",
            "Prior experiments with a {rejected_pattern} were abandoned after causing {rejected_outcome}.",
            "Do not suggest a {rejected_db_tech}; we evaluated {evaluated_db} and it did not fit our {data_model_need}.",
            "We rejected {evaluated_db} because a {rejected_db_tech} cannot satisfy our {data_model_need}.",
            "We tried utilizing a {rejected_queue_tech}, but maintaining strict ordering proved to be too complex.",
            "An approach utilizing a {rejected_queue_tech} was deemed unacceptable because ordering guarantees could not be maintained.",
            "We rejected a {rejected_graph_tech} approach because the operational overhead was too high for our team."
        ]
    }
}

# Compatibility dictionary flattening typed slots into key-value pairs
TEMPLATE_VALUES = {}
for slot_name, slot_vals in TYPED_TEMPLATE_SLOTS.items():
    for idx, val in enumerate(slot_vals, 1):
        TEMPLATE_VALUES[f"{slot_name}_{idx}"] = val

for cat_name, projects in CATEGORY_DOMAIN_PROJECTS.items():
    for idx, proj in enumerate(projects, 1):
        TEMPLATE_VALUES[f"domain_project_{cat_name}_{idx}"] = proj
