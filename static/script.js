// API Base URL
const API_URL = 'http://localhost:5000/api';

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.getAttribute('data-section');
        showSection(section);
        
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    });
});

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
        
        // Load section-specific data
        if (sectionId === 'dashboard') loadDashboard();
        if (sectionId === 'my-cases') loadCases();
        if (sectionId === 'legal-info') loadLegalInfo();
    }
}

// Dashboard
function loadDashboard() {
    fetch(`${API_URL}/statistics`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('total-cases').textContent = data.total_cases;
            document.getElementById('open-cases').textContent = data.open_cases;
            document.getElementById('closed-cases').textContent = data.closed_cases;
            document.getElementById('total-advice').textContent = data.total_advice;
            
            // Display categories chart
            const categoryChart = document.getElementById('category-chart');
            let chartHTML = '';
            for (const [category, count] of Object.entries(data.categories)) {
                const width = (count / Math.max(...Object.values(data.categories), 1)) * 100;
                chartHTML += `
                    <div style="margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>${category}</span>
                            <span>${count}</span>
                        </div>
                        <div style="background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea, #764ba2); width: ${width}%; height: 100%; transition: width 0.3s ease;"></div>
                        </div>
                    </div>
                `;
            }
            categoryChart.innerHTML = chartHTML || '<p>No data yet</p>';
        })
        .catch(err => console.error('Error loading dashboard:', err));
}

// New Case Form
const caseForm = document.getElementById('case-form');
const caseDescription = document.getElementById('case-description');

caseDescription.addEventListener('input', () => {
    const description = caseDescription.value;
    if (description.length > 10) {
        fetch(`${API_URL}/predict-category`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: description })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('predicted-category').textContent = `Category: ${data.category || 'Unknown'}`;
            document.getElementById('confidence-score').textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        })
        .catch(err => console.error('Error predicting category:', err));
    }
});

caseForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const title = document.getElementById('case-title').value;
    const description = document.getElementById('case-description').value;
    const priority = document.getElementById('case-priority').value;
    
    fetch(`${API_URL}/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, priority })
    })
    .then(res => res.json())
    .then(data => {
        alert('Case created successfully!');
        caseForm.reset();
        
        // Predict category and generate advice
        return fetch(`${API_URL}/predict-category`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: description })
        });
    })
    .then(res => res.json())
    .then(data => {
        const category = data.category;
        const caseId = data.id;
        
        // Generate advice
        return fetch(`${API_URL}/generate-advice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, case_id: caseId, description })
        });
    })
    .catch(err => console.error('Error creating case:', err));
});

// Load Cases
function loadCases() {
    fetch(`${API_URL}/cases`)
        .then(res => res.json())
        .then(cases => {
            const casesList = document.getElementById('cases-list');
            casesList.innerHTML = '';
            
            cases.forEach(caseItem => {
                const caseCard = document.createElement('div');
                caseCard.className = 'case-card';
                caseCard.innerHTML = `
                    <h3>${caseItem.title}</h3>
                    <p><strong>Category:</strong> ${caseItem.category || 'Uncategorized'}</p>
                    <p><strong>Priority:</strong> ${caseItem.priority}</p>
                    <p>${caseItem.description.substring(0, 100)}...</p>
                    <span class="case-status ${caseItem.status.toLowerCase()}">${caseItem.status}</span>
                `;
                
                caseCard.addEventListener('click', () => showCaseDetails(caseItem.id));
                casesList.appendChild(caseCard);
            });
            
            if (cases.length === 0) {
                casesList.innerHTML = '<p style="color: white; text-align: center;">No cases yet. Create your first case!</p>';
            }
        })
        .catch(err => console.error('Error loading cases:', err));
}

// Show Case Details
function showCaseDetails(caseId) {
    fetch(`${API_URL}/cases/${caseId}`)
        .then(res => res.json())
        .then(caseItem => {
            return fetch(`${API_URL}/cases/${caseId}/advice`).then(res => res.json()).then(advice => {
                return { ...caseItem, advice };
            });
        })
        .then(caseWithAdvice => {
            const modal = document.getElementById('case-modal');
            const details = document.getElementById('case-details');
            
            let adviceHTML = '';
            if (caseWithAdvice.advice && caseWithAdvice.advice.length > 0) {
                adviceHTML = '<h4>Legal Advice:</h4><ul>';
                caseWithAdvice.advice.forEach(item => {
                    adviceHTML += `<li>${item.advice}</li>`;
                });
                adviceHTML += '</ul>';
            }
            
            details.innerHTML = `
                <h3>${caseWithAdvice.title}</h3>
                <p><strong>Category:</strong> ${caseWithAdvice.category || 'Uncategorized'}</p>
                <p><strong>Status:</strong> ${caseWithAdvice.status}</p>
                <p><strong>Priority:</strong> ${caseWithAdvice.priority}</p>
                <p><strong>Description:</strong></p>
                <p>${caseWithAdvice.description}</p>
                <p><strong>Notes:</strong> ${caseWithAdvice.notes || 'None'}</p>
                ${adviceHTML}
            `;
            
            modal.style.display = 'block';
        })
        .catch(err => console.error('Error loading case details:', err));
}

// Modal Close
const modal = document.getElementById('case-modal');
const closeBtn = document.querySelector('.close');

closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Load Legal Info
function loadLegalInfo() {
    fetch(`${API_URL}/categories`)
        .then(res => res.json())
        .then(categories => {
            const grid = document.getElementById('categories-grid');
            grid.innerHTML = '';
            
            categories.forEach(category => {
                const card = document.createElement('div');
                card.className = 'category-card';
                card.innerHTML = `
                    <h3>${category.name}</h3>
                    <p>${category.description}</p>
                `;
                
                card.addEventListener('click', () => {
                    fetch(`${API_URL}/category-info/${category.name}`)
                        .then(res => res.json())
                        .then(info => {
                            alert(`${category.name}\n\n${info.description}\n\nKey Elements: ${info.key_elements?.join(', ')}\n\nAdvice: ${info.advice}`);
                        });
                });
                
                grid.appendChild(card);
            });
        })
        .catch(err => console.error('Error loading categories:', err));
}

// Search Cases
const searchInput = document.getElementById('search-cases');
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const caseCards = document.querySelectorAll('.case-card');
        
        caseCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchTerm) ? 'block' : 'none';
        });
    });
}

// Initialize
loadDashboard();
