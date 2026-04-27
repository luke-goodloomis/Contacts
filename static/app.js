// ============================================================================
// CONTACT MANAGER - FRONTEND JAVASCRIPT
// ============================================================================

// State management
const state = {
    contacts: [],
    companies: [],
    currentContact: null,
    currentFilter: {
        search: '',
        company: '',
        sortBy: 'last_name'
    },
    page: 0,
    pageSize: 100
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('Contact Manager loading...');
    loadStats();
    loadCompanies();
    loadContacts();
});

// ============================================================================
// API CALLS
// ============================================================================

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`/api${endpoint}`, options);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

async function loadStats() {
    try {
        const stats = await apiCall('/stats');
        document.getElementById('stat-count').textContent = stats.total_contacts;
        document.getElementById('company-count').textContent = stats.companies;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadCompanies() {
    try {
        const result = await apiCall('/companies');
        state.companies = result.companies;
        populateCompanyFilter();
    } catch (error) {
        console.error('Failed to load companies:', error);
    }
}

async function loadContacts() {
    try {
        const params = new URLSearchParams({
            skip: state.page * state.pageSize,
            limit: state.pageSize,
            search: state.currentFilter.search,
            company: state.currentFilter.company,
            sort_by: state.currentFilter.sortBy
        });

        const result = await apiCall(`/contacts?${params}`);
        state.contacts = result.contacts;
        renderContactsList();
    } catch (error) {
        console.error('Failed to load contacts:', error);
        showToast('Failed to load contacts', 'error');
    }
}

async function loadContact(email) {
    try {
        const contact = await apiCall(`/contacts/${encodeURIComponent(email)}`);
        state.currentContact = contact;
        renderDetailsPanel(contact);
    } catch (error) {
        console.error('Failed to load contact:', error);
        showToast('Failed to load contact details', 'error');
    }
}

async function saveContact(email, data) {
    try {
        if (state.contacts.find(c => c.email === email)) {
            // Update existing
            await apiCall(`/contacts/${encodeURIComponent(email)}`, 'PUT', data);
            showToast(`Contact ${data.first_name} ${data.last_name} updated successfully`, 'success');
        } else {
            // Create new
            data.email = email;
            await apiCall('/contacts', 'POST', data);
            showToast(`Contact ${data.first_name} ${data.last_name} created successfully`, 'success');
        }
        closeModal();
        loadContacts();
        loadStats();
    } catch (error) {
        showToast('Failed to save contact', 'error');
    }
}

async function deleteContact(email) {
    try {
        if (!confirm('Are you sure you want to delete this contact?')) {
            return;
        }
        await apiCall(`/contacts/${encodeURIComponent(email)}`, 'DELETE');
        showToast('Contact deleted successfully', 'success');
        closeDetailsPanel();
        loadContacts();
        loadStats();
    } catch (error) {
        showToast('Failed to delete contact', 'error');
    }
}

// ============================================================================
// UI RENDERING
// ============================================================================

function renderContactsList() {
    const container = document.getElementById('contacts-list');

    if (state.contacts.length === 0) {
        container.innerHTML = '<div class="no-results">No contacts found. Try adjusting your filters.</div>';
        return;
    }

    container.innerHTML = state.contacts.map(contact => `
        <div class="contact-item ${state.currentContact?.email === contact.email ? 'active' : ''}" 
             onclick="selectContact('${contact.email}')">
            <div class="contact-info">
                <div class="contact-name">${contact.first_name} ${contact.last_name}</div>
                <div class="contact-email">${contact.email}</div>
                ${contact.company ? `<div class="contact-company">${contact.company}</div>` : ''}
            </div>
            <div class="contact-actions">
                <button class="btn-icon" title="Edit" onclick="event.stopPropagation(); editContact('${contact.email}')">✏️</button>
                <button class="btn-icon" title="Delete" onclick="event.stopPropagation(); deleteContact('${contact.email}')">🗑️</button>
            </div>
        </div>
    `).join('');
}

function renderDetailsPanel(contact) {
    const detailsPanel = document.getElementById('details-panel');
    const detailsName = document.getElementById('details-name');
    const detailsContent = document.getElementById('details-content');

    detailsName.textContent = `${contact.first_name} ${contact.last_name}`;

    detailsContent.innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Email</div>
            <div class="detail-value"><a href="mailto:${contact.email}">${contact.email}</a></div>
        </div>

        ${contact.company ? `
            <div class="detail-item">
                <div class="detail-label">Company</div>
                <div class="detail-value">${contact.company}</div>
            </div>
        ` : ''}

        ${contact.phone ? `
            <div class="detail-item">
                <div class="detail-label">Phone</div>
                <div class="detail-value"><a href="tel:${contact.phone}">${contact.phone}</a></div>
            </div>
        ` : ''}

        ${contact.mobile ? `
            <div class="detail-item">
                <div class="detail-label">Mobile/Cell</div>
                <div class="detail-value"><a href="tel:${contact.mobile}">${contact.mobile}</a></div>
            </div>
        ` : ''}

        ${contact.notes ? `
            <div class="detail-item">
                <div class="detail-label">Notes</div>
                <div class="detail-value">${contact.notes}</div>
            </div>
        ` : ''}

        ${contact.created_at ? `
            <div class="detail-item">
                <div class="detail-label">Created</div>
                <div class="detail-value">${new Date(contact.created_at).toLocaleDateString()}</div>
            </div>
        ` : ''}

        ${contact.updated_at ? `
            <div class="detail-item">
                <div class="detail-label">Updated</div>
                <div class="detail-value">${new Date(contact.updated_at).toLocaleDateString()}</div>
            </div>
        ` : ''}

        <div class="detail-actions">
            <button class="btn btn-primary" onclick="editContact('${contact.email}')">Edit</button>
            <button class="btn btn-danger" onclick="deleteContact('${contact.email}')">Delete</button>
        </div>
    `;

    detailsPanel.classList.remove('hidden');
}

function populateCompanyFilter() {
    const select = document.getElementById('company-filter');
    const options = state.companies.map(company => 
        `<option value="${company}">${company}</option>`
    ).join('');
    select.innerHTML = `<option value="">All Companies</option>${options}`;
}

// ============================================================================
// EVENT HANDLERS
// ============================================================================

function selectContact(email) {
    loadContact(email);
}

function handleSearch() {
    state.currentFilter.search = document.getElementById('search-input').value;
    state.page = 0;
    loadContacts();
}

function handleFilter() {
    state.currentFilter.company = document.getElementById('company-filter').value;
    state.page = 0;
    loadContacts();
}

function handleSort() {
    state.currentFilter.sortBy = document.getElementById('sort-select').value;
    state.page = 0;
    loadContacts();
}

function resetFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('company-filter').value = '';
    document.getElementById('sort-select').value = 'last_name';
    
    state.currentFilter = {
        search: '',
        company: '',
        sortBy: 'last_name'
    };
    state.page = 0;
    
    loadContacts();
}

function showNewContactForm() {
    document.getElementById('modal-title').textContent = 'New Contact';
    document.getElementById('form-email').value = '';
    document.getElementById('form-email').readOnly = false;
    document.getElementById('form-first-name').value = '';
    document.getElementById('form-last-name').value = '';
    document.getElementById('form-company').value = '';
    document.getElementById('form-phone').value = '';
    document.getElementById('form-mobile').value = '';
    document.getElementById('form-notes').value = '';
    document.getElementById('delete-btn').classList.add('hidden');
    
    document.getElementById('contact-modal').classList.remove('hidden');
}

function editContact(email) {
    const contact = state.contacts.find(c => c.email === email);
    if (!contact) return;

    document.getElementById('modal-title').textContent = `Edit Contact`;
    document.getElementById('form-email').value = contact.email;
    document.getElementById('form-email').readOnly = true;
    document.getElementById('form-first-name').value = contact.first_name;
    document.getElementById('form-last-name').value = contact.last_name;
    document.getElementById('form-company').value = contact.company || '';
    document.getElementById('form-phone').value = contact.phone || '';
    document.getElementById('form-mobile').value = contact.mobile || '';
    document.getElementById('form-notes').value = contact.notes || '';
    
    document.getElementById('delete-btn').classList.remove('hidden');
    document.getElementById('contact-modal').classList.remove('hidden');
}

function handleSaveContact(event) {
    event.preventDefault();

    const email = document.getElementById('form-email').value.trim();
    const data = {
        first_name: document.getElementById('form-first-name').value.trim(),
        last_name: document.getElementById('form-last-name').value.trim(),
        company: document.getElementById('form-company').value.trim(),
        phone: document.getElementById('form-phone').value.trim(),
        mobile: document.getElementById('form-mobile').value.trim(),
        notes: document.getElementById('form-notes').value.trim()
    };

    if (!email || !data.first_name || !data.last_name) {
        showToast('Email, first name, and last name are required', 'warning');
        return;
    }

    saveContact(email, data);
}

function handleDeleteContact() {
    const email = document.getElementById('form-email').value;
    deleteContact(email);
}

// ============================================================================
// MODAL MANAGEMENT
// ============================================================================

function closeModal() {
    document.getElementById('contact-modal').classList.add('hidden');
}

function closeDetailsPanel() {
    document.getElementById('details-panel').classList.add('hidden');
    state.currentContact = null;
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('contact-modal');
    if (e.target === modal) {
        closeModal();
    }
});

// ============================================================================
// NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    // Auto-hide after 4 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4000);
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + N: New contact
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        showNewContactForm();
    }
    
    // Escape: Close modal or details panel
    if (e.key === 'Escape') {
        closeModal();
        closeOCRModal();
        closeDetailsPanel();
    }
});

// ============================================================================
// OCR IMAGE PROCESSING
// ============================================================================

function showOCRModal() {
    const modal = document.getElementById('ocr-modal');
    modal.classList.remove('hidden');
    
    // Setup drag and drop
    const uploadArea = document.getElementById('ocr-upload-area');
    const fileInput = document.getElementById('ocr-file-input');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-dark)';
        uploadArea.style.background = 'rgba(59, 130, 246, 0.15)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--primary)';
        uploadArea.style.background = 'rgba(59, 130, 246, 0.05)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
        uploadArea.style.background = 'rgba(59, 130, 246, 0.05)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleOCRFileSelect(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleOCRFileSelect(e.target.files[0]);
        }
    });
}

function closeOCRModal() {
    const modal = document.getElementById('ocr-modal');
    modal.classList.add('hidden');
}

function resetOCRModal() {
    document.getElementById('ocr-upload-area').classList.remove('hidden');
    document.getElementById('ocr-preview').classList.add('hidden');
    document.getElementById('ocr-file-input').value = '';
}

function handleOCRFileSelect(file) {
    const uploadArea = document.getElementById('ocr-upload-area');
    const preview = document.getElementById('ocr-preview');
    const imagePreview = document.getElementById('ocr-image-preview');
    const spinner = document.getElementById('ocr-spinner');
    const results = document.getElementById('ocr-results');
    
    // Show preview
    uploadArea.classList.add('hidden');
    preview.classList.remove('hidden');
    spinner.classList.remove('hidden');
    results.classList.add('hidden');
    
    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // Send to API
    processImageWithOCR(file);
}

async function processImageWithOCR(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/ocr/process', {
            method: 'POST',
            body: formData
        });
        
        const spinner = document.getElementById('ocr-spinner');
        spinner.classList.add('hidden');
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'OCR processing failed');
        }
        
        const data = await response.json();
        displayOCRResults(data);
    } catch (error) {
        document.getElementById('ocr-spinner').classList.add('hidden');
        showToast(`OCR Error: ${error.message}`, 'error');
    }
}

function displayOCRResults(data) {
    const results = document.getElementById('ocr-results');
    
    document.getElementById('ocr-confidence').textContent = Math.round(data.confidence);
    document.getElementById('ocr-first-name').value = data.first_name || '';
    document.getElementById('ocr-last-name').value = data.last_name || '';
    document.getElementById('ocr-email').value = data.email || '';
    document.getElementById('ocr-phone').value = data.phone || '';
    document.getElementById('ocr-mobile').value = data.mobile || '';
    document.getElementById('ocr-company').value = data.company || '';
    document.getElementById('ocr-title').value = data.title || '';
    document.getElementById('ocr-extracted-text').textContent = data.extracted_text || '';
    
    results.classList.remove('hidden');
}

async function importOCRContact() {
    try {
        const email = document.getElementById('ocr-email').value.trim();
        const firstName = document.getElementById('ocr-first-name').value.trim();
        const lastName = document.getElementById('ocr-last-name').value.trim();
        
        if (!email || !firstName || !lastName) {
            showToast('Please provide at least Email, First Name, and Last Name', 'error');
            return;
        }
        
        const contact = {
            email: email,
            first_name: firstName,
            last_name: lastName,
            company: document.getElementById('ocr-company').value.trim(),
            phone: document.getElementById('ocr-phone').value.trim(),
            mobile: document.getElementById('ocr-mobile').value.trim(),
            notes: `Title: ${document.getElementById('ocr-title').value.trim()}`
        };
        
        const response = await apiCall('/api/contacts', 'POST', contact);
        
        showToast(`✓ Contact "${firstName} ${lastName}" imported successfully!`, 'success');
        closeOCRModal();
        loadContacts();
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// ============================================================================
// PASTE & PARSE CONTACT INGESTION
// ============================================================================

let currentParsedContact = null;
let currentMergeTarget = null;

async function handleParseContact() {
    try {
        console.log('[Parse] Button clicked');
        const pasteText = document.getElementById('paste-input').value.trim();
        console.log('[Parse] Text extracted:', pasteText.substring(0, 50) + '...');
        
        if (!pasteText) {
            console.log('[Parse] No text pasted');
            showToast('Please paste some contact text first', 'warning');
            return;
        }
        
        console.log('[Parse] Calling API...');
        // Call parse API (apiCall adds /api prefix)
        const result = await apiCall('/parse-contact', 'POST', { text: pasteText });
        console.log('[Parse] API Response:', result);
        
        if (!result.success) {
            console.log('[Parse] Parse failed');
            showToast('Failed to parse contact', 'error');
            return;
        }
        
        // Store for later use
        currentParsedContact = result.contact;
        console.log('[Parse] Stored contact:', currentParsedContact);
        
        // Display in modal
        console.log('[Parse] Displaying results...');
        displayParseResults(result);
        
    } catch (error) {
        console.error('[Parse] Error:', error);
        showToast(`Parse Error: ${error.message}`, 'error');
    }
}

function displayParseResults(result) {
    console.log('[Display] Showing parse results');
    // Show confidence
    document.getElementById('parse-confidence').textContent = Math.round(result.confidence);
    
    // Show parsed fields
    document.getElementById('parse-first-name').textContent = result.contact.first_name || '(not found)';
    document.getElementById('parse-last-name').textContent = result.contact.last_name || '(not found)';
    document.getElementById('parse-email').textContent = result.contact.email || '(not found)';
    document.getElementById('parse-phone').textContent = result.contact.phone || '(not found)';
    document.getElementById('parse-mobile').textContent = result.contact.mobile || '(not found)';
    document.getElementById('parse-company').textContent = result.contact.company || '(not found)';
    document.getElementById('parse-title').textContent = result.contact.title || '(not found)';
    document.getElementById('parse-raw-text').textContent = result.contact.raw_text || '';
    console.log('[Display] Fields populated');
    
    // Show/hide duplicates section
    const duplicatesSection = document.getElementById('duplicates-section');
    if (result.has_duplicates && result.duplicates.length > 0) {
        duplicatesSection.classList.remove('hidden');
        renderDuplicatesList(result.duplicates);
    } else {
        duplicatesSection.classList.add('hidden');
    }
    
    // Open modal
    console.log('[Display] Opening parse-modal');
    const modal = document.getElementById('parse-modal');
    if (!modal) {
        console.error('[Display] ERROR: parse-modal element not found!');
        return;
    }
    modal.classList.remove('hidden');
    console.log('[Display] Modal should now be visible');
}

function renderDuplicatesList(duplicates) {
    const list = document.getElementById('duplicates-list');
    
    list.innerHTML = duplicates.map((dup, idx) => `
        <div class="duplicate-item">
            <div class="duplicate-match-badge">
                ${dup.match_type === 'email_exact' ? '📧 Email Match' :
                  dup.match_type === 'phone_exact' ? '☎️ Phone Match' :
                  dup.match_type === 'mobile_exact' ? '📱 Mobile Match' :
                  dup.match_type === 'name_fuzzy' ? '👤 Name Similar' : 'Match'}
                (${Math.round(dup.match_score)}%)
            </div>
            <div class="duplicate-details">
                <div><strong>${dup.first_name} ${dup.last_name}</strong></div>
                <div class="duplicate-field">Email: ${dup.email}</div>
                ${dup.company ? `<div class="duplicate-field">Company: ${dup.company}</div>` : ''}
                ${dup.phone ? `<div class="duplicate-field">Phone: ${dup.phone}</div>` : ''}
                ${dup.mobile ? `<div class="duplicate-field">Mobile: ${dup.mobile}</div>` : ''}
            </div>
            <button class="btn btn-secondary" onclick="selectDuplicateForMerge('${dup.email}')">
                Select & Review
            </button>
        </div>
    `).join('');
}

function selectDuplicateForMerge(email) {
    currentMergeTarget = email;
    showMergeModal(email);
}

function showMergeModal(email) {
    const mergeFields = document.getElementById('merge-fields');
    
    // Create comparison for each field
    const fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'company', 'title'];
    
    let html = '<div class="field-comparison">';
    
    fields.forEach(field => {
        const newVal = currentParsedContact[field] || '';
        const label = field.replace(/_/g, ' ').toUpperCase();
        
        html += `
            <div class="comparison-row">
                <div class="comparison-label">${label}</div>
                <div class="comparison-input">
                    <input 
                        type="text" 
                        id="merge-${field}"
                        value="${newVal}"
                        class="comparison-field"
                    >
                    <small>New value: ${newVal || '(empty)'}</small>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    mergeFields.innerHTML = html;
    
    document.getElementById('merge-modal').classList.remove('hidden');
}

async function handleConfirmMerge() {
    try {
        if (!currentMergeTarget) {
            showToast('No merge target selected', 'error');
            return;
        }
        
        // Collect updated values from form
        const updates = {
            first_name: document.getElementById('merge-first_name').value.trim(),
            last_name: document.getElementById('merge-last_name').value.trim(),
            email: document.getElementById('merge-email').value.trim(),
            phone: document.getElementById('merge-phone').value.trim(),
            mobile: document.getElementById('merge-mobile').value.trim(),
            company: document.getElementById('merge-company').value.trim(),
            title: document.getElementById('merge-title').value.trim()
        };
        
        // Call merge API
        const result = await apiCall('/merge-contact', 'POST', {
            existing_email: currentMergeTarget,
            updates: updates,
            merge_strategy: 'selective'
        });
        
        showToast(`✓ Contact updated successfully! (${result.message})`, 'success');
        
        // Close modals and refresh
        closeMergeModal();
        closeParsModal();
        document.getElementById('paste-input').value = '';
        loadContacts();
        loadStats();
        
    } catch (error) {
        showToast(`Merge Error: ${error.message}`, 'error');
    }
}

async function handleCreateNewContact() {
    try {
        if (!currentParsedContact || !currentParsedContact.email) {
            showToast('Contact must have at least an email address', 'error');
            return;
        }
        
        const contact = {
            email: currentParsedContact.email,
            first_name: currentParsedContact.first_name || 'Unknown',
            last_name: currentParsedContact.last_name || 'Contact',
            company: currentParsedContact.company || '',
            phone: currentParsedContact.phone || '',
            mobile: currentParsedContact.mobile || '',
            notes: currentParsedContact.title ? `Title: ${currentParsedContact.title}` : ''
        };
        
        // Validate required fields
        if (!contact.email || !contact.first_name || !contact.last_name) {
            showToast('Email, First Name, and Last Name are required', 'error');
            return;
        }
        
        // Save contact
        await apiCall('/contacts', 'POST', contact);
        
        showToast(`✓ Contact "${contact.first_name} ${contact.last_name}" created successfully!`, 'success');
        
        // Close modals and refresh
        closeParsModal();
        document.getElementById('paste-input').value = '';
        loadContacts();
        loadStats();
        
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

function closeParsModal() {
    document.getElementById('parse-modal').classList.add('hidden');
    currentParsedContact = null;
}

function closeMergeModal() {
    document.getElementById('merge-modal').classList.add('hidden');
    currentMergeTarget = null;
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    const parseModal = document.getElementById('parse-modal');
    const mergeModal = document.getElementById('merge-modal');
    
    if (e.target === parseModal) {
        closeParsModal();
    }
    
    if (e.target === mergeModal) {
        closeMergeModal();
    }
});

console.log('Contact Manager initialized');
