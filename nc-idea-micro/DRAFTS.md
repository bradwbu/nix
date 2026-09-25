# NC IDEA MICRO Application Drafts — Aeroby

**Status:** DRAFT v1 — needs Brad's review + customer discovery details
**Deadline:** Monday, August 24, 2026 at 5:00 PM EST

---

## DESCRIPTION (500 chars max)

Aeroby is a Database Backup as a Service platform that protects SMBs from ransomware and data loss. We provide zero-trust air-gapped backups, cross-cloud portability across PostgreSQL, MySQL, MongoDB, and Redis, and automated daily restore verification — closing the gap between enterprise-grade data protection and what small engineering teams can realistically deploy and maintain.

---

## PROBLEM (1,500 chars max)

Small and mid-size businesses are disproportionately devastated by ransomware and database failures, yet lack practical tools to protect themselves. According to Verizon's 2025 Data Breach Investigations Report, 88% of SMB breaches involved ransomware — 2.3x the rate of large enterprises. When attacks hit, 84% of organizations that paid ransom still failed to fully recover their data (Halcyon Research), and average recovery costs reach $1.53M even excluding the ransom itself (Sophos 2025).

The core issue: existing backup solutions either serve enterprises (Veeam, Commvault — complex, expensive, require dedicated staff) or are dangerously simplistic (cron-scripted pg_dump piped to the same cloud account the attacker already compromised). Cloud-native snapshots from AWS or GCP lock customers into a single provider and store backups in the same blast radius as production data. Meanwhile, most SMBs with 1-15 engineers have no dedicated DBA or DevOps lead to build and maintain a proper backup pipeline.

The result is a protection gap: small teams know backups matter but lack the time, expertise, or tooling to implement air-gapped storage, cross-cloud redundancy, and restore verification. They discover their backups are corrupted or incomplete only after a disaster — when it's too late. As ransomware attacks grew 58% year-over-year in 2025, this gap is widening.

---

## SOLUTION (1,500 chars max)

Aeroby eliminates the SMB backup gap with a managed platform built on three pillars that no existing tool combines:

**1. Zero-Trust Air-Gapped Storage.** Backups are written to isolated WORM (Write-Once-Read-Many) storage completely outside the customer's cloud account. Even if an attacker gains full admin access to the customer's infrastructure, they cannot reach, modify, or delete Aeroby-managed backups. This directly addresses the #1 ransomware recovery failure: backups stored in the compromised environment.

**2. Cross-Cloud & Multi-Engine Portability.** One dashboard manages backups across PostgreSQL, MySQL, MongoDB, and Redis — whether hosted on AWS, GCP, DigitalOcean, Hetzner, or bare metal. Customers aren't locked to a single cloud provider's snapshot system. Migration and disaster recovery across environments becomes a one-click restore.

**3. Automated Restore Verification.** Every day, Aeroby spins up isolated containers, restores backups into them, runs integrity checks, and reports results. Customers get proof their backups actually work — not just a file-exists confirmation, but a verified recovery. No more discovering corruption after a disaster.

Setup takes under 10 minutes. A lightweight agent connects to the database, and Aeroby handles scheduling, encryption, transport, storage, verification, and alerting automatically.

---

## DEFENSIBILITY (1,500 chars max)

Aeroby's defensibility rests on technical architecture, data gravity, and market positioning:

**Technical moat:** Our air-gapped WORM storage architecture requires purpose-built infrastructure — isolated storage nodes, immutable write paths, and cryptographic chain-of-custody verification. This isn't a feature competitors can bolt onto existing products; it's a fundamental architectural decision that shapes the entire platform. We're building proprietary restore verification pipelines for each supported database engine (PostgreSQL, MySQL, MongoDB, Redis) that go beyond file-level checks to validate data integrity at the application layer.

**Data gravity & switching costs:** Once a customer's backup history lives on Aeroby — with verified restore points, retention policies, and compliance audit trails — switching becomes costly and risky. Backup is inherently sticky: nobody casually migrates their disaster recovery infrastructure.

