document.addEventListener('DOMContentLoaded', () => {

    // --- Selectors ---
    const uploadForm = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const clearDbBtn = document.getElementById('clear-db-btn');
    const generateForm = document.getElementById('generate-form');
    const generateBtn = document.getElementById('generate-btn');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const welcomeMessage = document.getElementById('welcome-message');
    const resultsContainer = document.getElementById('results-container');
    const downloadBtn = document.getElementById('download-json-btn');
    
    // Card Templates
    const mcqTemplate = document.getElementById('mcq-card-template');
    const qaTemplate = document.getElementById('qa-card-template');

    // UI/UX Selectors
    const toastContainer = document.getElementById('toast-container');
    const toastTemplate = document.getElementById('toast-template');
    const fileInput = document.getElementById('file-input');
    const dropzone = document.getElementById('dropzone');
    const fileStatusMessage = document.getElementById('file-status-message');

    // --- NEW: Selectors for New UI ---
    const skeletonTemplate = document.getElementById('skeleton-card-template');
    const tipsPanel = document.getElementById('tips-panel');
    const detailsPanel = document.getElementById('details-panel');
    const detailQuery = document.getElementById('detail-query');
    const detailType = document.getElementById('detail-type');
    const detailWebSearch = document.getElementById('detail-web-search');

    // --- State ---
    let lastGeneratedData = null;
    
    // --- Toast Notification Function ---
    const showToast = (message, type = 'info', duration = 4000) => {
        if (!toastTemplate) return;
        
        const toastClone = toastTemplate.content.cloneNode(true);
        const toastElement = toastClone.querySelector('.toast-base');
        const toastMessage = toastElement.querySelector('.toast-message');
        const toastCloseBtn = toastElement.querySelector('.toast-close-btn');
        const iconContainer = toastElement.querySelector('.toast-icon');

        toastMessage.textContent = message;

        Array.from(iconContainer.children).forEach(icon => icon.classList.add('hidden'));
        if (type === 'success') {
            iconContainer.querySelector('.text-green-500').classList.remove('hidden');
        } else if (type === 'error') {
            iconContainer.querySelector('.text-red-500').classList.remove('hidden');
        } else { // 'info'
            iconContainer.querySelector('.text-primary-500').classList.remove('hidden');
        }
        
        const removeToast = () => {
            toastElement.classList.add('toast-exit');
            toastElement.addEventListener('animationend', () => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
            });
        };

        toastCloseBtn.addEventListener('click', removeToast);
        setTimeout(removeToast, duration);
        toastContainer.appendChild(toastElement);
    };

    // --- Utility Functions ---
    const showLoading = (btn, text = 'Processing...') => {
        btn.disabled = true;
        btn.innerHTML = `
            <div class="spinner w-5 h-5 border-2 border-white rounded-full mr-2"></div>
            ${text}
        `;
    };

    const hideLoading = (btn, originalText) => {
        btn.disabled = false;
        btn.innerHTML = originalText;
    };
    
    // --- NEW: Skeleton Loading Function ---
    const showSkeletonLoading = (count) => {
        welcomeMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');
        resultsContainer.innerHTML = ''; // Clear previous results

        for (let i = 0; i < count; i++) {
            const skeleton = skeletonTemplate.content.cloneNode(true);
            resultsContainer.appendChild(skeleton);
        }
    };

    // --- NEW: Context Panel Functions ---
    const showGenerationDetails = (query, numQuestions, type, useTavily) => {
        detailQuery.textContent = query;
        detailType.textContent = `${numQuestions} ${type.toUpperCase()} Questions`;
        detailWebSearch.textContent = useTavily ? 'Enabled' : 'Disabled';
        
        // --- NEW: Style the web search status ---
        if (useTavily) {
            detailWebSearch.classList.remove('text-gray-900', 'text-red-600');
            detailWebSearch.classList.add('text-green-600');
        } else {
            detailWebSearch.classList.remove('text-green-600', 'text-red-600');
            detailWebSearch.classList.add('text-gray-900');
        }
        
        tipsPanel.classList.add('hidden');
        detailsPanel.classList.remove('hidden');
    };

    const resetContextPanel = () => {
        tipsPanel.classList.remove('hidden');
        detailsPanel.classList.add('hidden');
    };

    const showError = (message) => {
        resultsContainer.innerHTML = ''; // Clear skeletons
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        welcomeMessage.classList.add('hidden');
        resetContextPanel(); // Hide details, show tips
    };

    // --- Drag-and-Drop File Handling ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-over'), false);
    });

    dropzone.addEventListener('drop', (e) => {
        fileInput.files = e.dataTransfer.files;
        updateFileStatus(fileInput.files);
    }, false);

    fileInput.addEventListener('change', () => {
        updateFileStatus(fileInput.files);
    });
    
    function updateFileStatus(files) {
        if (files.length > 0) {
            fileStatusMessage.textContent = `${files[0].name} selected`;
        } else {
            fileStatusMessage.textContent = '';
        }
    }


    // --- Event Handlers ---

    /**
     * Handle File Upload
     */
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast('Please select a file to upload.', 'error');
            return;
        }
        
        const formData = new FormData(uploadForm);
        const originalBtnText = uploadBtn.innerHTML;
        
        fileStatusMessage.textContent = 'Processing file...';
        showLoading(uploadBtn, 'Uploading...');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'File upload failed.');
            }

            showToast(result.message, 'success');
            fileInput.value = '';
            fileStatusMessage.textContent = 'Upload successful!';
            setTimeout(() => { fileStatusMessage.textContent = ''; }, 2000);


        } catch (err) {
            showToast(err.message, 'error');
            fileStatusMessage.textContent = 'Upload failed.';
        } finally {
            hideLoading(uploadBtn, originalBtnText);
            resultsContainer.innerHTML = ''; // Clear results
            downloadBtn.classList.add('hidden');
            welcomeMessage.classList.remove('hidden'); // Show welcome again
            resetContextPanel();
        }
    });

    /**
     * Handle Clear Database
     */
    clearDbBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear the entire database? This action cannot be undone.')) {
            return;
        }

        const originalBtnText = clearDbBtn.innerHTML;
        showLoading(clearDbBtn, 'Clearing...');

        try {
            const response = await fetch('/clear-db', {
                method: 'POST',
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to clear database.');
            }
            
            showToast(result.message, result.type);
            resultsContainer.innerHTML = '';
            downloadBtn.classList.add('hidden');
            welcomeMessage.classList.remove('hidden'); // Show welcome message again
            resetContextPanel();

        } catch (err)
        {
            showToast(err.message, 'error');
        } finally {
            hideLoading(clearDbBtn, originalBtnText);
        }
    });

    /**
     * Handle Generation
     */
    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const query = document.getElementById('query-input').value;
        const numQuestions = parseInt(document.getElementById('num-questions-input').value, 10);
        const type = document.getElementById('type-select').value;
        const useTavily = document.getElementById('tavily-toggle').checked;

        if (!query.trim()) {
            showToast('Please enter a query or topic.', 'error');
            return;
        }

        const originalBtnText = generateBtn.innerHTML;
        showLoading(generateBtn, 'Generating...');
        
        // --- NEW: Show skeletons and context panel ---
        showSkeletonLoading(numQuestions);
        showGenerationDetails(query, numQuestions, type, useTavily);
        // ---
        
        lastGeneratedData = null;
        downloadBtn.classList.add('hidden');
        errorMessage.classList.add('hidden'); // Hide old errors

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    numQuestions: numQuestions,
                    type: type,
                    useTavily: useTavily
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to generate questions.');
            }

            lastGeneratedData = result.data;
            renderResults(result.data, type); // This will replace the skeletons
            downloadBtn.classList.remove('hidden');

        } catch (err) {
            showError(err.message);
        } finally {
            hideLoading(generateBtn, originalBtnText);
            // Skeletons/error message are handled by renderResults or showError
        }
    });

    /**
     * Handle Download JSON
     */
    downloadBtn.addEventListener('click', () => {
        if (!lastGeneratedData) {
            showToast('No data to download.', 'error');
            return;
        }

        const dataStr = JSON.stringify(lastGeneratedData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_questions.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // --- Rendering Functions (With robust parsing) ---
    
    const renderResults = (data, type) => {
        resultsContainer.innerHTML = ''; // Clear skeletons
        let dataArray = []; 

        if (Array.isArray(data)) {
            dataArray = data;
        } else if (data && typeof data === 'object') {
            if (type === 'mcq' && data.mcq_list && Array.isArray(data.mcq_list)) {
                dataArray = data.mcq_list;
            } else if (type === 'qa' && data.qa_list && Array.isArray(data.qa_list)) {
                dataArray = data.qa_list;
            } else {
                let found = false;
                for (const key in data) {
                    if (Array.isArray(data[key]) && data[key].length > 0) {
                        const firstItem = data[key][0];
                        if (firstItem && typeof firstItem === 'object') {
                            if (type === 'mcq' && firstItem.question && firstItem.options) {
                                dataArray = data[key];
                                found = true;
                                break;
                            }
                            if (type === 'qa' && firstItem.question && firstItem.answer) {
                                dataArray = data[key];
                                found = true;
                                break;
                            }
                        }
                    }
                }
                if (!found && !Array.isArray(data)) {
                    if (type === 'mcq' && data.question && data.options) {
                         dataArray = [data];
                    } else if (type === 'qa' && data.question && data.answer) {
                         dataArray = [data];
                    }
                }
            }
        }

        if (!dataArray || dataArray.length === 0) {
            if (data && typeof data === 'object' && !Array.isArray(data)) {
                 showError('The model returned an object, but no valid questions could be found inside it. Check the downloaded JSON for details.');
            } else {
                 showError('The model returned no results or an unexpected data format. Try again.');
            }
            return;
        }

        if (type === 'mcq') {
            dataArray.forEach((item, index) => {
                if (!item || typeof item.question !== 'string' || !Array.isArray(item.options)) {
                    console.warn('Skipping malformed MCQ item:', item);
                    return; 
                }
                
                const card = mcqTemplate.content.cloneNode(true);
                card.querySelector('.question-text').textContent = `${index + 1}. ${item.question}`;
                
                const optionsList = card.querySelector('.options-list');
                const correctIndex = parseInt(item.correct_index, 10);
                
                item.options.forEach((option, i) => {
                    const li = document.createElement('li');
                    const isCorrect = (i + 1) === correctIndex;
                    
                    li.className = `flex items-center p-3 rounded-lg ${isCorrect ? 'bg-primary-50 border border-primary-200' : 'bg-gray-50'}`;
                    
                    const icon = document.createElement('span');
                    icon.className = `mr-3 font-semibold ${isCorrect ? 'text-primary-600' : 'text-gray-500'}`;
                    icon.textContent = `${String.fromCharCode(65 + i)}.`;
                    
                    const text = document.createElement('span');
                    text.className = ` ${isCorrect ? 'font-semibold text-primary-800' : 'text-gray-800'}`;
                    text.textContent = String(option); 
                    
                    li.appendChild(icon);
                    li.appendChild(text);
                    optionsList.appendChild(li);
                });

                card.querySelector('.explanation-text').textContent = item.explanation || 'No explanation provided.';
                resultsContainer.appendChild(card);
            });
        } else { // 'qa'
             dataArray.forEach((item, index) => {
                if (!item || typeof item.question !== 'string' || typeof item.answer !== 'string') {
                    console.warn('Skipping malformed Q&A item:', item);
                    return;
                }

                const card = qaTemplate.content.cloneNode(true);
                card.querySelector('.question-text').textContent = `${index + 1}. ${item.question}`;
                card.querySelector('.answer-text').textContent = item.answer;
                resultsContainer.appendChild(card);
            });
        }
    };

});