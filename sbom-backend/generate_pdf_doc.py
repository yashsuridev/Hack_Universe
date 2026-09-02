import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

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
        if self._pageNumber == 1:
            return  # Suppress running header/footer on cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header text & line
        self.drawString(54, 752, "AUTOMATED SOFTWARE SUPPLY CHAIN SECURITY & SBOM AUDITOR")
        self.setFont("Helvetica", 8)
        self.drawRightString(558, 752, "TECHNICAL SPECIFICATION REPORT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 744, 558, 744)

        # Footer line & text
        self.line(54, 48, 558, 48)
        self.setFont("Helvetica", 8)
        self.drawString(54, 36, "Confidential — System Architecture & Source Code Documentation")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.restoreState()


def create_pdf(output_filename="SBOM_Auditor_Project_Documentation.pdf"):
    pdf_path = os.path.abspath(output_filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'),
        alignment=0,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=0,
        spaceAfter=25
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    tbl_header_style = ParagraphStyle(
        'TblHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    tbl_cell_code = ParagraphStyle(
        'TblCellCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E3A8A')
    )

    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("AUTOMATED SOFTWARE SUPPLY CHAIN SECURITY & SBOM AUDITOR", title_style))
    story.append(Paragraph("Comprehensive Architecture, Workflow Engine, and Source Code Technical Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor("#2563EB"), spaceAfter=30))

    meta_data = [
        [Paragraph("Project Name", meta_label_style), Paragraph("Automated Software Supply Chain Security & SBOM Auditor", meta_val_style)],
        [Paragraph("Project Type", meta_label_style), Paragraph("Cybersecurity / Software Supply Chain Security Platform", meta_val_style)],
        [Paragraph("Frontend Stack", meta_label_style), Paragraph("React 18, TypeScript, Vite 5, React Router DOM v6, Tailwind CSS, Lucide Icons", meta_val_style)],
        [Paragraph("Backend Stack", meta_label_style), Paragraph("Python 3.14 / 3.13, FastAPI 0.115, Uvicorn, Pydantic v2, Structlog", meta_val_style)],
        [Paragraph("Database / ORM", meta_label_style), Paragraph("SQLite 3 (sbom_auditor_v2.db), SQLAlchemy 2.0 ORM", meta_val_style)],
        [Paragraph("External Intelligence APIs", meta_label_style), Paragraph("Google OSV.dev Batch Vulnerability API v1, npm Registry, PyPI API, Maven Central Solr API", meta_val_style)],
        [Paragraph("Supported Ecosystems", meta_label_style), Paragraph("npm (Node.js/JS/TS), PyPI (Python), Maven (Java/Kotlin/Gradle)", meta_val_style)],
        [Paragraph("SBOM Specifications", meta_label_style), Paragraph("CycloneDX v1.5 JSON, SPDX v2.3 JSON", meta_val_style)],
        [Paragraph("Document Status", meta_label_style), Paragraph("Complete Verified Technical Documentation", meta_val_style)],
        [Paragraph("Date", meta_label_style), Paragraph("August 2026", meta_val_style)],
    ]

    meta_table = Table(meta_data, colWidths=[150, 354])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 40))
    summary_box = [
        [Paragraph("<b>Executive Summary:</b> This technical documentation provides an in-depth, verified breakdown of the Automated Software Supply Chain Security & SBOM Auditor codebase. It outlines the end-to-end security pipeline, directory hierarchy, core data models, REST API specifications, static manifest parsers, vulnerability scanning engines, risk scoring algorithms, and React frontend state architecture.", body_style)]
    ]
    summary_table = Table(summary_box, colWidths=[504])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(summary_table)
    story.append(PageBreak())

    # =========================================================================
    # 2. PROJECT OVERVIEW
    # =========================================================================
    story.append(Paragraph("1. Project Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    story.append(Paragraph("<b>1.1 Non-Technical Overview (High-Level Purpose)</b>", h2_style))
    story.append(Paragraph(
        "Modern software development relies heavily on open-source third-party libraries and packages. While these libraries accelerate development, they create a massive <b>Software Supply Chain</b> risk. When an open-source dependency contains a known vulnerability or malicious code, every application consuming that library becomes exposed to security exploits.",
        body_style
    ))
    story.append(Paragraph(
        "The <b>Automated Software Supply Chain Security & SBOM Auditor</b> acts as an automated digital security inspector. Users upload a zip archive of their project's codebase. The platform automatically scans the project, detects all open-source packages and sub-dependencies, creates a standardized <b>Software Bill of Materials (SBOM)</b>, checks public security databases for known zero-day vulnerabilities (CVEs and GHSAs), flags typosquatting or dangerous build scripts, and outputs an executive risk score alongside remediation steps.",
        body_style
    ))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Key Definitions & Core Concepts:</b>", body_style))
    story.append(Paragraph("• <b>Software Supply Chain:</b> The combined ecosystem of third-party modules, build scripts, package managers, and upstream code required to assemble software applications.", bullet_style))
    story.append(Paragraph("• <b>SBOM (Software Bill of Materials):</b> A formal, structured inventory of all software components, libraries, versions, and relationships that make up an application (analogous to an ingredient list on packaged food).", bullet_style))
    story.append(Paragraph("• <b>Transitive Dependencies:</b> Packages that are not directly installed by the developer, but are required by third-party packages installed in the project (forming a deep dependency tree).", bullet_style))
    story.append(Paragraph("• <b>Typosquatting Attack:</b> Malicious packages published with names intentionally similar to popular packages (e.g., <code>expreass</code> instead of <code>express</code>) to trick developers into installing malware.", bullet_style))
    story.append(Paragraph("• <b>Lifecycle Script Risk:</b> Arbitrary code executed automatically during package installation (e.g., <code>preinstall</code> or <code>postinstall</code> hooks in npm) used by attackers to execute remote shell commands.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>1.2 Technical Deep Dive (Architecture & Engine Capabilities)</b>", h2_style))
    story.append(Paragraph(
        "Architecturally, the application is structured into a decoupled, high-performance web system consisting of a <b>React 18 SPA Frontend</b> and a <b>FastAPI Asynchronous Backend</b> with an integrated static analysis and security engine.",
        body_style
    ))
    story.append(Paragraph(
        "The platform addresses the limitations of manual dependency auditing through automated multi-ecosystem static analysis:",
        body_style
    ))
    story.append(Paragraph("1. <b>Multi-Ecosystem Static Parsing:</b> Parses npm (<code>package.json</code>, <code>package-lock.json</code>, <code>yarn.lock</code>, <code>pnpm-lock.yaml</code>), PyPI (<code>requirements.txt</code>, <code>pyproject.toml</code>, <code>setup.py</code>, <code>Pipfile.lock</code>), and Maven/Gradle (<code>pom.xml</code>, <code>build.gradle</code>) without requiring full application execution.", bullet_style))
    story.append(Paragraph("2. <b>Asynchronous Batch Vulnerability Lookup:</b> Integrates with Google OSV.dev REST API via batch queries (sending up to 100 packages per HTTP POST) to minimize network latency and query CVE/GHSA vulnerability feeds.", bullet_style))
    story.append(Paragraph("3. <b>Heuristic Supply Chain Threat Detection:</b> Performs string distance calculations (Levenshtein distance) against a curated database of 1000+ top open-source libraries to flag typosquatting risks, and inspects package manifests for pre/post-install lifecycle scripts.", bullet_style))
    story.append(Paragraph("4. <b>Dynamic Weighted Risk Engine:</b> Calculates a normalized 0-100 overall project Risk Score using configurable weights for critical vulnerabilities, unpinned package versions, unknown/restrictive open-source licenses, and transitive risks.", bullet_style))
    story.append(Paragraph("5. <b>Standards-Compliant SBOM Exporter:</b> Generates downloadable JSON SBOMs compliant with international standards <b>CycloneDX v1.5</b> and <b>SPDX v2.3</b>.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 3. COMPLETE PROJECT WORKFLOW
    # =========================================================================
    story.append(Paragraph("2. Complete Project Workflow & Execution Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    story.append(Paragraph("<b>2.1 End-to-End System Workflow Execution Diagram</b>", h2_style))
    story.append(Paragraph("The diagram below illustrates the exact sequence of data flow and component interactions from user upload to dashboard rendering:", body_style))

    # Draw Architecture Diagram using ReportLab Graphics
    dwg = Drawing(504, 180)
    
    # Background Canvas Box
    dwg.add(Rect(0, 0, 504, 180, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=1, rx=6, ry=6))
    
    # Row 1 Nodes
    # Node 1: User / Frontend
    dwg.add(Rect(15, 120, 105, 45, fillColor=colors.HexColor("#EFF6FF"), strokeColor=colors.HexColor("#2563EB"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(67.5, 148, "React Frontend", textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#1E3A8A")))
    dwg.add(String(67.5, 132, "Upload ZIP / Dashboard", textAnchor="middle", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#3B82F6")))

    # Arrow 1 -> 2
    dwg.add(Line(120, 142.5, 145, 142.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    dwg.add(String(132.5, 147, "POST /upload", textAnchor="middle", fontName="Courier-Bold", fontSize=7, fillColor=colors.HexColor("#475569")))

    # Node 2: FastAPI Router
    dwg.add(Rect(145, 120, 105, 45, fillColor=colors.HexColor("#F0FDF4"), strokeColor=colors.HexColor("#16A34A"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(197.5, 148, "FastAPI Endpoints", textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#14532D")))
    dwg.add(String(197.5, 132, "projects.py / scans.py", textAnchor="middle", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#22C55E")))

    # Arrow 2 -> 3
    dwg.add(Line(250, 142.5, 275, 142.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    dwg.add(String(262.5, 147, "Background", textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#475569")))

    # Node 3: Project Scanner
    dwg.add(Rect(275, 120, 105, 45, fillColor=colors.HexColor("#FEF2F2"), strokeColor=colors.HexColor("#DC2626"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(327.5, 148, "ProjectScanner", textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#7F1D1D")))
    dwg.add(String(327.5, 132, "project_scanner.py", textAnchor="middle", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor("#EF4444")))

    # Arrow 3 -> 4
    dwg.add(Line(380, 142.5, 405, 142.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))

    # Node 4: Manifest & Parsers
    dwg.add(Rect(405, 120, 84, 45, fillColor=colors.HexColor("#FAF5FF"), strokeColor=colors.HexColor("#9333EA"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(447, 148, "Ecosystem Parsers", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#581C87")))
    dwg.add(String(447, 132, "NPM / PyPI / Maven", textAnchor="middle", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#A855F7")))

    # Down Arrow from Node 4 to Node 5
    dwg.add(Line(447, 120, 447, 75, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))

    # Row 2 Nodes
    # Node 5: OSV & Risk Engine
    dwg.add(Rect(395, 30, 94, 45, fillColor=colors.HexColor("#FFF7ED"), strokeColor=colors.HexColor("#EA580C"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(442, 58, "Vulnerability & Risk", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#7C2D12")))
    dwg.add(String(442, 42, "OSV Client & Risk Engine", textAnchor="middle", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#F97316")))

    # Arrow 5 -> 6
    dwg.add(Line(395, 52.5, 365, 52.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))

    # Node 6: SBOM Generator
    dwg.add(Rect(260, 30, 105, 45, fillColor=colors.HexColor("#F0FDF4"), strokeColor=colors.HexColor("#16A34A"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(312.5, 58, "SBOM Generator", textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#14532D")))
    dwg.add(String(312.5, 42, "CycloneDX / SPDX JSON", textAnchor="middle", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#22C55E")))

    # Arrow 6 -> 7
    dwg.add(Line(260, 52.5, 230, 52.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))

    # Node 7: SQLite Database
    dwg.add(Rect(125, 30, 105, 45, fillColor=colors.HexColor("#FEF3C7"), strokeColor=colors.HexColor("#D97706"), strokeWidth=1.5, rx=4, ry=4))
    dwg.add(String(177.5, 58, "SQLite Database", textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#78350F")))
    dwg.add(String(177.5, 42, "SQLAlchemy Models", textAnchor="middle", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#F59E0B")))

    # Arrow 7 -> 1 (Return)
    dwg.add(Line(125, 52.5, 67.5, 52.5, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    dwg.add(Line(67.5, 52.5, 67.5, 120, strokeColor=colors.HexColor("#64748B"), strokeWidth=1.5))
    dwg.add(String(96, 60, "REST Data", textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor("#475569")))

    story.append(dwg)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.2 Detailed Step-by-Step Workflow Pipeline Specification</b>", h2_style))

    workflow_steps = [
        ("Step 1: Project Upload", "frontend/src/pages/ProjectDetail.tsx", "handleFileUpload()", "ZIP file selected by user", "Sends FormData POST request to /api/projects/{id}/upload via api.ts Axios client.", "Scan object with 'pending' status"),
        ("Step 2: File Security & Extraction", "backend/app/api/projects.py", "upload_and_scan()", "Multipart UploadFile (.zip)", "Validates zip size (<50MB), path traversal attack check, safe temp extraction.", "Extracted project directory in ./temp_scans/"),
        ("Step 3: Background Scan Task", "backend/app/api/projects.py", "run_scan_task()", "scan_id, zip_path", "Launches FastAPI BackgroundTask executing project_scanner.scan_project().", "Scan status updated to 'running' in DB"),
        ("Step 4: Ecosystem & Manifest Detection", "backend/app/services/manifest_detector.py", "ManifestDetector.detect()", "Extracted root directory", "Walks directory tree, ignores node_modules/.venv, locates package.json, requirements.txt, pom.xml.", "List of detected manifest & lockfile paths"),
        ("Step 5: Dependency Parsing & Tree Building", "backend/app/services/dependency_analyzer.py", "DependencyAnalyzer.analyze()", "Manifest file paths", "Invokes NPMParser, PythonParser, or MavenParser. Resolves direct vs transitive packages.", "List of Dependency objects with versions and purls"),
        ("Step 6: OSV Vulnerability Querying", "backend/app/services/vulnerability_scanner.py", "scan_dependencies()", "Dependencies list", "Calls OSVClient.query_batch() with chunked payload (100 pkgs/batch) to hit https://api.osv.dev/v1.", "List of Vulnerability models (CVE/GHSA/CVSS)"),
        ("Step 7: Registry Version Audit", "backend/app/services/version_checker.py", "VersionChecker.get_version_info()", "Package name & version", "Fetches npmjs.org / PyPI API / Maven Central to check outdated status and patched versions.", "Latest & recommended package versions"),
        ("Step 8: Supply Chain Threat Analysis", "backend/app/services/supply_chain_analyzer.py", "SupplyChainAnalyzer.analyze()", "Extracted files & deps", "Runs TyposquattingDetector (Levenshtein check), LifecycleScriptAnalyzer (preinstall hooks), LicenseAnalyzer.", "List of RiskFinding models"),
        ("Step 9: Dynamic Risk Engine Scoring", "backend/app/services/risk_engine.py", "RiskEngine.calculate_risk_score()", "Vulns & RiskFindings", "Computes weighted risk score (0-100) and assigns risk level (CRITICAL, HIGH, MEDIUM, LOW).", "Normalized score & risk breakdown map"),
        ("Step 10: SBOM Document Generation", "backend/app/services/sbom_generator.py", "SBOMGenerator.generate()", "Scan, Deps, Vulns", "Formats standard CycloneDX v1.5 and SPDX v2.3 JSON documents.", "Serialized SBOM JSON string saved in DB"),
        ("Step 11: Database Persistence", "backend/app/services/project_scanner.py", "ProjectScanner.scan_project()", "All analysis results", "Commits dependencies, vulnerabilities, risk findings, and SBOMs to SQLite via SQLAlchemy.", "Scan status updated to 'completed'"),
        ("Step 12: React Dashboard Update", "frontend/src/hooks/useApi.ts", "useProjects(), useLatestScan()", "REST API response", "Axios fetches completed scan metrics; React components render tables, SVG trees, and charts.", "Updated Dashboard UI")
    ]

    wf_data = [[
        Paragraph("Step & File", tbl_header_style),
        Paragraph("Function / Handler", tbl_header_style),
        Paragraph("Input / Processing", tbl_header_style),
        Paragraph("Output Product", tbl_header_style)
    ]]

    for step, file_path, func, inp, proc, out in workflow_steps:
        wf_data.append([
            Paragraph(f"<b>{step}</b><br/><font color='#2563EB'>{file_path}</font>", tbl_cell_style),
            Paragraph(f"<code>{func}</code>", tbl_cell_code),
            Paragraph(f"<b>In:</b> {inp}<br/><b>Process:</b> {proc}", tbl_cell_style),
            Paragraph(f"<b>Out:</b> {out}", tbl_cell_style)
        ])

    wf_table = Table(wf_data, colWidths=[110, 110, 184, 100])
    wf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))

    story.append(wf_table)
    story.append(PageBreak())

    # =========================================================================
    # 4. COMPLETE FOLDER STRUCTURE
    # =========================================================================
    story.append(Paragraph("3. Complete Verified Folder & Module Directory Structure", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    story.append(Paragraph("The directory tree below reflects the exact, verified file organization of the repository:", body_style))

    folder_tree = """sbom/
├── README.md                          # Main project readme & execution guide
├── ARCHITECTURE.md                    # Architecture design document
├── RISK_SCORING.md                    # Risk Engine scoring mathematical model
├── SBOM.md                            # CycloneDX & SPDX spec overview
├── SECURITY.md                        # Security model & threat boundary
├── access.txt                         # Server manual startup instructions
├── backend/                           # FastAPI Python Backend Application
│   ├── run_server.ps1                 # Server startup script
│   ├── start_and_test.ps1             # Health test execution script
│   ├── test_scan.py                   # End-to-end integration test script
│   ├── test_server.py                 # Backend health test script
│   ├── requirements.txt               # Python package dependencies
│   ├── sbom_auditor_v2.db             # SQLite Production Database File
│   └── app/                           # Core FastAPI Application Module
│       ├── main.py                    # Application factory, middleware & router registration
│       ├── config.py                  # Pydantic BaseSettings environment configuration
│       ├── api/                       # REST API Route Handlers
│       │   ├── health.py              # Health check endpoints
│       │   ├── projects.py            # Project CRUD & ZIP upload scan trigger
│       │   ├── scans.py               # Scan metrics & dependency list endpoints
│       │   ├── scans_2.py             # Dependency tree, risk breakdown, vulns & comparison
│       │   ├── dependencies.py        # Dependency status table endpoints
│       │   ├── vulnerabilities.py    # Vulnerability statistics & lookup endpoints
│       │   ├── sbom.py                # CycloneDX/SPDX export & explorer endpoints
│       │   └── reports.py             # Compliance reports & summary JSON endpoints
│       ├── services/                  # Business Logic & Security Engines
│       │   ├── project_scanner.py     # End-to-end scanner orchestrator
│       │   ├── manifest_detector.py   # Manifest finder (package.json, requirements.txt, pom.xml)
│       │   ├── dependency_analyzer.py # Multi-ecosystem analysis coordinator
│       │   ├── npm_parser.py          # Node.js npm/yarn/pnpm parser
│       │   ├── python_parser.py       # Python requirements/pyproject parser
│       │   ├── maven_parser.py        # Java pom.xml/gradle parser
│       │   ├── osv_client.py          # Google OSV.dev REST batch API client
│       │   ├── vulnerability_scanner.py # Vulnerability detection orchestrator
│       │   ├── version_checker.py     # Registry version comparison (npm/pypi/maven)
│       │   ├── license_analyzer.py    # SPDX license risk classifier
│       │   ├── typosquatting_detector.py # Levenshtein distance brandjacking detector
│       │   ├── lifecycle_script_analyzer.py # Malicious install script inspector
│       │   ├── supply_chain_analyzer.py # Integrated threat aggregator
│       │   ├── risk_engine.py         # 0-100 dynamic risk score calculator
│       │   └── sbom_generator.py      # CycloneDX v1.5 & SPDX v2.3 generator
│       ├── models/                    # SQLAlchemy Database ORM Models
│       │   ├── project.py             # Project & ProjectEcosystem tables
│       │   ├── scan.py                # Scan table
│       │   ├── dependency.py          # Dependency & DependencyRelationship tables
│       │   ├── vulnerability.py       # Vulnerability table
│       │   ├── risk_finding.py        # RiskFinding table
│       │   ├── sbom.py                # SBOM table
│       │   └── license.py             # LicenseInfo & KnownLicense tables
│       ├── schemas/                   # Pydantic Validation & Serializer Schemas
│       │   ├── project.py             # Project schemas
│       │   ├── scan.py                # Scan schemas
│       │   ├── dependency.py          # Dependency & tree node schemas
│       │   ├── vulnerability.py       # Vulnerability schemas
│       │   ├── risk.py                # Risk score & finding schemas
│       │   ├── sbom.py                # SBOM explorer & export schemas
│       │   └── report.py              # Summary report schemas
│       ├── database/                  # Database Core
│       │   └── database.py            # SQLAlchemy engine, SessionLocal & get_db
│       └── utils/                     # Security & Helper Utilities
│           ├── file_security.py       # Zip validation & traversal protection
│           ├── subprocess_security.py # Safe CLI execution helper
│           ├── logging.py             # Structlog JSON logging configuration
│           └── version_utils.py       # Semver comparison utilities
└── frontend/                          # React + TypeScript + Vite SPA
    ├── package.json                   # Node dependencies & Vite scripts
    ├── vite.config.ts                 # Vite server config & /api proxy to 8000
    ├── tsconfig.json                  # TypeScript compiler settings
    ├── tailwind.config.js             # Tailwind CSS design system tokens
    ├── index.html                     # HTML entry point
    └── src/                           # React Application Source
        ├── main.tsx                   # React root mount point
        ├── App.tsx                    # React Router DOM route switchboard
        ├── layouts/                   # Layout Wrappers
        │   └── MainLayout.tsx         # Navigation sidebar & header wrapper
        ├── pages/                     # Primary Screen Views
        │   ├── Dashboard.tsx          # Main security metrics & project cards
        │   ├── Projects.tsx           # Project management & search
        │   ├── ProjectDetail.tsx      # Single project scans & upload modal
        │   ├── Vulnerabilities.tsx    # Vulnerability list & severity filters
        │   ├── SBOMExplorer.tsx       # Interactive SBOM component search table
        │   ├── DependencyTree.tsx     # Visual SVG dependency relationship graph
        │   ├── Reports.tsx            # Compliance summary & export controls
        │   └── Settings.tsx           # System API timeouts & risk weights
        ├── hooks/                     # Custom React Hooks
        │   └── useApi.ts              # Stable useRef API data fetching hooks
        ├── services/                  # Network Services
        │   └── api.ts                 # Axios HTTP client class
        ├── types/                     # TypeScript Interface Definitions
        │   └── index.ts               # Core entity type definitions
        └── utils/                     # Formatting & Styling Helpers
            └── helpers.ts             # Relative time, badge colors & cn class merger
"""

    tree_rows = []
    tree_cell_style = ParagraphStyle(
        'TreeCell',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#F8FAFC')
    )
    for line in folder_tree.strip().split('\n'):
        formatted_line = line.replace(' ', '&nbsp;')
        tree_rows.append([Paragraph(formatted_line, tree_cell_style)])

    tree_table = Table(tree_rows, colWidths=[504])
    tree_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0, colors.HexColor("#0F172A")),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tree_table)
    story.append(PageBreak())

    # =========================================================================
    # 5. EVERY IMPORTANT FILE EXPLANATION
    # =========================================================================
    story.append(Paragraph("4. Comprehensive File-by-File Technical Reference", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    story.append(Paragraph("The tables below provide a complete specification of every source file in the system.", body_style))

    file_specs = [
        # Backend Core & API
        ("backend/app/main.py", "FastAPI application entry point, CORS middleware setup, lifespan initialization, router inclusion.", "app, lifespan, root()", "HTTP Requests", "JSON Responses / API Routes", "FastAPI, CORS, app.api", "Uvicorn ASGI Server"),
        ("backend/app/config.py", "Application environment settings management using Pydantic BaseSettings.", "Settings class", ".env file / Env vars", "Settings instance", "pydantic-settings", "All backend modules"),
        ("backend/app/database/database.py", "SQLAlchemy engine setup, session maker, DB initialization, and dependency generator.", "get_db(), init_db()", "database_url config", "SQLAlchemy Session", "SQLAlchemy, app.config", "API route handlers"),
        ("backend/app/api/projects.py", "Project CRUD REST endpoints and async ZIP file upload trigger.", "create_project, list_projects, upload_and_scan", "ProjectCreate JSON, UploadFile", "ProjectResponse, ScanResponse", "FastAPI, ProjectScanner", "Frontend Projects/Dashboard pages"),
        ("backend/app/api/scans.py", "Endpoints for fetching scan summaries and package dependency lists.", "get_scan, get_scan_dependencies", "scan_id, filter params", "ScanDetailResponse, DependencySummaryResponse", "SQLAlchemy, Scan model", "Frontend ProjectDetail page"),
        ("backend/app/api/scans_2.py", "Endpoints for visual dependency tree, scan vulnerability listing, and risk breakdown.", "get_dependency_tree, get_scan_risk", "scan_id", "DependencyTreeNode list, Risk dict", "DependencyRelationship model", "Frontend DependencyTree/Dashboard pages"),
        ("backend/app/api/dependencies.py", "Endpoints for single dependency detail and scan status overview tables.", "get_dependency, get_dependency_status", "dependency_id, scan_id", "DependencyDetailResponse", "Dependency model", "Frontend Dependency Status table"),
        ("backend/app/api/vulnerabilities.py", "Vulnerability detail lookup and scan-level vulnerability severity statistics.", "get_vulnerability, get_vulnerability_stats", "vulnerability_id, scan_id", "VulnerabilityStatsResponse", "Vulnerability model", "Frontend Vulnerabilities page"),
        ("backend/app/api/sbom.py", "CycloneDX/SPDX SBOM generation, download, and interactive explorer querying.", "get_sbom, download_sbom, explore_sbom", "scan_id, filter params", "SBOMResponse, File Blob", "SBOMGenerator", "Frontend SBOMExplorer page"),
        ("backend/app/api/reports.py", "Compliance summary reports and machine-readable JSON report exports.", "download_json_report, get_report_summary", "scan_id", "ReportSummary, JSON File Blob", "Scan/Risk models", "Frontend Reports page"),
        
        # Backend Services
        ("backend/app/services/project_scanner.py", "Main security audit orchestrator managing extraction, parsing, scanning, and persistence.", "ProjectScanner, scan_project()", "project_id, zip_path, scan_id", "Scan model (completed)", "All parsers, scanners, ORM", "backend/app/api/projects.py"),
        ("backend/app/services/manifest_detector.py", "Scans directory tree for package manifest and lockfile paths across ecosystems.", "ManifestDetector, detect()", "Project root folder path", "List of ManifestInfo dicts", "pathlib, os.walk", "DependencyAnalyzer"),
        ("backend/app/services/dependency_analyzer.py", "Coordinates ecosystem-specific parsing and builds total package lists and stats.", "DependencyAnalyzer, analyze()", "Project root folder path", "Analysis result dictionary", "NPMParser, PythonParser, MavenParser", "ProjectScanner"),
        ("backend/app/services/npm_parser.py", "Parses package.json, package-lock.json, yarn.lock, pnpm-lock.yaml for JS/TS projects.", "NPMParser, parse()", "package.json & lockfile paths", "List of dependency dicts", "json parsing, lockfile regex", "DependencyAnalyzer"),
        ("backend/app/services/python_parser.py", "Parses requirements.txt, pyproject.toml, setup.py, Pipfile.lock for Python projects.", "PythonParser, parse()", "python manifest file paths", "List of dependency dicts", "tomllib, regex, semver", "DependencyAnalyzer"),
        ("backend/app/services/maven_parser.py", "Parses pom.xml and build.gradle files for Java/Kotlin projects.", "MavenParser, parse()", "pom.xml & build.gradle paths", "List of dependency dicts", "xml.etree.ElementTree", "DependencyAnalyzer"),
        ("backend/app/services/osv_client.py", "Asynchronous HTTP client querying Google OSV.dev batch API with in-memory caching.", "OSVClient, query_batch()", "List of OSVQuery objects", "OSV batch query response", "httpx, asyncio, cache", "VulnerabilityScanner"),
        ("backend/app/services/vulnerability_scanner.py", "Orchestrates vulnerability detection for resolved dependencies against OSV.dev.", "VulnerabilityScanner, scan_dependencies()", "List of Dependency ORM models", "List of Vulnerability ORM models", "OSVClient", "ProjectScanner"),
        ("backend/app/services/version_checker.py", "Queries npm, PyPI, and Maven registries to identify outdated packages.", "VersionChecker, check_dependencies()", "List of dependencies", "Updated version fields", "httpx, packaging.version", "ProjectScanner"),
        ("backend/app/services/license_analyzer.py", "Classifies open-source licenses into SPDX types and flags unknown or viral licenses.", "LicenseAnalyzer, analyze()", "Package license strings", "LicenseInfo & risk ratings", "SPDX mapping rules", "ProjectScanner"),
        ("backend/app/services/typosquatting_detector.py", "Detects brandjacking attacks via Levenshtein distance checks against 1000+ top libraries.", "TyposquattingDetector, check()", "Dependency package name", "Typosquatting flag & distance", "Levenshtein calculation", "SupplyChainAnalyzer"),
        ("backend/app/services/lifecycle_script_analyzer.py", "Inspects package manifests for hazardous pre/post-install lifecycle scripts.", "LifecycleScriptAnalyzer, inspect()", "package.json content", "Script findings & risk severity", "json parsing", "SupplyChainAnalyzer"),
        ("backend/app/services/supply_chain_analyzer.py", "Aggregates typosquatting, lifecycle scripts, unpinned dependencies, and license findings.", "SupplyChainAnalyzer, analyze()", "Project root & dependencies", "List of RiskFinding models", "Typosquatting, Lifecycle, License", "ProjectScanner"),
        ("backend/app/services/risk_engine.py", "Calculates dynamic 0-100 overall project Risk Score using configurable weighted rules.", "RiskEngine, calculate_risk_score()", "Vulnerabilities & RiskFindings", "Risk score & risk level label", "app.config.settings", "ProjectScanner"),
        ("backend/app/services/sbom_generator.py", "Constructs standard CycloneDX v1.5 and SPDX v2.3 JSON documents.", "SBOMGenerator, generate()", "Scan, Dependencies, Vulns", "Structured SBOM JSON dict", "uuid, datetime", "ProjectScanner"),

        # Backend Models & Schemas
        ("backend/app/models/project.py", "SQLAlchemy ORM definitions for projects and project_ecosystems tables.", "Project, ProjectEcosystem", "DB records", "Python objects", "SQLAlchemy Base", "All API routes & services"),
        ("backend/app/models/scan.py", "SQLAlchemy ORM definition for scans table.", "Scan, ScanStatus", "DB records", "Python objects", "SQLAlchemy Base", "ProjectScanner & API"),
        ("backend/app/models/dependency.py", "SQLAlchemy ORM definitions for dependencies and dependency_relationships tables.", "Dependency, DependencyRelationship", "DB records", "Python objects", "SQLAlchemy Base", "Dependency services & API"),
        ("backend/app/models/vulnerability.py", "SQLAlchemy ORM definition for vulnerabilities table.", "Vulnerability, SeverityEnum", "DB records", "Python objects", "SQLAlchemy Base", "VulnerabilityScanner & API"),
        ("backend/app/models/risk_finding.py", "SQLAlchemy ORM definition for risk_findings table.", "RiskFinding, RiskFindingType", "DB records", "Python objects", "SQLAlchemy Base", "RiskEngine & API"),
        ("backend/app/models/sbom.py", "SQLAlchemy ORM definition for sboms table.", "SBOM", "DB records", "Python objects", "SQLAlchemy Base", "SBOMGenerator & API"),
        ("backend/app/schemas/*.py", "Pydantic v2 schemas for request validation and response serialization.", "ProjectCreate, ScanResponse, etc.", "JSON Payload", "Validated Pydantic object", "Pydantic v2 BaseModel", "FastAPI Route Handlers"),
        ("backend/app/utils/file_security.py", "Zip bomb protection, path traversal defenses, and safe extraction functions.", "validate_zip_file, safe_extract_zip", "Zip file path, extract directory", "Status boolean, file list", "zipfile, os, shutil", "backend/app/api/projects.py"),

        # Frontend Modules
        ("frontend/src/App.tsx", "React Router DOM route switchboard establishing layout routes.", "App()", "URL location", "React element tree", "react-router-dom, MainLayout", "frontend/src/main.tsx"),
        ("frontend/src/layouts/MainLayout.tsx", "Primary application layout wrapper containing sidebar navigation and header search.", "MainLayout()", "Child page outlet", "Rendered layout frame", "react-router-dom, lucide-react", "frontend/src/App.tsx"),
        ("frontend/src/pages/Dashboard.tsx", "Main security operations center displaying project cards, scan metrics, and risk charts.", "Dashboard()", "Projects & LatestScan hook data", "Dashboard UI view", "useProjects, useLatestScan", "frontend/src/App.tsx"),
        ("frontend/src/pages/Projects.tsx", "Project management page with search, creation modal, and deletion controls.", "Projects()", "useProjects hook data", "Projects management UI", "useProjects, api.createProject", "frontend/src/App.tsx"),
        ("frontend/src/pages/ProjectDetail.tsx", "Single project view with scan history table and new ZIP scan upload modal.", "ProjectDetail()", "projectId route param", "Project details UI view", "useProject, useScans, api", "frontend/src/App.tsx"),
        ("frontend/src/pages/Vulnerabilities.tsx", "Vulnerability repository browser with severity badge filters and search.", "VulnerabilitiesPage()", "useScanVulnerabilities data", "Vulnerability list UI", "useScanVulnerabilities", "frontend/src/App.tsx"),
        ("frontend/src/pages/SBOMExplorer.tsx", "Interactive component inventory table with ecosystem/license/type filters.", "SBOMExplorerPage()", "useSBOMExplorer data", "SBOM component table UI", "useSBOMExplorer", "frontend/src/App.tsx"),
        ("frontend/src/pages/DependencyTree.tsx", "Visual SVG dependency tree renderer with risk-colored connection paths.", "DependencyTreePage()", "useDependencyTree data", "Interactive SVG tree UI", "useDependencyTree", "frontend/src/App.tsx"),
        ("frontend/src/pages/Reports.tsx", "Compliance report overview, executive summary, and JSON download triggers.", "ReportsPage()", "useReportSummary data", "Report summary view UI", "useReportSummary, api", "frontend/src/App.tsx"),
        ("frontend/src/pages/Settings.tsx", "Configuration settings page for OSV timeouts, batch sizes, and risk scoring weights.", "SettingsPage()", "Local state & config", "Settings UI form", "lucide-react", "frontend/src/App.tsx"),
        ("frontend/src/services/api.ts", "Axios HTTP client class wrapping REST calls to /api backend.", "ApiService class, api instance", "Method call & payload", "Promise of typed data", "axios, frontend/src/types", "React custom hooks & pages"),
        ("frontend/src/hooks/useApi.ts", "Custom data-fetching hook with useRef stabilization to eliminate render loops.", "useApi(), useProjects(), etc.", "API call function & deps", "data, loading, error, refetch", "React useRef, useCallback", "All frontend pages"),
        ("frontend/src/utils/helpers.ts", "Utility helpers for formatting relative dates, CSS badge classes, and risk colors.", "formatRelativeTime, cn, etc.", "Raw strings/dates/scores", "Formatted strings & CSS classes", "clsx, tailwind-merge", "All frontend components")
    ]

    f_data = [[
        Paragraph("File Path", tbl_header_style),
        Paragraph("Primary Purpose", tbl_header_style),
        Paragraph("Key Functions / Classes", tbl_header_style),
        Paragraph("Dependencies / Used By", tbl_header_style)
    ]]

    for fpath, purpose, funcs, inp, out, deps, used_by in file_specs:
        f_data.append([
            Paragraph(f"<b><font color='#1E3A8A'>{fpath}</font></b>", tbl_cell_style),
            Paragraph(purpose, tbl_cell_style),
            Paragraph(f"<code>{funcs}</code>", tbl_cell_code),
            Paragraph(f"<b>Deps:</b> {deps}<br/><b>Used by:</b> {used_by}", tbl_cell_style)
        ])

    f_table = Table(f_data, colWidths=[120, 144, 120, 120])
    f_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))

    story.append(f_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("5. Security, Risk Engine & Compliance Specifications", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

    story.append(Paragraph("<b>5.1 Risk Engine Mathematical Model</b>", h2_style))
    story.append(Paragraph(
        "The project features a proprietary dynamic risk scoring engine (<code>app/services/risk_engine.py</code>). "
        "The engine computes a normalized overall Risk Score on a scale from 0.0 (Safe) to 100.0 (Critical Threat) using weighted penalty points:",
        body_style
    ))

    risk_model_data = [
        [Paragraph("Finding / Risk Category", tbl_header_style), Paragraph("Weight Penalty", tbl_header_style), Paragraph("Description & Impact Rule", tbl_header_style)],
        [Paragraph("Critical Vulnerability", tbl_cell_style), Paragraph("25.0 points / vuln", tbl_cell_code), Paragraph("Extremely severe vulnerability (CVSS >= 9.0 or Critical severity flag).", tbl_cell_style)],
        [Paragraph("High Vulnerability", tbl_cell_style), Paragraph("15.0 points / vuln", tbl_cell_code), Paragraph("High severity vulnerability (CVSS 7.0 - 8.9).", tbl_cell_style)],
        [Paragraph("Medium Vulnerability", tbl_cell_style), Paragraph("8.0 points / vuln", tbl_cell_code), Paragraph("Medium severity vulnerability (CVSS 4.0 - 6.9).", tbl_cell_style)],
        [Paragraph("Low Vulnerability", tbl_cell_style), Paragraph("3.0 points / vuln", tbl_cell_code), Paragraph("Low severity vulnerability (CVSS 0.1 - 3.9).", tbl_cell_style)],
        [Paragraph("Typosquatting Risk", tbl_cell_style), Paragraph("10.0 points / finding", tbl_cell_code), Paragraph("Package name Levenshtein distance <= 2 from top 1000 open source packages.", tbl_cell_style)],
        [Paragraph("Lifecycle Script Risk", tbl_cell_style), Paragraph("5.0 points / script", tbl_cell_code), Paragraph("Presence of preinstall / postinstall build scripts in package manifest.", tbl_cell_style)],
        [Paragraph("Transitive Vulnerability", tbl_cell_style), Paragraph("5.0 points / vuln", tbl_cell_code), Paragraph("Vulnerability residing deep in indirect dependency tree.", tbl_cell_style)],
        [Paragraph("Unpinned Dependency", tbl_cell_style), Paragraph("4.0 points / dep", tbl_cell_code), Paragraph("Wildcard or unpinned version range (e.g. <code>*</code> or <code>>=1.0.0</code>).", tbl_cell_style)],
        [Paragraph("Unknown / Restricted License", tbl_cell_style), Paragraph("3.0 points / dep", tbl_cell_code), Paragraph("Unrecognized license or restrictive copyleft license (GPL/AGPL).", tbl_cell_style)],
        [Paragraph("Outdated Dependency", tbl_cell_style), Paragraph("2.0 points / dep", tbl_cell_code), Paragraph("Installed version is behind current registry latest release.", tbl_cell_style)],
    ]

    rm_table = Table(risk_model_data, colWidths=[140, 110, 254])
    rm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(rm_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Normalized Risk Level Thresholds:</b>", body_style))
    story.append(Paragraph("• <b>CRITICAL:</b> Score >= 75.0 (Requires immediate build halt & patch deployment)", bullet_style))
    story.append(Paragraph("• <b>HIGH:</b> Score 50.0 - 74.9 (High-priority security updates needed)", bullet_style))
    story.append(Paragraph("• <b>MEDIUM:</b> Score 25.0 - 49.9 (Moderate risk; schedule updates)", bullet_style))
    story.append(Paragraph("• <b>LOW:</b> Score 0.0 - 24.9 (Safe build posture; routine maintenance)", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF report at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_pdf()