**Market positioning:** Enterprise tools (Veeam, Commvault) are moving upmarket toward larger contracts. DIY scripts don't evolve. We're occupying the underserved middle: production-grade database backup for teams of 1-15 engineers, priced for SMB budgets ($19-$249/mo). No current competitor combines air-gapped storage, multi-engine support, cross-cloud portability, and automated restore verification at this price point.

---

## CUSTOMER DISCOVERY DETAIL (1,000 chars max)

⚠️ **[PLACEHOLDER — Brad needs to fill in after completing interviews]**

Describe one specific customer discovery conversation:
- Who did you talk to? (role, company size, industry)
- What was their current backup setup?
- What pain points did they describe?
- What surprised you about the conversation?
- How did it validate or change your assumptions?

**Tips for the interview:**
- Ask open-ended questions: "Walk me through what happens when your database goes down"
- Don't pitch Aeroby — listen for pain
- Ask about their worst data loss experience
- Ask what they're paying/spending (time + money) on current backup approach
- Get specific numbers: how often do they test restores? (Most will say never or rarely)

---

## ADDITIONAL DISCOVERY (1,000 chars max)

Beyond direct interviews, we've validated demand through multiple channels. Analysis of Reddit communities (r/selfhosted: 400K+ members, r/devops: 550K+, r/sysadmin: 900K+) reveals recurring threads about backup failures, untested restores, and ransomware anxiety — with no clear product recommendation emerging. Verizon's 2025 DBIR confirms SMBs face 2.3x the ransomware rate of enterprises. Sophos research shows average recovery costs of $1.53M, yet most SMBs spend under $100/mo on backup. We still need to learn: exact willingness to pay at each tier, whether teams prefer agent-based or agentless connection, and which database engine to prioritize first for launch (current hypothesis: PostgreSQL based on community size and SMB adoption).

---

## CUSTOMER DESCRIPTION (1,500 chars max)

Our primary early adopter is the technical co-founder or lead engineer at a bootstrapped SaaS company with 1-15 engineers and annual revenue between $100K-$5M. They run PostgreSQL or MySQL on cloud infrastructure (AWS, DigitalOcean, or Hetzner), handle their own DevOps without a dedicated DBA, and currently rely on cron-scripted database dumps or basic cloud snapshots they've never actually tested restoring. They know their backup situation is inadequate but haven't prioritized fixing it because existing solutions require enterprise-level complexity or budget.

Our secondary early adopter is the MSP or agency technical lead managing 10-50+ client environments. They need a single dashboard showing backup status across all clients, with automated alerting when something fails. Currently they cobble together per-client scripts with inconsistent monitoring.

The common thread: technically competent people who understand backup importance but lack time or tooling to implement production-grade protection. They'll pay $29-$99/mo to eliminate the risk and operational burden — a fraction of what one data loss incident would cost them.

Demographics skew toward 25-45 year-old technical professionals, primarily in the US, with concentration in startup hubs and tech-forward SMBs.

---

## CUSTOMER ACQUISITION (1,500 chars max)

Our go-to-market strategy focuses on organic developer trust before paid channels:

**Phase 1 (Months 1-4): Community-led growth.** Publish technical content on database backup best practices, ransomware recovery, and restore verification — targeting SEO keywords like "PostgreSQL backup best practices" and "ransomware-proof database backup." Distribute through dev-focused channels: Hacker News, Reddit (r/selfhosted, r/devops), Dev.to, and the PostgreSQL community Slack. Release an open-source restore verification tool to build credibility and capture top-of-funnel developers.

**Phase 2 (Months 3-6): Direct outreach + partnerships.** Engage MSP and agency communities through targeted outreach on MSP-focused forums and LinkedIn. Partner with hosting providers (DigitalOcean, Hetzner) for co-marketing — they benefit from customers having better backup practices on their platforms.

**Phase 3 (Months 5+): Product-led growth + paid.** Offer a free tier (1 database, 7-day retention) to drive self-service signups. Implement usage-based upgrade triggers: storage limits, additional databases, or advanced features like PITR and multi-region. Layer in targeted paid ads (Google search, LinkedIn) once organic channels establish baseline CAC and conversion rates.

