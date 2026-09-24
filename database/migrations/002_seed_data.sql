-- Seed data for Brand Building HITL Approval Example Application Demo (brand_apex, brand_aurora, brand_lumina)
INSERT INTO initiative_assets (id, brand_id, category, trend_name, status, version, revision_count, brief_payload, created_at, updated_at)
VALUES
(
    'a1000000-0000-4000-8000-000000000001',
    'brand_apex',
    'fabric_care',
    'Cold-Water Bio-Enzymatic Energy Surge',
    'PENDING_APPROVAL',
    1,
    0,
    '{
        "initiative_id": "a1000000-0000-4000-8000-000000000001",
        "brand_id": "brand_apex",
        "category": "fabric_care",
        "trend_name": "Cold-Water Bio-Enzymatic Energy Surge",
        "trend_summary": "Rising residential utility costs in 2026 have accelerated consumer adoption of 60°F cold-water wash cycles by 42%, creating demand for bio-enzymatic formulations that activate without thermal energy while protecting synthetic athletic fibers.",
        "target_audience": "Eco-conscious suburban households and activewear enthusiasts seeking lower utility bills without sacrificing garment longevity.",
        "citations": [
            {
                "title": "US Department of Energy: Residential Cold-Water Laundry Efficiency Benchmark 2026",
                "url": "https://www.energy.gov/energysaver/laundry-energy-efficiency-2026",
                "snippet": "Heating water accounts for 90% of the energy used by washing machines; switching to cold water reduces household carbon footprint by 1,600 lbs CO2 annually.",
                "publication_date": "2026-08-12"
            },
            {
                "title": "Sustainable Textile Institute: Bio-Surfactant Activation Below 18°C",
                "url": "https://www.americancleaninginstitute.org/cold-water-wash-trends-2026",
                "snippet": "Next-generation protease and lipase enzyme blends deliver 99.2% sebum lift in 15°C municipal tap water.",
                "publication_date": "2026-09-03"
            }
        ],
        "memories_applied": [
            {
                "memory_id": "mem_01",
                "directive": "Preferred Tone: Optimistic, empowering, and scientific yet accessible.",
                "category": "tone"
            },
            {
                "memory_id": "mem_02",
                "directive": "Claim Guardrail: Cold-water wash saves up to 90% energy in wash cycle; never claim 100% stain elimination on silk.",
                "category": "legal"
            },
            {
                "memory_id": "mem_04",
                "directive": "Brand Motif: Visuals must emphasize crisp natural daylight and glacial water flow.",
                "category": "hook"
            }
        ],
        "creative_hooks": [
            {
                "headline": "Turn Down the Dial. Turn Up the Brilliance.",
                "narrative_angle": "Frame the cold-water dial switch as an effortless scientific upgrade that saves up to 90% wash-cycle energy while locking in fiber elasticity.",
                "key_claims": ["Saves up to 90% energy in wash cycle", "Sub-60°F bio-enzymatic activation", "Zero thermal fiber shrinkage"],
                "visual_direction": "Macro slow-motion shot of crisp natural daylight refracting through glacial water droplets lifting micro-soil from technical knit fibers."
            },
            {
                "headline": "Peak Performance at 60°F.",
                "narrative_angle": "Target technical activewear owners whose synthetic elastane breaks down in warm washes.",
                "key_claims": ["Preserves elastane recovery across 50+ washes", "Cold-water energy savings"],
                "visual_direction": "Split-frame microscopy showing intact cold-washed activewear fibers bathed in bright morning sunlight."
            },
            {
                "headline": "Smart Science for Conscious Homes.",
                "narrative_angle": "Empower families with measurable utility bill reductions backed by enzymatic cleaning science.",
                "key_claims": ["Saves up to 90% energy in wash cycle", "Dermatologist-verified clean rinse"],
                "visual_direction": "Sunlit modern laundry room with translucent aqua water streams and clean botanical linen textures."
            }
        ],
        "confidence_score": 0.94,
        "created_at": "2026-09-24T16:00:00Z"
    }'::jsonb,
    NOW() - INTERVAL '45 minutes',
    NOW() - INTERVAL '45 minutes'
),
(
    'b2000000-0000-4000-8000-000000000002',
    'brand_aurora',
    'baby_care',
    'Microbiome-Safe Newborn Barrier Protection',
    'PENDING_APPROVAL',
    2,
    1,
    '{
        "initiative_id": "b2000000-0000-4000-8000-000000000002",
        "brand_id": "brand_aurora",
        "category": "baby_care",
        "trend_name": "Microbiome-Safe Newborn Barrier Protection",
        "trend_summary": "Millennial and Gen-Z parents in 2026 prioritize pH-balanced, prebiotic diaper liners that support infant skin microbiome integrity and eliminate synthetic fragrances.",
        "target_audience": "First-time parents researching pediatrician-tested, hypoallergenic newborn skin care.",
        "citations": [
            {
                "title": "Pediatric Dermatology Review: Infant Skin Microbiome & pH 5.5 Liners (2026)",
                "url": "https://www.aap.org/infant-skin-barrier-microbiome-2026",
                "snippet": "Maintaining acid mantle pH between 5.0 and 5.5 reduces diaper irritation incidence by 64% in clinical observation.",
                "publication_date": "2026-07-28"
            }
        ],
        "memories_applied": [
            {
                "memory_id": "mem_aurora_01",
                "directive": "Emphasize pediatrician_tested and gentle_comfort; never use medical cure or miracle healing claims.",
                "category": "legal"
            },
            {
                "memory_id": "mem_sync_01",
                "directive": "Focus messaging on gentle prebiotic skin barrier nourishment rather than clinical fear hooks.",
                "category": "tone"
            }
        ],
        "creative_hooks": [
            {
                "headline": "Pediatrician-Tested Comfort for Delicate First Days.",
                "narrative_angle": "Reassure parents with gentle comfort and pH-balanced plant-derived liners.",
                "key_claims": ["Pediatrician-tested hypoallergenic liner", "100% fragrance-free gentle comfort"],
                "visual_direction": "Warm nursery morning light, ultra-soft organic cotton textures, calm parent-infant bonding."
            }
        ],
        "confidence_score": 0.91,
        "created_at": "2026-09-24T15:30:00Z"
    }'::jsonb,
    NOW() - INTERVAL '90 minutes',
    NOW() - INTERVAL '25 minutes'
),
(
    'c3000000-0000-4000-8000-000000000003',
    'brand_lumina',
    'home_care',
    'Waterless Dissolvable Bio-Refill Concentrates',
    'APPROVED',
    2,
    0,
    '{
        "initiative_id": "c3000000-0000-4000-8000-000000000003",
        "brand_id": "brand_lumina",
        "category": "home_care",
        "trend_name": "Waterless Dissolvable Bio-Refill Concentrates",
        "trend_summary": "Urban consumers are replacing single-use plastic spray bottles with effervescent plant-based tablet refills packaged in home-compostable cellulose sleeves.",
        "target_audience": "Zero-waste urban apartments and design-forward eco households.",
        "citations": [
            {
                "title": "EPA Safer Choice Packaging & Refill Innovation Report 2026",
                "url": "https://www.epa.gov/saferchoice/zero-plastic-home-care-refills-2026",
                "snippet": "Concentrated tablet refills cut shipping weight by 88% and eliminate single-use HDPE triggers.",
                "publication_date": "2026-08-05"
            }
        ],
        "memories_applied": [
            {
                "memory_id": "mem_lumina_01",
                "directive": "Require zero_plastic_packaging and biodegradable surfactant claims; prohibit bleach safe on wood claims.",
                "category": "legal"
            }
        ],
        "creative_hooks": [
            {
                "headline": "Just Add Tap Water. Zero Plastic Waste.",
                "narrative_angle": "Turn reusable glass spray bottles into high-performance botanical surface cleaners.",
                "key_claims": ["100% biodegradable plant surfactants", "Zero plastic packaging sleeve"],
                "visual_direction": "Minimalist architectural kitchen counter with amber glass bottle and effervescent botanical tablet."
            }
        ],
        "confidence_score": 0.96,
        "created_at": "2026-09-24T14:00:00Z"
    }'::jsonb,
    NOW() - INTERVAL '180 minutes',
    NOW() - INTERVAL '60 minutes'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO workflow_callbacks (id, initiative_id, workflow_execution_id, callback_url, status, created_at, updated_at)
