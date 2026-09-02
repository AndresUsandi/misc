import json

PARAGRAPH_TYPES = [
    {
        "type": "background_project_info",
        "description": "Business requirements, high level mandates, non-technical motivators or goals."
    },
    {
        "type": "specific_project_details",
        "description": "Details about the specific project at hand (technical background)."
    },
    {
        "type": "problem_overview",
        "description": "Details about what needs to be solved."
    },
    {
        "type": "caveats_and_considerations",
        "description": "Caveats and considerations."
    },
    {
        "type": "the_request",
        "description": "The request (what the AI has to generate, taking into account all the info provided below)."
    },
    {
        "type": "constraints_and_limitations",
        "description": "Strict boundaries such as budget, timeline, team size, compliance/regulatory requirements, or hard technical limits."
    },
    {
        "type": "current_architecture",
        "description": "A description of what already exists (e.g., legacy state, current stack, current scale)."
    },
    {
        "type": "target_audience",
        "description": "Context on who the resulting design document is for (e.g., executives, junior engineers)."
    },
    {
        "type": "success_criteria",
        "description": "How the success of the project will be measured (e.g., KPIs, latency requirements, user limits)."
    },
    {
        "type": "tech_stack",
        "description": "Explicit instructions on what languages, frameworks, or cloud providers must or must not be used."
    },
    {
        "type": "expected_output_format",
        "description": "Formatting instructions for the AI's response (e.g., Markdown, Mermaid diagrams, specific sections)."
    },
    {
        "type": "assumptions",
        "description": "Things the engineer is assuming to be true for the sake of the design."
    },
    {
        "type": "alternative_approaches_rejected",
        "description": "What has already been attempted and why it failed."
    }
]