Target CAC under $150 with LTV:CAC ratio above 3:1 within 12 months.

---

## REVENUE MODEL (1,000 chars max)

Aeroby uses tiered SaaS subscription pricing based on database count, storage volume, and feature access:

- **Starter ($19-$29/mo):** Up to 3 databases, 100 GB storage, daily snapshots, 7-day retention
- **Pro ($79-$99/mo):** Up to 10 databases, 500 GB, continuous WAL streaming (point-in-time recovery), 30-day retention, automated restore testing
- **Agency/Team ($249/mo+):** Unlimited databases, multi-region replication, custom retention, SSO, team permissions

Overage pricing: $0.03-$0.05/GB above tier limits.

Revenue scales with customer infrastructure growth — as they add databases and data volume, they naturally move to higher tiers. Gross margins target 70%+ (storage is our primary COGS). Expected average revenue per account: $65/mo at launch, growing to $110/mo as customers expand usage.

---

## MARKET OPPORTUNITY (1,000 chars max)

The data backup and recovery market reached $18.86B in 2026, growing at 14.5% CAGR (Business Research Company). The broader data backup solutions market is projected to hit $55.46B by 2030 at 12.7% CAGR. SMBs represent the fastest-growing and most underserved segment.

Aeroby's serviceable market: ~2.5M SMBs in the US running production databases on cloud or self-hosted infrastructure. At conservative 0.1% penetration and $65/mo average revenue, that's $1.95M ARR. Path to $2M+ within 5 years: capture 200+ paying customers by year 2, expand ARPA through usage growth and tier upgrades, add enterprise features (compliance, audit logs) to unlock mid-market. Target: $500K ARR by year 3, $2M+ ARR by year 5, positioning for NC IDEA SEED application by year 2.

---

## COMPETITION (1,500 chars max)

**Cloud-native snapshots (AWS Backup, RDS, GCP Cloud SQL):** Lock customers to one provider. Backups live in the same account as production — ransomware that compromises admin credentials deletes snapshots too. No cross-cloud portability. No restore verification.

**Enterprise platforms (Veeam, Commvault, Acronis):** Designed for large IT teams with dedicated backup administrators. Pricing starts at $1,000+/year, requires complex deployment, and is moving further upmarket. Overkill for a 5-person engineering team.

**DIY scripts (pg_dump, mysqldump + cron):** The default "solution" for most SMBs. No monitoring, no verification, no air-gapping. Scripts silently fail for months until a disaster reveals the gap. Zero cross-cloud portability.

**Simpler SaaS tools (SimpleBackups, Rewind.io):** Closer to our market but lack air-gapped storage, restore verification, and multi-engine support. Primarily focused on file/app backup rather than database-specific protection.

Aeroby's differentiation: we're the only platform combining air-gapped WORM storage, multi-engine database support (Postgres, MySQL, MongoDB, Redis), cross-cloud portability, and automated restore verification — priced for SMBs at $19-$249/mo. We're not competing with enterprise tools; we're serving the customers they ignore.

---

## MOMENTUM & TRACTION (1,500 chars max)

Aeroby is in active alpha development with the following progress over the past 6 months:

**Product development:**
- Core backup engine built for PostgreSQL, supporting full snapshots and incremental backups
- Air-gapped WORM storage architecture designed and prototyped
- Restore verification pipeline in development — automated container-based restore testing
- Web dashboard in early development for backup monitoring and management

**Market validation:**
- Extensive market research confirming SMB backup gap — synthesized data from Verizon DBIR, Sophos, IBM, and Halcyon reports
- Community research across Reddit (r/selfhosted, r/devops, r/sysadmin) validating pain points and willingness to pay
- Customer discovery interviews in progress with target ICPs

**Founder commitment:**
- Full-time on Aeroby since mid-2026 — no side employment, 100% dedicated
- Self-funded to date with zero outside investment
- 10+ years of computer and network engineering experience directly relevant to infrastructure and security tooling

