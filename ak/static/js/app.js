// API Configuration
const API_BASE = '/api';

// State
let currentFilter = 'unread';
let articles = [];

// DOM Elements
const articlesContainer = document.getElementById('articlesContainer');
const addArticleBtn = document.getElementById('addArticleBtn');
const sendDigestBtn = document.getElementById('sendDigestBtn');
const addArticleModal = document.getElementById('addArticleModal');
const articleModal = document.getElementById('articleModal');
const articleUrl = document.getElementById('articleUrl');
const submitArticle = document.getElementById('submitArticle');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            loadArticles();
        });
    });

    // Modal tabs (URL vs Text)
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            document.getElementById(tab + 'Tab').classList.add('active');
        });
    });

    // Add article button
    addArticleBtn.addEventListener('click', () => {
        // Clear inputs when opening modal
        document.getElementById('articleUrl').value = '';
        document.getElementById('articleTitle').value = '';
        document.getElementById('articleText').value = '';
        openModal(addArticleModal);
    });

    // Send digest button
    sendDigestBtn.addEventListener('click', () => {
        sendDigest();
    });

    // Submit article
    submitArticle.addEventListener('click', () => {
        addArticle();
    });

    // Article URL enter key
    articleUrl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addArticle();
        }
    });

    // Close modals
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            closeModal(e.target.closest('.modal'));
        });
    });

    // Close modal on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
}

// API Functions
async function loadArticles() {
    try {
        showLoading();

        let url = `${API_BASE}/articles`;
        const params = new URLSearchParams();

        if (currentFilter === 'favorited') {
            params.append('favorited', 'true');
        } else if (currentFilter !== 'all') {
            params.append('status', currentFilter);
        }

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await fetch(url);
        articles = await response.json();

        renderArticles();
    } catch (error) {
        console.error('Error loading articles:', error);
        showError('Failed to load articles');
    }
}