CATEGORY_PARAGRAPHS = {
    "Software Feature": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a real-time collaborative document editing tool with conflict resolution.",
            "We have been assigned the responsibility of implementing a real-time collaborative document editing tool with conflict resolution.",
            "The architectural committee requested a technical blueprint for a real-time collaborative document editing tool with conflict resolution.",
            "I am the lead engineer responsible for prototyping a real-time collaborative document editing tool with conflict resolution.",
            "We are kicking off a new sprint dedicated entirely to building a real-time collaborative document editing tool with conflict resolution.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Software System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a distributed background task execution engine with priority queues.",
            "We have been assigned the responsibility of implementing a distributed background task execution engine with priority queues.",
            "The architectural committee requested a technical blueprint for a distributed background task execution engine with priority queues.",
            "I am the lead engineer responsible for prototyping a distributed background task execution engine with priority queues.",
            "We are kicking off a new sprint dedicated entirely to building a distributed background task execution engine with priority queues.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Distributed System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a distributed key-value storage engine using the Raft consensus protocol.",
            "We have been assigned the responsibility of implementing a distributed key-value storage engine using the Raft consensus protocol.",
            "The architectural committee requested a technical blueprint for a distributed key-value storage engine using the Raft consensus protocol.",
            "I am the lead engineer responsible for prototyping a distributed key-value storage engine using the Raft consensus protocol.",
            "We are kicking off a new sprint dedicated entirely to building a distributed key-value storage engine using the Raft consensus protocol.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Backend/API": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a high-performance GraphQL schema federation gateway for microservices.",
            "We have been assigned the responsibility of implementing a high-performance GraphQL schema federation gateway for microservices.",
            "The architectural committee requested a technical blueprint for a high-performance GraphQL schema federation gateway for microservices.",
            "I am the lead engineer responsible for prototyping a high-performance GraphQL schema federation gateway for microservices.",
            "We are kicking off a new sprint dedicated entirely to building a high-performance GraphQL schema federation gateway for microservices.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Frontend/UI": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a virtualized data grid component rendering 100,000 real-time rows smoothly.",
            "We have been assigned the responsibility of implementing a virtualized data grid component rendering 100,000 real-time rows smoothly.",
            "The architectural committee requested a technical blueprint for a virtualized data grid component rendering 100,000 real-time rows smoothly.",
            "I am the lead engineer responsible for prototyping a virtualized data grid component rendering 100,000 real-time rows smoothly.",
            "We are kicking off a new sprint dedicated entirely to building a virtualized data grid component rendering 100,000 real-time rows smoothly.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Mobile Application": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a background location tracking service optimized for minimal battery drain.",
            "We have been assigned the responsibility of implementing a background location tracking service optimized for minimal battery drain.",
            "The architectural committee requested a technical blueprint for a background location tracking service optimized for minimal battery drain.",
            "I am the lead engineer responsible for prototyping a background location tracking service optimized for minimal battery drain.",
            "We are kicking off a new sprint dedicated entirely to building a background location tracking service optimized for minimal battery drain.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Database/Data Storage": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a time-series metrics storage engine supporting automatic downsampling and retention policies.",
            "We have been assigned the responsibility of implementing a time-series metrics storage engine supporting automatic downsampling and retention policies.",
            "The architectural committee requested a technical blueprint for a time-series metrics storage engine supporting automatic downsampling and retention policies.",
            "I am the lead engineer responsible for prototyping a time-series metrics storage engine supporting automatic downsampling and retention policies.",
            "We are kicking off a new sprint dedicated entirely to building a time-series metrics storage engine supporting automatic downsampling and retention policies.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Data Pipeline": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a real-time streaming ETL pipeline processing Kafka event topics.",
            "We have been assigned the responsibility of implementing a real-time streaming ETL pipeline processing Kafka event topics.",
            "The architectural committee requested a technical blueprint for a real-time streaming ETL pipeline processing Kafka event topics.",
            "I am the lead engineer responsible for prototyping a real-time streaming ETL pipeline processing Kafka event topics.",
            "We are kicking off a new sprint dedicated entirely to building a real-time streaming ETL pipeline processing Kafka event topics.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Search/Retrieval": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a hybrid search engine combining BM25 keyword matching and vector embeddings.",
            "We have been assigned the responsibility of implementing a hybrid search engine combining BM25 keyword matching and vector embeddings.",
            "The architectural committee requested a technical blueprint for a hybrid search engine combining BM25 keyword matching and vector embeddings.",
            "I am the lead engineer responsible for prototyping a hybrid search engine combining BM25 keyword matching and vector embeddings.",
            "We are kicking off a new sprint dedicated entirely to building a hybrid search engine combining BM25 keyword matching and vector embeddings.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Messaging/Eventing": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a partitioned publish-subscribe message broker with persistent disk storage.",
            "We have been assigned the responsibility of implementing a partitioned publish-subscribe message broker with persistent disk storage.",
            "The architectural committee requested a technical blueprint for a partitioned publish-subscribe message broker with persistent disk storage.",
            "I am the lead engineer responsible for prototyping a partitioned publish-subscribe message broker with persistent disk storage.",
            "We are kicking off a new sprint dedicated entirely to building a partitioned publish-subscribe message broker with persistent disk storage.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Networking": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a software-defined WAN (SD-WAN) dynamic path selection controller.",
            "We have been assigned the responsibility of implementing a software-defined WAN (SD-WAN) dynamic path selection controller.",
            "The architectural committee requested a technical blueprint for a software-defined WAN (SD-WAN) dynamic path selection controller.",
            "I am the lead engineer responsible for prototyping a software-defined WAN (SD-WAN) dynamic path selection controller.",
            "We are kicking off a new sprint dedicated entirely to building a software-defined WAN (SD-WAN) dynamic path selection controller.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Network Protocol": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a custom binary framing protocol for ultra-low-latency RPC communications.",
            "We have been assigned the responsibility of implementing a custom binary framing protocol for ultra-low-latency RPC communications.",
            "The architectural committee requested a technical blueprint for a custom binary framing protocol for ultra-low-latency RPC communications.",
            "I am the lead engineer responsible for prototyping a custom binary framing protocol for ultra-low-latency RPC communications.",
            "We are kicking off a new sprint dedicated entirely to building a custom binary framing protocol for ultra-low-latency RPC communications.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Cloud Infrastructure": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a multi-region active-active cloud infrastructure deployment design.",
            "We have been assigned the responsibility of implementing a multi-region active-active cloud infrastructure deployment design.",
            "The architectural committee requested a technical blueprint for a multi-region active-active cloud infrastructure deployment design.",
            "I am the lead engineer responsible for prototyping a multi-region active-active cloud infrastructure deployment design.",
            "We are kicking off a new sprint dedicated entirely to building a multi-region active-active cloud infrastructure deployment design.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Infrastructure/Platform": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an internal developer platform (IDP) for microservice scaffolding and provisioning.",
            "We have been assigned the responsibility of implementing an internal developer platform (IDP) for microservice scaffolding and provisioning.",
            "The architectural committee requested a technical blueprint for an internal developer platform (IDP) for microservice scaffolding and provisioning.",
            "I am the lead engineer responsible for prototyping an internal developer platform (IDP) for microservice scaffolding and provisioning.",
            "We are kicking off a new sprint dedicated entirely to building an internal developer platform (IDP) for microservice scaffolding and provisioning.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "DevOps/CI-CD": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an autonomous CI/CD deployment pipeline with automated quality gates.",
            "We have been assigned the responsibility of implementing an autonomous CI/CD deployment pipeline with automated quality gates.",
            "The architectural committee requested a technical blueprint for an autonomous CI/CD deployment pipeline with automated quality gates.",
            "I am the lead engineer responsible for prototyping an autonomous CI/CD deployment pipeline with automated quality gates.",
            "We are kicking off a new sprint dedicated entirely to building an autonomous CI/CD deployment pipeline with automated quality gates.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Observability/Monitoring": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a predictive anomaly detection engine for high-cardinality system metrics.",
            "We have been assigned the responsibility of implementing a predictive anomaly detection engine for high-cardinality system metrics.",
            "The architectural committee requested a technical blueprint for a predictive anomaly detection engine for high-cardinality system metrics.",
            "I am the lead engineer responsible for prototyping a predictive anomaly detection engine for high-cardinality system metrics.",
            "We are kicking off a new sprint dedicated entirely to building a predictive anomaly detection engine for high-cardinality system metrics.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Security": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere.",
            "We have been assigned the responsibility of implementing a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere.",
            "The architectural committee requested a technical blueprint for a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere.",
            "I am the lead engineer responsible for prototyping a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere.",
            "We are kicking off a new sprint dedicated entirely to building a zero-trust microservice architecture enforcing mutual TLS (mTLS) everywhere.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Reliability/Fault Tolerance": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an automated multi-region database failover and replica promotion engine.",
            "We have been assigned the responsibility of implementing an automated multi-region database failover and replica promotion engine.",
            "The architectural committee requested a technical blueprint for an automated multi-region database failover and replica promotion engine.",
            "I am the lead engineer responsible for prototyping an automated multi-region database failover and replica promotion engine.",
            "We are kicking off a new sprint dedicated entirely to building an automated multi-region database failover and replica promotion engine.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Performance/Scalability": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a high-throughput API platform capable of processing 1,000,000 requests per second.",
            "We have been assigned the responsibility of implementing a high-throughput API platform capable of processing 1,000,000 requests per second.",
            "The architectural committee requested a technical blueprint for a high-throughput API platform capable of processing 1,000,000 requests per second.",
            "I am the lead engineer responsible for prototyping a high-throughput API platform capable of processing 1,000,000 requests per second.",
            "We are kicking off a new sprint dedicated entirely to building a high-throughput API platform capable of processing 1,000,000 requests per second.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "AI/ML Feature": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an automated AI code review assistant that flags security and performance bugs.",
            "We have been assigned the responsibility of implementing an automated AI code review assistant that flags security and performance bugs.",
            "The architectural committee requested a technical blueprint for an automated AI code review assistant that flags security and performance bugs.",
            "I am the lead engineer responsible for prototyping an automated AI code review assistant that flags security and performance bugs.",
            "We are kicking off a new sprint dedicated entirely to building an automated AI code review assistant that flags security and performance bugs.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "LLM/Generative AI": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries.",
            "We have been assigned the responsibility of implementing a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries.",
            "The architectural committee requested a technical blueprint for a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries.",
            "I am the lead engineer responsible for prototyping a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries.",
            "We are kicking off a new sprint dedicated entirely to building a Retrieval-Augmented Generation (RAG) assistant for querying technical libraries.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "ML Training": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel.",
            "We have been assigned the responsibility of implementing a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel.",
            "The architectural committee requested a technical blueprint for a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel.",
            "I am the lead engineer responsible for prototyping a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel.",
            "We are kicking off a new sprint dedicated entirely to building a distributed multi-GPU model training pipeline using PyTorch Distributed Data Parallel.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Embedded Software": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a UAV flight controller firmware implementing real-time PID feedback loops.",
            "We have been assigned the responsibility of implementing a UAV flight controller firmware implementing real-time PID feedback loops.",
            "The architectural committee requested a technical blueprint for a UAV flight controller firmware implementing real-time PID feedback loops.",
            "I am the lead engineer responsible for prototyping a UAV flight controller firmware implementing real-time PID feedback loops.",
            "We are kicking off a new sprint dedicated entirely to building a UAV flight controller firmware implementing real-time PID feedback loops.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Real-Time System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a real-time flight stabilization control loop running at 1000 Hz.",
            "We have been assigned the responsibility of implementing a real-time flight stabilization control loop running at 1000 Hz.",
            "The architectural committee requested a technical blueprint for a real-time flight stabilization control loop running at 1000 Hz.",
            "I am the lead engineer responsible for prototyping a real-time flight stabilization control loop running at 1000 Hz.",
            "We are kicking off a new sprint dedicated entirely to building a real-time flight stabilization control loop running at 1000 Hz.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "IoT System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a remote device management platform monitoring 2,000,000 IoT endpoints.",
            "We have been assigned the responsibility of implementing a remote device management platform monitoring 2,000,000 IoT endpoints.",
            "The architectural committee requested a technical blueprint for a remote device management platform monitoring 2,000,000 IoT endpoints.",
            "I am the lead engineer responsible for prototyping a remote device management platform monitoring 2,000,000 IoT endpoints.",
            "We are kicking off a new sprint dedicated entirely to building a remote device management platform monitoring 2,000,000 IoT endpoints.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "PCB Design": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a 6-layer high-speed SDR controller PCB layout with controlled impedance traces.",
            "We have been assigned the responsibility of implementing a 6-layer high-speed SDR controller PCB layout with controlled impedance traces.",
            "The architectural committee requested a technical blueprint for a 6-layer high-speed SDR controller PCB layout with controlled impedance traces.",
            "I am the lead engineer responsible for prototyping a 6-layer high-speed SDR controller PCB layout with controlled impedance traces.",
            "We are kicking off a new sprint dedicated entirely to building a 6-layer high-speed SDR controller PCB layout with controlled impedance traces.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Digital Electronics": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an FPGA-based digital logic block for high-speed signal processing.",
            "We have been assigned the responsibility of implementing an FPGA-based digital logic block for high-speed signal processing.",
            "The architectural committee requested a technical blueprint for an FPGA-based digital logic block for high-speed signal processing.",
            "I am the lead engineer responsible for prototyping an FPGA-based digital logic block for high-speed signal processing.",
            "We are kicking off a new sprint dedicated entirely to building an FPGA-based digital logic block for high-speed signal processing.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Analog Electronics": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a low-noise analog front-end amplifier for a 24-bit high-resolution ADC.",
            "We have been assigned the responsibility of implementing a low-noise analog front-end amplifier for a 24-bit high-resolution ADC.",
            "The architectural committee requested a technical blueprint for a low-noise analog front-end amplifier for a 24-bit high-resolution ADC.",
            "I am the lead engineer responsible for prototyping a low-noise analog front-end amplifier for a 24-bit high-resolution ADC.",
            "We are kicking off a new sprint dedicated entirely to building a low-noise analog front-end amplifier for a 24-bit high-resolution ADC.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "RF Feature": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an adaptive frequency hopping subsystem for drone communication links.",
            "We have been assigned the responsibility of implementing an adaptive frequency hopping subsystem for drone communication links.",
            "The architectural committee requested a technical blueprint for an adaptive frequency hopping subsystem for drone communication links.",
            "I am the lead engineer responsible for prototyping an adaptive frequency hopping subsystem for drone communication links.",
            "We are kicking off a new sprint dedicated entirely to building an adaptive frequency hopping subsystem for drone communication links.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "RF Hardware": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit.",
            "We have been assigned the responsibility of implementing a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit.",
            "The architectural committee requested a technical blueprint for a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit.",
            "I am the lead engineer responsible for prototyping a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit.",
            "We are kicking off a new sprint dedicated entirely to building a 2.4 GHz low-noise amplifier (LNA) RF receiver front-end circuit.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Antenna System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an airborne mesh-network node antenna system design.",
            "We have been assigned the responsibility of implementing an airborne mesh-network node antenna system design.",
            "The architectural committee requested a technical blueprint for an airborne mesh-network node antenna system design.",
            "I am the lead engineer responsible for prototyping an airborne mesh-network node antenna system design.",
            "We are kicking off a new sprint dedicated entirely to building an airborne mesh-network node antenna system design.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Signal Processing": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a Doppler radar signal processing pipeline for target velocity estimation.",
            "We have been assigned the responsibility of implementing a Doppler radar signal processing pipeline for target velocity estimation.",
            "The architectural committee requested a technical blueprint for a Doppler radar signal processing pipeline for target velocity estimation.",
            "I am the lead engineer responsible for prototyping a Doppler radar signal processing pipeline for target velocity estimation.",
            "We are kicking off a new sprint dedicated entirely to building a Doppler radar signal processing pipeline for target velocity estimation.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Wireless Communications": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a resilient air-to-air broadband data link between autonomous UAVs.",
            "We have been assigned the responsibility of implementing a resilient air-to-air broadband data link between autonomous UAVs.",
            "The architectural committee requested a technical blueprint for a resilient air-to-air broadband data link between autonomous UAVs.",
            "I am the lead engineer responsible for prototyping a resilient air-to-air broadband data link between autonomous UAVs.",
            "We are kicking off a new sprint dedicated entirely to building a resilient air-to-air broadband data link between autonomous UAVs.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Mechanical System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a two-axis mechanical radar antenna mounting and drive assembly.",
            "We have been assigned the responsibility of implementing a two-axis mechanical radar antenna mounting and drive assembly.",
            "The architectural committee requested a technical blueprint for a two-axis mechanical radar antenna mounting and drive assembly.",
            "I am the lead engineer responsible for prototyping a two-axis mechanical radar antenna mounting and drive assembly.",
            "We are kicking off a new sprint dedicated entirely to building a two-axis mechanical radar antenna mounting and drive assembly.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Electromechanical System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an automated antenna positioning system driven by stepper motors.",
            "We have been assigned the responsibility of implementing an automated antenna positioning system driven by stepper motors.",
            "The architectural committee requested a technical blueprint for an automated antenna positioning system driven by stepper motors.",
            "I am the lead engineer responsible for prototyping an automated antenna positioning system driven by stepper motors.",
            "We are kicking off a new sprint dedicated entirely to building an automated antenna positioning system driven by stepper motors.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Power System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a complete electrical power and battery architecture for long-endurance UAVs.",
            "We have been assigned the responsibility of implementing a complete electrical power and battery architecture for long-endurance UAVs.",
            "The architectural committee requested a technical blueprint for a complete electrical power and battery architecture for long-endurance UAVs.",
            "I am the lead engineer responsible for prototyping a complete electrical power and battery architecture for long-endurance UAVs.",
            "We are kicking off a new sprint dedicated entirely to building a complete electrical power and battery architecture for long-endurance UAVs.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Hardware/Software Integration": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a Software-Defined Radio (SDR) integration bridging hardware and DSP code.",
            "We have been assigned the responsibility of implementing a Software-Defined Radio (SDR) integration bridging hardware and DSP code.",
            "The architectural committee requested a technical blueprint for a Software-Defined Radio (SDR) integration bridging hardware and DSP code.",
            "I am the lead engineer responsible for prototyping a Software-Defined Radio (SDR) integration bridging hardware and DSP code.",
            "We are kicking off a new sprint dedicated entirely to building a Software-Defined Radio (SDR) integration bridging hardware and DSP code.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "System Integration": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a drone mesh-network subsystem integrated with ground control stations.",
            "We have been assigned the responsibility of implementing a drone mesh-network subsystem integrated with ground control stations.",
            "The architectural committee requested a technical blueprint for a drone mesh-network subsystem integrated with ground control stations.",
            "I am the lead engineer responsible for prototyping a drone mesh-network subsystem integrated with ground control stations.",
            "We are kicking off a new sprint dedicated entirely to building a drone mesh-network subsystem integrated with ground control stations.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Manufacturing/Test": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing an automated production test fixture for populated circuit board assemblies.",
            "We have been assigned the responsibility of implementing an automated production test fixture for populated circuit board assemblies.",
            "The architectural committee requested a technical blueprint for an automated production test fixture for populated circuit board assemblies.",
            "I am the lead engineer responsible for prototyping an automated production test fixture for populated circuit board assemblies.",
            "We are kicking off a new sprint dedicated entirely to building an automated production test fixture for populated circuit board assemblies.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Migration/Modernization": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a monolithic application migration to a microservices-based architecture.",
            "We have been assigned the responsibility of implementing a monolithic application migration to a microservices-based architecture.",
            "The architectural committee requested a technical blueprint for a monolithic application migration to a microservices-based architecture.",
            "I am the lead engineer responsible for prototyping a monolithic application migration to a microservices-based architecture.",
            "We are kicking off a new sprint dedicated entirely to building a monolithic application migration to a microservices-based architecture.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Aerospace/Airframe Design": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload.",
            "We have been assigned the responsibility of implementing a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload.",
            "The architectural committee requested a technical blueprint for a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload.",
            "I am the lead engineer responsible for prototyping a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload.",
            "We are kicking off a new sprint dedicated entirely to building a VTOL UAV airframe layout capable of carrying a 5 kg sensor payload.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Aerodynamics": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a fixed-wing UAV drag reduction and longitudinal stability design.",
            "We have been assigned the responsibility of implementing a fixed-wing UAV drag reduction and longitudinal stability design.",
            "The architectural committee requested a technical blueprint for a fixed-wing UAV drag reduction and longitudinal stability design.",
            "I am the lead engineer responsible for prototyping a fixed-wing UAV drag reduction and longitudinal stability design.",
            "We are kicking off a new sprint dedicated entirely to building a fixed-wing UAV drag reduction and longitudinal stability design.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Propulsion System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a motor and propeller selection optimization for long-endurance quadcopters.",
            "We have been assigned the responsibility of implementing a motor and propeller selection optimization for long-endurance quadcopters.",
            "The architectural committee requested a technical blueprint for a motor and propeller selection optimization for long-endurance quadcopters.",
            "I am the lead engineer responsible for prototyping a motor and propeller selection optimization for long-endurance quadcopters.",
            "We are kicking off a new sprint dedicated entirely to building a motor and propeller selection optimization for long-endurance quadcopters.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Mechanical Mechanism": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a retractable antenna deployment mechanism for aircraft enclosures.",
            "We have been assigned the responsibility of implementing a retractable antenna deployment mechanism for aircraft enclosures.",
            "The architectural committee requested a technical blueprint for a retractable antenna deployment mechanism for aircraft enclosures.",
            "I am the lead engineer responsible for prototyping a retractable antenna deployment mechanism for aircraft enclosures.",
            "We are kicking off a new sprint dedicated entirely to building a retractable antenna deployment mechanism for aircraft enclosures.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Structural/Load-Bearing Design": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a lightweight electronics mount engineered for high-vibration aircraft.",
            "We have been assigned the responsibility of implementing a lightweight electronics mount engineered for high-vibration aircraft.",
            "The architectural committee requested a technical blueprint for a lightweight electronics mount engineered for high-vibration aircraft.",
            "I am the lead engineer responsible for prototyping a lightweight electronics mount engineered for high-vibration aircraft.",
            "We are kicking off a new sprint dedicated entirely to building a lightweight electronics mount engineered for high-vibration aircraft.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Electrical Circuit Design": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing the power and control circuitry for a motorized antenna mount.",
            "We have been assigned the responsibility of implementing the power and control circuitry for a motorized antenna mount.",
            "The architectural committee requested a technical blueprint for the power and control circuitry for a motorized antenna mount.",
            "I am the lead engineer responsible for prototyping the power and control circuitry for a motorized antenna mount.",
            "We are kicking off a new sprint dedicated entirely to building the power and control circuitry for a motorized antenna mount.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Power Electronics": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics.",
            "We have been assigned the responsibility of implementing a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics.",
            "The architectural committee requested a technical blueprint for a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics.",
            "I am the lead engineer responsible for prototyping a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics.",
            "We are kicking off a new sprint dedicated entirely to building a high-efficiency 48 V to 12 V DC/DC buck converter for airborne electronics.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "EMI/EMC/Noise Mitigation": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a switching regulator noise mitigation strategy for sensitive RF receivers.",
            "We have been assigned the responsibility of implementing a switching regulator noise mitigation strategy for sensitive RF receivers.",
            "The architectural committee requested a technical blueprint for a switching regulator noise mitigation strategy for sensitive RF receivers.",
            "I am the lead engineer responsible for prototyping a switching regulator noise mitigation strategy for sensitive RF receivers.",
            "We are kicking off a new sprint dedicated entirely to building a switching regulator noise mitigation strategy for sensitive RF receivers.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Sensor/Instrumentation System": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a current, voltage, and temperature monitoring subsystem for drone power.",
            "We have been assigned the responsibility of implementing a current, voltage, and temperature monitoring subsystem for drone power.",
            "The architectural committee requested a technical blueprint for a current, voltage, and temperature monitoring subsystem for drone power.",
            "I am the lead engineer responsible for prototyping a current, voltage, and temperature monitoring subsystem for drone power.",
            "We are kicking off a new sprint dedicated entirely to building a current, voltage, and temperature monitoring subsystem for drone power.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
    "Thermal Management": {
        "background_project_info": [
            "Our legacy implementation was built as a monolithic service, but as traffic grew to 200,000 active users, operational overhead became unmanageable.",
            "The corporation's monolithic service infrastructure has network latency issues that are causing customers to lose the actionable window in the real-time stock trading market.",
            "Our prior microservice deployment strategy failed to scale during the holiday rush, leading to frequent timeouts and lost transactions.",
            "We recently secured Series B funding and need to overhaul our internal systems to prepare for an aggressive European market expansion.",
            "The current solution was initially developed as a quick prototype, but it has now become a critical dependency with severe technical debt.",
        ],
        "specific_project_details": [
            "Our team is tasked with designing a cooling system for a 100 W RF power amplifier inside a sealed enclosure.",
            "We have been assigned the responsibility of implementing a cooling system for a 100 W RF power amplifier inside a sealed enclosure.",
            "The architectural committee requested a technical blueprint for a cooling system for a 100 W RF power amplifier inside a sealed enclosure.",
            "I am the lead engineer responsible for prototyping a cooling system for a 100 W RF power amplifier inside a sealed enclosure.",
            "We are kicking off a new sprint dedicated entirely to building a cooling system for a 100 W RF power amplifier inside a sealed enclosure.",
        ],
        "problem_overview": [
            "Currently, our system handles approximately 200,000 requests per second across 3 AWS regions, but during peak load we experience significant performance degradation.",
            "System throughput has plateaued while hardware costs are rising exponentially due to inefficient resource utilization.",
            "We are seeing a high rate of data inconsistency and race conditions during concurrent user operations.",
            "Our database locks up entirely whenever the analytics team runs their daily heavy aggregation queries.",
            "The application crashes silently under memory pressure, causing us to manually restart the pods multiple times a day.",
        ],
        "caveats_and_considerations": [
            "Our organization manages over 200,000 records and needs to ensure compliance with strict SOC2 and GDPR security requirements.",
            "The solution must be fully backwards-compatible with our V1 API clients to avoid breaking legacy integrations.",
            "We cannot rely on third-party SaaS vendors for this component due to strict data sovereignty laws.",
            "The system must gracefully handle intermittent connectivity drops without data loss or corruption.",
            "Security is our absolute highest priority; any potential for data exfiltration is a hard failure.",
        ],
        "the_request": [
            "Please provide a detailed architectural specification including:\n- Functional and non-functional requirements\n- Component architecture diagrams and data flows",
            "I need you to draft a comprehensive RFC outlining the system design, API contracts, and database schemas.",
            "Could you generate a complete technical design document detailing the architecture, potential failure modes, and mitigation strategies?",
            "Please act as a Staff Engineer and present a detailed architectural proposal to solve this.",
            "Generate a structured engineering design doc covering the system architecture, required components, and deployment steps.",
        ],
        "constraints_and_limitations": [
            "The operational budget is constrained, so we must optimize for low resource consumption and minimal maintenance burden.",
            "We have a hard deadline of 3 months to deliver this MVP, so we cannot afford to build everything from scratch.",
            "The hardware environment is highly constrained, limited to only 256MB of RAM and intermittent connectivity.",
            "We are limited to a very small DevOps team, meaning the infrastructure must be entirely self-healing.",
            "Due to regulatory compliance, all data processing must occur strictly on-premise without touching the public internet.",
        ],
        "current_architecture": [
            "We currently rely on a monolithic architecture that is reaching its end of life.",
            "Our stack consists of a React frontend talking to a Node.js backend, backed by a single PostgreSQL database.",
            "We operate a sprawling mesh of over 500 microservices communicating synchronously via REST.",
            "The system is currently composed of heavily fragmented serverless functions that are difficult to orchestrate.",
            "Our legacy architecture relies on an aging mainframe doing nightly batch processing to a data warehouse.",
        ],
        "target_audience": [
            "This design document will be reviewed by the principal engineering group.",
            "The primary audience for this RFC consists of junior engineers who will be tasked with implementation.",
            "Keep in mind this document will be presented to non-technical stakeholders and executive leadership.",
            "This proposal is intended for the security and compliance review board.",
            "The document will serve as the primary onboarding guide for new developers joining the team.",
        ],
        "success_criteria": [
            "We expect the system to scale to 200,000 concurrent connections while maintaining zero-downtime availability.",
            "The project will be considered successful if we reduce p99 response times to under 10ms.",
            "Success means handling the daily batch processing load within a 2-hour window instead of 8 hours.",
            "We need to achieve 99.999% availability even in the event of a complete availability zone outage.",
            "The feature must support a sustained throughput of 50,000 events per second with zero data loss.",
        ],
        "tech_stack": [
            "We are an AWS shop and heavily rely on Kubernetes.",
            "The implementation must exclusively use Python, FastAPI, and Redis. Do not suggest Java.",
            "Our organization strongly prefers open-source, vendor-neutral technologies like Kafka and PostgreSQL.",
            "We use Google Cloud Platform for all of our compute, and BigQuery for data warehousing.",
            "The codebase is primarily Go and Rust, and we use gRPC for internal service communication.",
        ],
        "expected_output_format": [
            "Please output the design in markdown format with appropriate headers.",
            "Format your response strictly as a bulleted checklist accompanied by Mermaid.js sequence diagrams.",
            "I expect a narrative explanation broken down into Problem, Proposal, and Alternatives Considered.",
            "Please structure the output exactly like a standard AWS Well-Architected Framework review.",
            "Provide the output as a step-by-step implementation guide with code snippets for the core interfaces.",
        ],
        "assumptions": [
            "Assume that all internal network traffic is trusted and unencrypted.",
            "You can assume that user authentication is already handled upstream by our API gateway.",
            "For this design, assume we have infinite storage capacity and prioritize read speeds.",
            "Assume that the average payload size is small, roughly 2 KB per request.",
            "Assume our team has the technical expertise to maintain whatever complex system you propose.",
        ],
        "alternative_approaches_rejected": [
            "We have already ruled out a pure serverless approach due to cold start latency.",
            "We previously attempted a polling architecture, but it resulted in unacceptable delays.",
            "Do not suggest a NoSQL database; we evaluated MongoDB and it did not fit our relational data model.",
            "We tried utilizing a message queue, but maintaining strict ordering proved to be too complex.",
            "We rejected a graph database approach because the operational overhead was too high for our team.",
        ],
    },
}