**Immediate roadmap:**
- Complete alpha for PostgreSQL backup + restore verification by Q4 2026
- Launch closed beta with 10-20 design partners by Q1 2027
- First paying customers by Q1-Q2 2027

---

## IMPACT (500 chars max)

The $10K + NC IDEA programming will accelerate Aeroby from alpha to beta launch 2-3 months faster than self-funding alone. The grant covers critical infrastructure costs (cloud hosting, WORM storage nodes) and the 8-week program provides structured customer discovery methodology. NC IDEA's network connects us to mentors and future SEED applicants. Greensboro gains a cybersecurity-adjacent startup contributing to NC's growing tech ecosystem.

---

## MILESTONES (1,000 chars max)

1. **Month 1:** Complete PostgreSQL backup engine with air-gapped WORM storage integration. Deploy to staging environment.
2. **Month 2:** Build automated restore verification pipeline. Launch closed beta with 10 design partners from customer discovery.
3. **Month 3:** Add MySQL engine support. Collect structured feedback from beta users. Iterate on UX and reliability.
4. **Month 4:** Implement web dashboard for backup monitoring, alerting, and one-click restore. Onboard 10 additional beta users (20 total).
5. **Month 5:** Add MongoDB support. Begin content marketing and community engagement for launch pipeline.
6. **Month 6:** Public launch with Starter and Pro tiers. Target: 5 paying customers and $500 MRR.
7. **Month 7:** Evaluate SEED application readiness. Target: 15 paying customers, $1,500 MRR.

---

## USE OF FUNDS (1,000 chars max)

- **Cloud infrastructure & WORM storage ($4,000):** Dedicated storage nodes for air-gapped backup architecture, compute for restore verification containers, and staging/production environments. This is our primary technical cost — the isolated infrastructure that makes Aeroby's security model work.
- **LLC & legal/compliance ($1,000):** Business formation costs, terms of service, privacy policy, and initial compliance review for handling customer database backups.
- **Development tools & services ($1,500):** CI/CD pipeline, monitoring, error tracking, SSL certificates, domain, and third-party API integrations.
- **Marketing & customer acquisition ($2,000):** Content creation, SEO tooling, community sponsorships, and targeted ads for beta launch.
- **Contingency & operations ($1,500):** Buffer for unexpected costs during the 7-month grant period.

---

## FOUNDER BACKGROUND (1,000 chars max)

Bradley brings 10+ years of hands-on computer and network engineering experience to Aeroby, spanning enterprise IT infrastructure, network administration, and help desk operations. This background provides deep understanding of the backup and disaster recovery challenges that SMBs face daily — he's personally witnessed organizations lose data to failed backups, ransomware attacks, and inadequate recovery processes.

As a full-time solo founder since mid-2026, Bradley is entirely dedicated to building Aeroby. His technical skillset covers the full stack required to build and operate a database backup platform: systems administration, network security, cloud infrastructure, and software development. Based in Guilford County, NC, he's committed to building Aeroby as an NC-headquartered company.

---

## ADVISORS (800 chars max)

⚠️ **[PLACEHOLDER — Brad, do you have any advisors, mentors, or people helping you with Aeroby? Even informal ones count — a friend in tech who gives you feedback, someone you bounce ideas off, etc. If not, that's fine — you can mention that you're seeking mentorship through the NC IDEA program itself.]**

---

## VIDEO SCRIPT NOTES (optional, 3 min max)

**If you want to record a video (highly recommended for software), here's a rough structure:**

1. **Intro (20 sec):** "I'm Bradley, founder of Aeroby. We're building database backup as a service for small engineering teams."
2. **Problem (40 sec):** Ransomware stats, SMB vulnerability, the backup gap
3. **Demo/Solution (60 sec):** Walk through the product — setup, dashboard, restore verification
4. **Market + Traction (30 sec):** Market size, customer discovery highlights
5. **Ask (20 sec):** What $10K + NC IDEA program means for Aeroby's trajectory
6. **Close (10 sec):** "Aeroby — backups that actually work."