VALUES
(
    'd4000000-0000-4000-8000-000000000001',
    'a1000000-0000-4000-8000-000000000001',
    'projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-apex-001',
    'https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-apex-001/callbacks/cb-apex-001',
    'WAITING',
    NOW() - INTERVAL '45 minutes',
    NOW() - INTERVAL '45 minutes'
),
(
    'd4000000-0000-4000-8000-000000000002',
    'b2000000-0000-4000-8000-000000000002',
    'projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-aurora-002',
    'https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-aurora-002/callbacks/cb-aurora-002',
    'WAITING',
    NOW() - INTERVAL '25 minutes',
    NOW() - INTERVAL '25 minutes'
),
(
    'd4000000-0000-4000-8000-000000000003',
    'c3000000-0000-4000-8000-000000000003',
    'projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-lumina-003',
    'https://workflowexecutions.googleapis.com/v1/projects/wortz-project-352116/locations/us-central1/workflows/trend_discovery_flow/executions/exec-lumina-003/callbacks/cb-lumina-003',
    'RECEIVED',
    NOW() - INTERVAL '180 minutes',
    NOW() - INTERVAL '60 minutes'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO initiative_reviews (id, initiative_id, reviewer_email, action, comments, created_at)
VALUES
(
    'e5000000-0000-4000-8000-000000000001',
    'b2000000-0000-4000-8000-000000000002',
    'brand.director@aurora-care.enterprise.com',
    'REVISION_REQUESTED',
    'First draft leaned too heavily on clinical dermatologist jargon. Revise to emphasize gentle prebiotic comfort and warm parenting reassurance.',
    NOW() - INTERVAL '50 minutes'
),
(
    'e5000000-0000-4000-8000-000000000002',
    'c3000000-0000-4000-8000-000000000003',
    'vp.sustainability@lumina-home.enterprise.com',
    'APPROVED',
    'Approved for Q4 Omni-Channel Retail & Digital Asset Pipeline (Step 2 Eventarc Handoff). Verified EPA Safer Choice citation.',
    NOW() - INTERVAL '60 minutes'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO memory_sync_events (id, initiative_id, brand_id, feedback_text, distilled_rule, memory_bank_record_id, synced_at)
VALUES
(
    'f6000000-0000-4000-8000-000000000001',
    'b2000000-0000-4000-8000-000000000002',
    'brand_aurora',
    'First draft leaned too heavily on clinical dermatologist jargon. Revise to emphasize gentle prebiotic comfort and warm parenting reassurance.',
    'Focus messaging on gentle prebiotic skin barrier nourishment and warm parental reassurance rather than clinical fear hooks.',
    'mem_sync_01',
    NOW() - INTERVAL '49 minutes'
)
ON CONFLICT (id) DO NOTHING;
