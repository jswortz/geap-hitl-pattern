/**
 * Frontend Callback Dispatch & Live Workflow Graph Interaction Handler (PRD Section 7.2)
 * Strictly uses safe DOM manipulation (`textContent`, `createElement`) per security guidelines.
 */

function showToast(title, message, isError = false) {
    const banner = document.getElementById('toast-banner');
    const titleEl = document.getElementById('toast-title');
    const msgEl = document.getElementById('toast-message');
    const iconEl = document.getElementById('toast-icon');
    if (!banner || !titleEl || !msgEl) return;

    titleEl.textContent = title;
    msgEl.textContent = message;
    iconEl.textContent = isError ? '⚠️' : '✅';
    banner.classList.remove('hidden');
    setTimeout(() => {
        banner.classList.add('hidden');
    }, 5500);
}

function openTriggerModal() {
    const modal = document.getElementById('trigger-workflow-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeTriggerModal() {
    const modal = document.getElementById('trigger-workflow-modal');
    if (modal) modal.classList.add('hidden');
}

function toggleRevisionDrawer() {
    const drawer = document.getElementById('revision-drawer');
    const rejectDrawer = document.getElementById('reject-drawer');
    if (rejectDrawer) rejectDrawer.classList.add('hidden');
    if (drawer) drawer.classList.toggle('hidden');
}

function toggleRejectDrawer() {
    const drawer = document.getElementById('reject-drawer');
    const revDrawer = document.getElementById('revision-drawer');
    if (revDrawer) revDrawer.classList.add('hidden');
    if (drawer) drawer.classList.toggle('hidden');
}

function appendWorkflowLog(lineText) {
    const logContainer = document.getElementById('workflow-event-log');
    if (!logContainer) return;
    const row = document.createElement('div');
    row.className = 'text-emerald-300 font-semibold';
    const ts = new Date().toISOString().slice(11, 19);
    row.textContent = `[${ts} UTC] ${lineText}`;
    logContainer.prepend(row);
}

async function submitReviewDecision(initiativeId, decision) {
    let comments = 'Approved for Q4 Campaign Step 2 Creative Asset Generation.';
    if (decision === 'REVISION_REQUESTED') {
        const input = document.getElementById('revision-comments-input');
        const errEl = document.getElementById('revision-validation-error');
        comments = input ? input.value.trim() : '';
        if (comments.length < 10) {
            if (errEl) {
                errEl.textContent = 'Validation Error: Please enter at least 10 characters of actionable brand feedback.';
                errEl.classList.remove('hidden');
            }
            return;
        }
        if (errEl) errEl.classList.add('hidden');
    } else if (decision === 'REJECTED') {
        const input = document.getElementById('reject-comments-input');
        comments = input ? input.value.trim() : 'Rejected by Brand Director.';
    }

    showToast(
        'Dispatching Callback to Cloud Workflows...',
        `Sending ${decision} webhook signal for initiative ${initiativeId.slice(0, 8)}...`
    );

    try {
        const response = await fetch(`/api/initiatives/${initiativeId}/decision`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                decision: decision,
                reviewer: 'brand.director@enterprise.com',
                comments: comments
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            showToast('Review Submission Blocked', errData.detail || 'Error submitting decision', true);
            return;
        }

        const result = await response.json();
        showToast(
            'Cloud Workflows Resumed Successfully!',
            `Decision ${decision} committed to AlloyDB System of Record. Reloading updated state...`
        );

        setTimeout(() => {
            window.location.reload();
        }, 900);
    } catch (err) {
        showToast('Network Error', String(err), true);
    }
}

async function quickApproveFromGraph(initiativeId) {
    appendWorkflowLog(`CALLBACK_DISPATCH: Sending APPROVED webhook to Cloud Workflows for ${initiativeId.slice(0, 8)}...`);
    try {
        const response = await fetch(`/api/initiatives/${initiativeId}/decision`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                decision: 'APPROVED',
                reviewer: 'director@enterprise.com',
                comments: 'Approved asynchronously from Live Workflow Graph Monitor.'
            })
        });
        if (response.ok) {
            appendWorkflowLog(`WORKFLOW_RESUMED: Initiative ${initiativeId.slice(0, 8)} transitioned to APPROVED -> Step 2 Eventarc emitted!`);
            showToast('Workflow Callback Resumed!', `Initiative ${initiativeId.slice(0, 8)} transitioned from WAITING to APPROVED.`);
            setTimeout(() => window.location.reload(), 900);
        }
    } catch (e) {
        showToast('Error', String(e), true);
    }
}

async function runAsyncWorkflowGraphSimulation() {
    appendWorkflowLog('SIMULATION_START: Stepping asynchronous workflow graph transitions...');
    try {
        const listRes = await fetch('/api/initiatives');
        const data = await listRes.json();
        const pending = (data.initiatives || []).filter(i => i.status === 'PENDING_APPROVAL');
        if (pending.length > 0) {
            await quickApproveFromGraph(pending[0].id);
        } else {
            appendWorkflowLog('TRIGGER_NEW_EXECUTION: Launching new Cloud Workflow execution for brand_apex...');
            await fetch('/api/workflows/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    brand_id: 'brand_apex',
                    category: 'fabric_care',
                    search_query: 'cold water bio-enzymatic laundry sustainability trends 2026'
                })
            });
            setTimeout(() => window.location.reload(), 900);
        }
    } catch (e) {
        showToast('Error', String(e), true);
    }
}

async function handleTriggerWorkflow(event) {
    event.preventDefault();
    const brand = document.getElementById('trigger-brand').value;
    const category = document.getElementById('trigger-category').value;
    const query = document.getElementById('trigger-query').value;

    closeTriggerModal();
    showToast('Launching Cloud Workflow...', `Triggering trend_discovery_flow for ${brand} (${category})...`);

    try {
        const response = await fetch('/api/workflows/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                brand_id: brand,
                category: category,
                search_query: query
            })
        });
        const res = await response.json();
        showToast('Cloud Workflow Started!', `Execution ${res.execution_name || ''} is active.`);
        setTimeout(() => window.location.reload(), 1000);
    } catch (err) {
        showToast('Error Triggering Workflow', String(err), true);
    }
}