import os
import json
import re
import torch
import spacy
from collections import defaultdict
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from gliner import GLiNER

def clean_bert_word(w):
    return w.replace("##", "").replace("Ġ", "").strip()

# Configuration & Constants for Extraction Pipeline
SIMILARITY_THRESHOLD = 0.3
MIN_PHRASE_WORDS = 2
MAX_PHRASE_WORDS = 5
MIN_VOTES_REQUIRED_STANDARD = 2
MIN_VOTES_REQUIRED_PROPN_INJECTED = 2  # Majority (2 out of 3) for standalone PROPN
CLASSIFIER_BATCH_SIZE = 32
HYPOTHESIS_TEMPLATE = "In this technical context, this phrase represents a {}."
DEVICE_ID = 0 if torch.cuda.is_available() else -1

GLINER_ENTITY_LABELS = ["software product", "programming language", "framework", "database", "cloud provider", "technology", "library"]
DISALLOWED_1WORD_POS = ('PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PUNCT')
DISALLOWED_EDGE_POS_START = ('PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PUNCT', 'VERB', 'AUX')
DISALLOWED_EDGE_POS_END = ('PRON', 'DET', 'ADP', 'CCONJ', 'SCONJ', 'PUNCT', 'VERB', 'AUX', 'PART')
VALID_DEP_TAGS = ('dobj', 'pobj', 'nsubj', 'nsubjpass', 'attr', 'conj')

