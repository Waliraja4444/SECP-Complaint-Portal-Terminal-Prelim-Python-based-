// SECP Complaints Classification System - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeComplaintForm();
    initializeDashboard();
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

function initializeComplaintForm() {
    const form = document.getElementById('complaint-form');
    if (!form) return;

    const complaintText = document.getElementById('complaint_text');
    const classifyBtn = document.getElementById('classify-btn');
    const classifyText = document.getElementById('classify-text');
    const aiResults = document.getElementById('ai-results');
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    const natureSelect = document.getElementById('nature_of_issue');
    const applyChangesBtn = document.getElementById('apply-changes-btn');
    const changesApplied = document.getElementById('changes-applied');
    const errorMessage = document.getElementById('error-message');
    const submitBtn = document.getElementById('submit-btn');

    // Complaint categories data
    const complaintCategories = {
        'Insurance Services': {
            'subcategories': ['Health Insurance Claims', 'Life Insurance Claims', 'Motor Insurance Claims', 'Property Insurance Claims'],
            'nature_of_issues': ['Delayed Processing', 'Claim Rejection', 'Premium Issues', 'Policy Terms Dispute']
        },
        'Brokerage Services': {
            'subcategories': ['Unauthorized Trading', 'Account Management', 'Commission Disputes', 'Market Manipulation'],
            'nature_of_issues': ['Account Manipulation', 'Excessive Charges', 'Poor Service Quality', 'Regulatory Violations']
        },
        'Investment Services': {
            'subcategories': ['Mutual Funds', 'Securities Trading', 'Portfolio Management', 'Investment Advisory'],
            'nature_of_issues': ['Performance Issues', 'Misleading Information', 'Unauthorized Transactions', 'Fee Disputes']
        },
        'Pension Services': {
            'subcategories': ['Retirement Benefits', 'Provident Fund', 'Gratuity Claims', 'Pension Payments'],
            'nature_of_issues': ['Withdrawal Process', 'Calculation Errors', 'Delayed Payments', 'Documentation Issues']
        },
        'Banking Services': {
            'subcategories': ['Loan Services', 'Account Services', 'Credit Cards', 'Digital Banking'],
            'nature_of_issues': ['Interest Rate Dispute', 'Service Charges', 'Account Access Issues', 'Transaction Disputes']
        },
        'Capital Markets': {
            'subcategories': ['Stock Exchange', 'Bond Markets', 'Derivatives', 'Market Infrastructure'],
            'nature_of_issues': ['Trading Issues', 'Settlement Problems', 'Market Data Issues', 'Regulatory Compliance']
        }
    };

    // AI Classification
    if (classifyBtn) {
        classifyBtn.addEventListener('click', async function() {
            const text = complaintText.value.trim();
            if (!text) {
                showError('Please enter a complaint description first.');
                return;
            }

            setLoadingState(classifyBtn, classifyText, true);
            
            try {
                const response = await fetch('/api/classify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        complaint_text: text
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                displayAIResults(result.classification);
                populateManualForm(result.classification);
                
            } catch (error) {
                console.error('Classification error:', error);
                showError('Failed to classify complaint. Please try again or fill manually.');
            } finally {
                setLoadingState(classifyBtn, classifyText, false);
            }
        });
    }

    // Category change handler
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const category = this.value;
            updateSubcategories(category);
            updateNatureOfIssues(category);
        });
    }

    // Apply Changes button
    if (applyChangesBtn) {
        applyChangesBtn.addEventListener('click', function() {
            const category = categorySelect.value;
            const subcategory = subcategorySelect.value;
            const nature = natureSelect.value;

            if (!category || !subcategory || !nature) {
                showError('Fill the fields first');
                return;
            }

            hideError();
            changesApplied.classList.remove('hidden');
            submitBtn.disabled = false;
            
            // Add success animation
            changesApplied.classList.add('fade-in');
        });
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            const category = categorySelect.value;
            const subcategory = subcategorySelect.value;
            const nature = natureSelect.value;

            if (!category || !subcategory || !nature || submitBtn.disabled) {
                e.preventDefault();
                showError('Fill the fields first');
                return;
            }

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="loading-spinner mr-2"></div>Submitting...';
        });
    }

    function setLoadingState(button, textElement, loading) {
        if (loading) {
            button.disabled = true;
            textElement.innerHTML = '<div class="loading-spinner mr-2"></div>Classifying...';
        } else {
            button.disabled = false;
            textElement.innerHTML = '<i data-lucide="brain-circuit" class="w-5 h-5 mr-2"></i>Classify with AI';
            lucide.createIcons();
        }
    }

    function displayAIResults(classification) {
        document.getElementById('ai-category').textContent = classification.category;
        document.getElementById('ai-subcategory').textContent = classification.subcategory;
        document.getElementById('ai-nature').textContent = classification.nature_of_issue;
        
        const confidence = Math.round(classification.confidence * 100);
        document.getElementById('confidence-text').textContent = `${confidence}%`;
        document.getElementById('confidence-bar').style.width = `${confidence}%`;
        
        aiResults.classList.remove('hidden');
        aiResults.classList.add('fade-in');
    }

    function populateManualForm(classification) {
        categorySelect.value = classification.category;
        updateSubcategories(classification.category);
        
        setTimeout(() => {
            subcategorySelect.value = classification.subcategory;
            updateNatureOfIssues(classification.category);
            
            setTimeout(() => {
                natureSelect.value = classification.nature_of_issue;
            }, 100);
        }, 100);
    }

    function updateSubcategories(category) {
        subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';
        natureSelect.innerHTML = '<option value="">Select Nature of Issue</option>';
        
        if (category && complaintCategories[category]) {
            subcategorySelect.disabled = false;
            complaintCategories[category].subcategories.forEach(sub => {
                const option = document.createElement('option');
                option.value = sub;
                option.textContent = sub;
                subcategorySelect.appendChild(option);
            });
        } else {
            subcategorySelect.disabled = true;
            natureSelect.disabled = true;
        }
    }

    function updateNatureOfIssues(category) {
        natureSelect.innerHTML = '<option value="">Select Nature of Issue</option>';
        
        if (category && complaintCategories[category]) {
            natureSelect.disabled = false;
            complaintCategories[category].nature_of_issues.forEach(nature => {
                const option = document.createElement('option');
                option.value = nature;
                option.textContent = nature;
                natureSelect.appendChild(option);
            });
        } else {
            natureSelect.disabled = true;
        }
    }

    function showError(message) {
        errorMessage.querySelector('p').textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.classList.add('slide-up');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }
}

function initializeDashboard() {
    const successBanner = document.getElementById('success-banner');
    if (successBanner) {
        // Trigger confetti if on dashboard with success
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('success')) {
            triggerConfetti();
            
            // Remove success parameter after animation
            setTimeout(() => {
                const url = new URL(window.location);
                url.searchParams.delete('success');
                window.history.replaceState({}, document.title, url.pathname);
            }, 3000);
        }
    }
}

function triggerConfetti() {
    if (typeof confetti !== 'undefined') {
        // Multiple confetti bursts
        const duration = 3000;
        const animationEnd = Date.now() + duration;
        const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        const interval = setInterval(function() {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);
            
            confetti(Object.assign({}, defaults, {
                particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
            }));
            
            confetti(Object.assign({}, defaults, {
                particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
            }));
        }, 250);
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Export functions for potential external use
window.SECPApp = {
    triggerConfetti,
    formatDate,
    truncateText
};