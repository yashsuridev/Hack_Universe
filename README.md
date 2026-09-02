# Hack_Universe — Cyber SOC & Software Supply Chain Security Platform

A unified cybersecurity platform featuring **Software Supply Chain Security & SBOM Auditing**, **Autonomous AI Cyber SOC Detection & Response**, and an integrated **Network Scanner**.

---

## 🌟 Project Architecture

This repository contains the complete full-stack solution split into modular, high-performance services:

```text
Hack_Universe/
├── frontend/           # React + Vite + TypeScript + Tailwind CSS Dashboard
├── sbom-backend/       # FastAPI SBOM Auditor (CycloneDX / OSV Vulnerability Scanner)
├── soc-engine/         # Autonomous Cyber SOC Engine (ML Anomaly Detection & AI Playbooks)
└── network-scanner/    # Network Scanner Engine (Async Port & Service Discovery)
```

---

## 🚀 Quick Start Guide

### 1. Frontend Web Dashboard (`/frontend`)
The unified React dashboard connecting to all microservices.

```bash
cd frontend
npm install
npm run dev
```

### 2. SBOM Auditor Service (`/sbom-backend`)
FastAPI service performing automated dependency parsing, license checks, and vulnerability scanning via OSV database.

```bash
cd sbom-backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
* **Swagger API Docs**: `http://localhost:8000/docs`

### 3. Autonomous Cyber SOC Engine (`/soc-engine`)
Machine learning threat detection simulator and automated response playbook pipeline.

```bash
cd soc-engine
pip install -r requirements.txt  # (if applicable)
python part5_api.py
```
* **API / WebSocket Endpoint**: `http://localhost:8001`

### 4. Network Scanner API (`/network-scanner`)
Fast network discovery and service port scanner.

```bash
cd network-scanner
pip install -r requirements.txt
python scanner_api.py
```
* **API Endpoint**: `http://localhost:8002`

---

## 🛠️ Features

* **SBOM Generator & Auditor**: Parses `package.json`, `requirements.txt`, and `pom.xml` to build CycloneDX 1.6 SBOMs.
* **Vulnerability Scanning**: Real-time CVE detection via Google OSV API.
* **Autonomous SOC Response**: Real-time log streaming, anomaly detection, and automated containment actions.
* **Network Discovery**: Port scanner with service detection and OS fingerprinting.

---

## 🌐 Deployment

* **Frontend**: Deployable on **Vercel** or **Netlify** (Vite build settings included with `vercel.json`).
* **Backends**: Deployable on **Render**, **Railway**, or **Docker** VPS.