# Global variables to hold our loaded models
MODELS = None

def load_models():
    global MODELS
    if MODELS is not None:
        return MODELS
        
    print("Loading ML Models (this may take a minute)...")
    nlp = spacy.load("en_core_web_sm")
    embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=DEVICE_ID)
    
    gliner_model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
    if torch.cuda.is_available():
        gliner_model = gliner_model.to("cuda")
        
    ner_it = pipeline("ner", model="Nucha/Nucha_ITSkillNER_BERT", aggregation_strategy="simple", device=DEVICE_ID)
    ner_sw = pipeline("ner", model="mrm8488/codebert-base-finetuned-stackoverflow-ner", aggregation_strategy="simple", device=DEVICE_ID)
    
    MODELS = {
        'nlp': nlp,
        'embedder': embedder,
        'classifier': classifier,
        'gliner_model': gliner_model,
        'ner_it': ner_it,
        'ner_sw': ner_sw
    }
    return MODELS

def clean_bert_word(w):
    return w.replace("##", "").replace("Ġ", "").strip()

def is_word_in_entity_list(word, entity_list):
    word_l = word.lower()
    for ent in entity_list:
        if word_l in ent or ent in word_l:
            return True
    return False

# We cache entity votes per sentence to avoid running Heavy NER on the same sentence twice
SENTENCE_ENTITY_CACHE = {}