async function addArticle() {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

    let requestBody = {};

    if (activeTab === 'url') {
        const url = document.getElementById('articleUrl').value.trim();
        if (!url) {
            showNotification('Please enter a URL', 'error');
            return;
        }
        requestBody = { url };
    } else {
        const title = document.getElementById('articleTitle').value.trim();
        const text = document.getElementById('articleText').value.trim();
        if (!text) {
            showNotification('Please paste article text', 'error');
            return;
        }
        requestBody = {
            text: text,
            title: title || 'Pasted Article'
        };
    }

    try {
        showNotification('Adding article...', 'info');
        closeModal(addArticleModal);

        const response = await fetch(`${API_BASE}/articles`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (response.ok) {
            showNotification('Article added successfully!', 'success');
            document.getElementById('articleUrl').value = '';
            document.getElementById('articleTitle').value = '';
            document.getElementById('articleText').value = '';
            loadArticles();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to add article', 'error');
        }
    } catch (error) {
        console.error('Error adding article:', error);
        showNotification('Failed to add article', 'error');
    }
}

async function viewArticle(articleId) {
    try {
        const response = await fetch(`${API_BASE}/articles/${articleId}`);
        const article = await response.json();

        renderArticleDetail(article);
        openModal(articleModal);
    } catch (error) {
        console.error('Error loading article:', error);
        showNotification('Failed to load article', 'error');
    }
}

async function markAsRead(articleId, event) {
    event.stopPropagation();

    try {
        await fetch(`${API_BASE}/articles/${articleId}/read`, {
            method: 'POST'
        });

        showNotification('Marked as read', 'success');
        loadArticles();
    } catch (error) {
        console.error('Error marking as read:', error);
        showNotification('Failed to mark as read', 'error');
    }
}

async function markAsUnread(articleId, event) {
    event.stopPropagation();

    try {
        await fetch(`${API_BASE}/articles/${articleId}/unread`, {
            method: 'POST'
        });

        showNotification('Marked as unread', 'success');
        loadArticles();
    } catch (error) {
        console.error('Error marking as unread:', error);
        showNotification('Failed to mark as unread', 'error');
    }
}

async function archiveArticle(articleId, event) {
    event.stopPropagation();

    try {
        await fetch(`${API_BASE}/articles/${articleId}/archive`, {
            method: 'POST'
        });

        showNotification('Article archived', 'success');
        loadArticles();
    } catch (error) {
        console.error('Error archiving article:', error);
        showNotification('Failed to archive article', 'error');
    }
}

async function toggleFavorite(articleId, event) {
    event.stopPropagation();

    try {
        const response = await fetch(`${API_BASE}/articles/${articleId}/favorite`, {
            method: 'POST'
        });

        const data = await response.json();
        showNotification(data.favorited ? 'Added to favorites' : 'Removed from favorites', 'success');
        loadArticles();
    } catch (error) {
        console.error('Error toggling favorite:', error);
        showNotification('Failed to update favorite', 'error');
    }
}

async function generateAudio(articleId) {
    try {
        showNotification('Generating audio...', 'info');

        const response = await fetch(`${API_BASE}/articles/${articleId}/audio`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            showNotification('Audio generated!', 'success');

            // Reload article detail to show audio player
            viewArticle(articleId);
        } else {
            showNotification('Failed to generate audio', 'error');
        }
    } catch (error) {
        console.error('Error generating audio:', error);
        showNotification('Failed to generate audio', 'error');
    }
}

async function sendDigest() {
    try {
        showNotification('Sending digest...', 'info');

        const response = await fetch(`${API_BASE}/digest/send`, {
            method: 'POST'
        });

        if (response.ok) {
            showNotification('Digest sent!', 'success');
        } else {
            showNotification('Failed to send digest', 'error');
        }
    } catch (error) {
        console.error('Error sending digest:', error);
        showNotification('Failed to send digest', 'error');
    }
}

// Rendering Functions
function renderArticles() {
    if (articles.length === 0) {
        articlesContainer.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <p>No articles found</p>
            </div>
        `;
        return;
    }

    articlesContainer.innerHTML = articles.map(article => createArticleCard(article)).join('');
}

function createArticleCard(article) {
    const isRead = article.status === 'read';
    const isFavorited = article.favorited === 1;

    return `
        <div class="article-card ${isRead ? 'read' : ''}" onclick="viewArticle(${article.id})">
            <div class="article-meta">
                <span class="article-source">${article.source || 'Unknown'}</span>
                ${article.author ? `<span>• ${article.author}</span>` : ''}
                <span class="status-badge status-${article.status}">${article.status}</span>
            </div>
            <div class="article-title">${article.title || 'Untitled'}</div>
            <div class="article-summary">${article.summary || 'No summary available'}</div>
            <div class="article-actions">
                ${isRead
                    ? `<button class="btn btn-small btn-secondary" onclick="markAsUnread(${article.id}, event)">Mark Unread</button>`
                    : `<button class="btn btn-small btn-primary" onclick="markAsRead(${article.id}, event)">Mark Read</button>`
                }
                <button class="btn btn-small btn-favorite ${isFavorited ? 'favorited' : ''}" onclick="toggleFavorite(${article.id}, event)">
                    ${isFavorited ? '★' : '☆'}
                </button>
                <button class="btn btn-small btn-secondary" onclick="archiveArticle(${article.id}, event)">Archive</button>
            </div>
        </div>
    `;
}

function renderArticleDetail(article) {
    let keyInsights = article.key_insights;
    if (typeof keyInsights === 'string') {
        try {
            keyInsights = JSON.parse(keyInsights);
        } catch {
            keyInsights = [];
        }
    }

    const insightsList = Array.isArray(keyInsights) && keyInsights.length > 0
        ? `<ul class="insights-list">
            ${keyInsights.map(insight => `<li>${insight}</li>`).join('')}
           </ul>`
        : '<p>No insights available</p>';

    const implicationsBox = article.implications
        ? `<div class="implications-box">${article.implications}</div>`
        : '<p>No implications available</p>';

    const audioPlayer = article.audio_path
        ? `<div class="audio-player">
            <audio controls>
                <source src="${article.audio_path}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
           </div>`
        : `<button class="btn btn-secondary" onclick="generateAudio(${article.id})">Generate Audio</button>`;

    document.getElementById('articleDetail').innerHTML = `
        <div class="article-detail-header">
            <h2 class="article-detail-title">${article.title || 'Untitled'}</h2>
            <div class="article-detail-meta">
                ${article.source || 'Unknown source'}
                ${article.author ? `• ${article.author}` : ''}
            </div>
        </div>

        <div class="section">
            <div class="section-title">Summary</div>
            <p>${article.summary || 'No summary available'}</p>
        </div>

        <div class="section">
            <div class="section-title">Key Insights</div>
            ${insightsList}
        </div>

        <div class="section">
            <div class="section-title">Why It Matters</div>
            ${implicationsBox}
        </div>

        <div class="section">
            <div class="section-title">Audio Summary</div>
            ${audioPlayer}
        </div>

        <div class="section">
            <a href="${article.url}" target="_blank" class="btn btn-primary" style="width: 100%; text-align: center; display: inline-block; text-decoration: none;">
                Read Full Article →
            </a>
        </div>
    `;
}

// UI Functions
function openModal(modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

function showLoading() {
    articlesContainer.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
}

function showError(message) {
    articlesContainer.innerHTML = `
        <div class="empty-state">
            <p style="color: var(--danger-color);">${message}</p>
        </div>
    `;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;

    if (type === 'error') {
        notification.style.backgroundColor = 'var(--danger-color)';
    } else if (type === 'success') {
        notification.style.backgroundColor = 'var(--success-color)';
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
