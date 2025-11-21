document.addEventListener('DOMContentLoaded', () => {
    // Initialize Quill Editor
    const quill = new Quill('#editor-container', {
        theme: 'snow',
        placeholder: 'Compose your email here...',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'header': 1 }, { 'header': 2 }],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                ['link', 'image'],
                ['clean']
            ]
        }
    });

    // State
    let recipients = [];
    let attachmentFile = null;
    let resumeFile = null;

    // Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Manual Recipient Parsing
    document.getElementById('parse-manual-btn').addEventListener('click', () => {
        const text = document.getElementById('manual-recipients').value;
        if (!text) return showToast('Please enter email addresses', 'error');

        const emails = text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi);

        if (emails) {
            addRecipients(emails);
            document.getElementById('manual-recipients').value = '';
            showToast(`Added ${emails.length} recipients`, 'success');
        } else {
            showToast('No valid emails found', 'error');
        }
    });

    // CSV Upload
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-upload');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border)';
        if (e.dataTransfer.files.length) {
            handleCsvFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleCsvFile(e.target.files[0]);
        }
    });

    async function handleCsvFile(file) {
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            return showToast('Please upload a CSV file', 'error');
        }

        const formData = new FormData();
        formData.append('file', file);

        showLoading(true);
        try {
            const response = await fetch('/api/parse-csv', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to parse CSV');

            const data = await response.json();
            addRecipients(data.recipients);

            document.getElementById('filename').textContent = file.name;
            document.getElementById('file-info').classList.remove('hidden');
            document.getElementById('drop-zone').classList.add('hidden');

            showToast(`Imported ${data.recipients.length} recipients from CSV`, 'success');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            showLoading(false);
        }
    }

    document.getElementById('remove-file').addEventListener('click', () => {
        document.getElementById('file-info').classList.add('hidden');
        document.getElementById('drop-zone').classList.remove('hidden');
        fileInput.value = '';
    });

    // Recipient Management
    function addRecipients(newEmails) {
        // Filter duplicates
        const uniqueNew = newEmails.filter(e => !recipients.includes(e));
        recipients = [...recipients, ...uniqueNew];
        renderRecipients();
    }

    function renderRecipients() {
        const list = document.getElementById('recipient-list');
        const count = document.getElementById('recipient-count');
        const clearBtn = document.getElementById('clear-recipients-btn');

        list.innerHTML = '';
        recipients.forEach(email => {
            const chip = document.createElement('div');
            chip.className = 'recipient-chip';
            chip.innerHTML = `
                <span>${email}</span>
                <i class="fas fa-times" onclick="removeRecipient('${email}')"></i>
            `;
            list.appendChild(chip);
        });

        count.textContent = `${recipients.length} recipients`;

        if (recipients.length > 0) {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }
    }

    window.removeRecipient = (email) => {
        recipients = recipients.filter(e => e !== email);
        renderRecipients();
    };

    document.getElementById('clear-recipients-btn').addEventListener('click', () => {
        recipients = [];
        renderRecipients();
    });

    // AI Generation
    document.getElementById('resume-upload').addEventListener('change', (e) => {
        if (e.target.files.length) {
            resumeFile = e.target.files[0];
            document.getElementById('resume-name').textContent = resumeFile.name;
        }
    });

    document.getElementById('generate-btn').addEventListener('click', async () => {
        const prompt = document.getElementById('ai-prompt').value;
        if (!prompt) return showToast('Please enter a prompt for the AI', 'error');

        showLoading(true, 'Generating email content...');
        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            if (resumeFile) {
                formData.append('resume', resumeFile);
            }

            const response = await fetch('/api/generate-email', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Generation failed');
            }

            const data = await response.json();
            document.getElementById('email-subject').value = data.subject;
            quill.root.innerHTML = data.body;

            showToast('Email generated successfully!', 'success');
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            showLoading(false);
        }
    });

    // Attachment
    document.getElementById('attachment-input').addEventListener('change', (e) => {
        if (e.target.files.length) {
            attachmentFile = e.target.files[0];
            document.getElementById('attachment-name').textContent = attachmentFile.name;
        }
    });

    // Send Emails
    document.getElementById('send-btn').addEventListener('click', async () => {
        const senderEmail = document.getElementById('sender-email').value;
        const senderPassword = document.getElementById('sender-password').value;
        const subject = document.getElementById('email-subject').value;
        const body = quill.root.innerHTML;
        const sendingMode = document.querySelector('input[name="sending-mode"]:checked').value;

        if (!senderEmail || !senderPassword) return showToast('Please provide sender credentials', 'error');
        if (recipients.length === 0) return showToast('Please add at least one recipient', 'error');
        if (!subject) return showToast('Please enter a subject', 'error');
        if (quill.getText().trim().length === 0 && !attachmentFile) return showToast('Email body cannot be empty', 'error');

        const formData = new FormData();
        formData.append('sender_email', senderEmail);
        formData.append('sender_password', senderPassword);
        formData.append('recipients', JSON.stringify(recipients));
        formData.append('subject', subject);
        formData.append('body', body);
        formData.append('sending_mode', sendingMode);

        if (attachmentFile) {
            formData.append('attachment', attachmentFile);
        }

        // Show Progress Modal
        showProgressModal(true);

        try {
            const response = await fetch('/api/send-email', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Sending failed');
            }

            const data = await response.json();
            const taskId = data.task_id;

            // Start polling
            pollProgress(taskId);

        } catch (error) {
            showToast(error.message, 'error');
            showProgressModal(false);
        }
    });

    function pollProgress(taskId) {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`/api/task-status/${taskId}`);
                if (!res.ok) return;

                const status = await res.json();
                updateProgressUI(status);

                if (status.status === 'completed' || status.status === 'failed') {
                    clearInterval(interval);
                    document.getElementById('close-progress-btn').classList.remove('hidden');
                    if (status.status === 'completed') {
                        showToast('All emails sent!', 'success');
                    } else {
                        showToast('Sending failed: ' + status.message, 'error');
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }, 1000);
    }

    function updateProgressUI(status) {
        const bar = document.getElementById('progress-bar');
        const text = document.getElementById('progress-text');
        const details = document.getElementById('progress-details');

        const percent = status.total > 0 ? (status.sent / status.total) * 100 : 0;
        bar.style.width = `${percent}%`;
        text.textContent = status.message;
        details.textContent = `${status.sent}/${status.total}`;
    }

    function showProgressModal(show) {
        const modal = document.getElementById('progress-modal');
        const closeBtn = document.getElementById('close-progress-btn');

        if (show) {
            modal.classList.remove('hidden');
            closeBtn.classList.add('hidden');
            updateProgressUI({ sent: 0, total: 0, message: 'Initializing...' });
        } else {
            modal.classList.add('hidden');
        }
    }

    document.getElementById('close-progress-btn').addEventListener('click', () => {
        showProgressModal(false);
    });

    // UI Helpers
    function showLoading(show, text = 'Processing...') {
        const overlay = document.getElementById('loading-overlay');
        const loadingText = document.getElementById('loading-text');

        if (show) {
            loadingText.textContent = text;
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s reverse forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