def process_paragraphs(paragraphs, return_debug=False):
    """
    Process a list of paragraph strings.
    If return_debug is True, it returns a list of detailed dictionaries tracing the ML steps.
    If False, it acts like the normal extractor.
    """
    models = load_models()
    nlp = models['nlp']
    embedder = models['embedder']
    gliner_model = models['gliner_model']
    ner_it = models['ner_it']
    ner_sw = models['ner_sw']
    
    results = []
    
    for p_text in paragraphs:
        doc = nlp(p_text)
        
        debug_info = {
            "spacy_raw": [],
            "cleaned_subtrees": [],
            "length_validation": [],
            "voting_gate": [],
            "keybert_scores": [],
            "final_spans": []
        }
        
        candidate_spans = []
        pre_validated_1word_texts = set()

        def evaluate_candidate(token_list, source_label="", min_votes=MIN_VOTES_REQUIRED_STANDARD):
            if not token_list:
                return

            if len(token_list) == 1:
                start_idx = 0
                while start_idx < len(token_list) and token_list[start_idx].pos_ in DISALLOWED_1WORD_POS:
                    start_idx += 1
                end_idx = len(token_list) - 1
                while end_idx >= start_idx and token_list[end_idx].pos_ in DISALLOWED_1WORD_POS:
                    end_idx -= 1
            else:
                start_idx = 0
                while start_idx < len(token_list) and token_list[start_idx].pos_ in DISALLOWED_EDGE_POS_START:
                    start_idx += 1
                    
                end_idx = len(token_list) - 1
                while end_idx >= start_idx and token_list[end_idx].pos_ in DISALLOWED_EDGE_POS_END:
                    end_idx -= 1
                
            if start_idx <= end_idx:
                cleaned_tokens = token_list[start_idx:end_idx+1]
                start_char = cleaned_tokens[0].idx
                end_char = cleaned_tokens[-1].idx + len(cleaned_tokens[-1].text)
                candidate_text = p_text[start_char:end_char].strip()
                
                debug_info["cleaned_subtrees"].append({
                    "root_token": source_label,
                    "cleaned_text": candidate_text,
                    "pos_array": [t.pos_ for t in cleaned_tokens]
                })
                
                if 1 <= len(cleaned_tokens) <= MAX_PHRASE_WORDS:
                    is_contiguous = True
                    for i in range(len(cleaned_tokens) - 1):
                        if cleaned_tokens[i+1].i - cleaned_tokens[i].i > 1:
                            is_contiguous = False
                            break
                            
                    if is_contiguous:
                        words = candidate_text.split()
                        if "\n" not in candidate_text:
                            if MIN_PHRASE_WORDS <= len(words) <= MAX_PHRASE_WORDS:
                                # Avoid merging distinct entities conjoined by 'and' / 'or'
                                has_internal_conjunction = any(
                                    t.pos_ == 'CCONJ' or t.text.lower() in ('and', 'or', '&')
                                    for t in cleaned_tokens[1:-1]
                                )
                                if has_internal_conjunction:
                                    debug_info["length_validation"].append({
                                        "candidate": candidate_text,
                                        "status": "FAILED (Contains internal conjunction list)"
                                    })
                                else:
                                    debug_info["length_validation"].append({
                                        "candidate": candidate_text,
                                        "status": f"PASSED ({MIN_PHRASE_WORDS}-{MAX_PHRASE_WORDS} words)"
                                    })
                                    candidate_spans.append((start_char, end_char, candidate_text))
                            elif len(words) == 1:
                                if p_text not in SENTENCE_ENTITY_CACHE:
                                    gliner_ents = gliner_model.predict_entities(p_text, GLINER_ENTITY_LABELS)
                                    m1_texts = [e["text"].lower() for e in gliner_ents]
                                    
                                    it_ents = ner_it(p_text)
                                    m2_texts = [clean_bert_word(e["word"]).lower() for e in it_ents]
                                    
                                    sw_ents = ner_sw(p_text)
                                    m3_texts = [clean_bert_word(e["word"]).lower() for e in sw_ents]
                                    
                                    SENTENCE_ENTITY_CACHE[p_text] = (m1_texts, m2_texts, m3_texts)
                                    
                                m1_t, m2_t, m3_t = SENTENCE_ENTITY_CACHE[p_text]
                                
                                v1 = is_word_in_entity_list(candidate_text, m1_t)
                                v2 = is_word_in_entity_list(candidate_text, m2_t)
                                v3 = is_word_in_entity_list(candidate_text, m3_t)
                                
                                votes = sum([v1, v2, v3])
                                
                                debug_info["voting_gate"].append({
                                    "candidate": candidate_text,
                                    "source": source_label,
                                    "gliner_vote": v1,
                                    "itskill_vote": v2,
                                    "so_vote": v3,
                                    "total_votes": votes,
                                    "required": min_votes,
                                    "passed": votes >= min_votes
                                })
                                
                                if votes >= min_votes:
                                    candidate_spans.append((start_char, end_char, candidate_text))
                                    pre_validated_1word_texts.add(candidate_text)
                            else:
                                debug_info["length_validation"].append({
                                    "candidate": candidate_text,
                                    "status": f"FAILED (Length > {MAX_PHRASE_WORDS})"
                                })
                else:
                    debug_info["length_validation"].append({
                        "candidate": " ".join([t.text for t in cleaned_tokens]),
                        "status": "FAILED (Length out of bounds)"
                    })
        
        # 1. Evaluate Subtrees from Syntactic Roots
        for token in doc:
            if token.dep_ in VALID_DEP_TAGS:
                subtree = list(token.subtree)
                if subtree:
                    subtree.sort(key=lambda x: x.i)
                    debug_info["spacy_raw"].append({
                        "token": token.text,
                        "dep": token.dep_,
                        "subtree": " ".join([t.text for t in subtree])
                    })
                    evaluate_candidate(subtree, source_label=f"subtree({token.text})")

        # 2. Evaluate Base Noun Chunks (captures phrases without attached clauses)
        for chunk in doc.noun_chunks:
            chunk_tokens = list(chunk)
            debug_info["spacy_raw"].append({
                "token": chunk.root.text,
                "dep": f"noun_chunk({chunk.root.dep_})",
                "subtree": chunk.text
            })
            evaluate_candidate(chunk_tokens, source_label=f"chunk({chunk.root.text})")

        # 3. Evaluate Standalone PROPN (Proper Nouns) with 2/3 vote requirement
        for token in doc:
            if token.pos_ == 'PROPN':
                debug_info["spacy_raw"].append({
                    "token": token.text,
                    "dep": f"propn({token.dep_})",
                    "subtree": token.text
                })
                evaluate_candidate([token], source_label=f"propn({token.text})", min_votes=MIN_VOTES_REQUIRED_PROPN_INJECTED)

        # 4. Evaluate Entities Proposed by Any Ensemble Model (catches mistagged words like 'Go' tagged as VERB)
        if p_text not in SENTENCE_ENTITY_CACHE:
            gliner_ents = gliner_model.predict_entities(p_text, GLINER_ENTITY_LABELS)
            m1_texts = [e["text"].lower() for e in gliner_ents]
            
            it_ents = ner_it(p_text)
            m2_texts = [clean_bert_word(e["word"]).lower() for e in it_ents]
            
            sw_ents = ner_sw(p_text)
            m3_texts = [clean_bert_word(e["word"]).lower() for e in sw_ents]
            
            SENTENCE_ENTITY_CACHE[p_text] = (m1_texts, m2_texts, m3_texts)
            
        m1_t, m2_t, m3_t = SENTENCE_ENTITY_CACHE[p_text]
        all_proposed_entities = set(m1_t + m2_t + m3_t)

        for ent_text in all_proposed_entities:
            clean_ent = ent_text.strip()
            if not clean_ent:
                continue
            # Match whole word boundaries in original text
            pattern = re.compile(rf"\b{re.escape(clean_ent)}\b", re.IGNORECASE)
            for match in pattern.finditer(p_text):
                ent_start, ent_end = match.span()
                ent_span = doc.char_span(ent_start, ent_end)
                if ent_span is not None:
                    evaluate_candidate(list(ent_span), source_label=f"model_proposal({clean_ent})", min_votes=MIN_VOTES_REQUIRED_STANDARD)
        
        candidate_spans = list(set(candidate_spans))
        final_spans = []
        
        if candidate_spans:
            sentence_emb = embedder.encode(p_text, convert_to_tensor=True)
            candidate_texts = [text for _, _, text in candidate_spans]
            candidate_embs = embedder.encode(candidate_texts, convert_to_tensor=True)
            
            cosine_scores = util.cos_sim(sentence_emb, candidate_embs)[0]
            
            for i, score in enumerate(cosine_scores):
                sc = score.item()
                c_text = candidate_spans[i][2]
                is_pre_val_1w = (c_text in pre_validated_1word_texts and len(c_text.split()) == 1)
                passed_keybert = (sc >= SIMILARITY_THRESHOLD) or is_pre_val_1w

                debug_info["keybert_scores"].append({
                    "candidate": c_text,
                    "score": sc,
                    "passed": passed_keybert,
                    "bypassed_due_to_vote": is_pre_val_1w and (sc < SIMILARITY_THRESHOLD)
                })
                if passed_keybert:
                    final_spans.append(candidate_spans[i])
                    
            final_spans.sort(key=lambda x: (len(x[2]), x[0]), reverse=True)
            
            non_overlapping = []
            for span in final_spans:
                overlap = False
                for existing in non_overlapping:
                    if not (span[1] <= existing[0] or span[0] >= existing[1]):
                        overlap = True
                        break
                if not overlap:
                    non_overlapping.append(span)
            
            non_overlapping.sort(key=lambda x: x[0], reverse=True)
            final_spans = non_overlapping
            
        debug_info["final_spans"] = [s[2] for s in final_spans]
        
        results.append({
            "paragraph": p_text,
            "char_spans": final_spans,
            "debug": debug_info
        })
        
    return results

def run_extraction_v1_with_voting():
    print("Starting Main Extraction Pipeline...")
    
    # Pre-load to initialize cache
    models = load_models()
    classifier = models['classifier']
    
    unique_concepts = {}
    paragraphs_with_spans = []

    categories = [
        "system_or_project", "problem_or_issue", "the_ask", "the_action",
        "technology_or_tool", "requirement_or_constraint", "metric_or_scale",
        "actor_or_role", "environment_or_context", "outcome_or_result",
        "action_verb", "miscellaneous"
    ]

    print("Processing all CATEGORY_PARAGRAPHS...")
    for cat_name, p_types in CATEGORY_PARAGRAPHS.items():
        for p_type, paragraphs in p_types.items():
            results = process_paragraphs(paragraphs, return_debug=False)
            for res in results:
                p_text = res["paragraph"]
                char_spans = res["char_spans"]
                paragraphs_with_spans.append((cat_name, p_type, p_text, char_spans))
                
                for span in char_spans:
                    if span[2] not in unique_concepts:
                        unique_concepts[span[2]] = p_text

    print(f"Extracted {len(unique_concepts)} unique concepts.")

    print("Classifying concepts contextually...")
    string_to_category = {}
    items = list(unique_concepts.items())

    for i in range(0, len(items), CLASSIFIER_BATCH_SIZE):
        batch = items[i:i+CLASSIFIER_BATCH_SIZE]
        premises = [f"Consider the term '{concept}' within this sentence: '{context}'" for concept, context in batch]
        results = classifier(
            premises,
            candidate_labels=categories,
            hypothesis_template=HYPOTHESIS_TEMPLATE,
            batch_size=CLASSIFIER_BATCH_SIZE
        )
        if isinstance(results, dict):
            results = [results]
        for j, res in enumerate(results):
            concept = batch[j][0]
            string_to_category[concept] = res["labels"][0]
        
        if (i + CLASSIFIER_BATCH_SIZE) % 32 == 0 or (i + CLASSIFIER_BATCH_SIZE) >= len(items):
            print(f"Classified {min(i+CLASSIFIER_BATCH_SIZE, len(items))}/{len(items)}")

    print("Assigning IDs and grouping...")
    category_counters = defaultdict(int)
    string_to_id = {}
    grouped_template_values = defaultdict(dict)

    for concept in unique_concepts.keys():
        cat = string_to_category[concept]
        category_counters[cat] += 1
        new_id = f"{cat}_{category_counters[cat]}"
        string_to_id[concept] = new_id
        grouped_template_values[cat][new_id] = concept

    print("Templating paragraphs...")
    TEMPLATED_CATEGORY_PARAGRAPHS = defaultdict(lambda: defaultdict(list))
    for cat_name, p_type, p_text, char_spans in paragraphs_with_spans:
        new_text = p_text
        for start_char, end_char, text_val in char_spans:
            if text_val in string_to_id:
                placeholder = f"{{{string_to_id[text_val]}}}"
                new_text = new_text[:start_char] + placeholder + new_text[end_char:]
        TEMPLATED_CATEGORY_PARAGRAPHS[cat_name][p_type].append(new_text)

    for k in TEMPLATED_CATEGORY_PARAGRAPHS:
        TEMPLATED_CATEGORY_PARAGRAPHS[k] = dict(TEMPLATED_CATEGORY_PARAGRAPHS[k])
    TEMPLATED_CATEGORY_PARAGRAPHS = dict(TEMPLATED_CATEGORY_PARAGRAPHS)

    print("Writing to file...")
    output = "TEMPLATE_VALUES = {\n"
    for cat in categories:
        if cat in grouped_template_values and len(grouped_template_values[cat]) > 0:
            output += f"    # {cat}\n"
            for k, v in grouped_template_values[cat].items():
                v_escaped = v.replace('\n', '\\n').replace('"', '\\"')
                output += f'    "{k}": "{v_escaped}",\n'
            output += "\n"
    output += "}\n"

    output += "\nTEMPLATED_CATEGORY_PARAGRAPHS = " + json.dumps(TEMPLATED_CATEGORY_PARAGRAPHS, indent=4) + "\n"

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt_data_generator_v1.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
        
    print(f"V1 Pipeline completed! {output_path} generated.")

if __name__ == "__main__":
    run_extraction_v1_with_voting()
