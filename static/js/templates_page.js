let pageCount = 1;
let editors = [];

// Sayfa Ekleme Fonksiyonu
function addPage() {
    pageCount++;

    const container = document.getElementById('pages-container');
    const pageCard = document.createElement('div');
    pageCard.classList.add('card', 'mb-3', 'page');
    pageCard.setAttribute('data-page-number', pageCount);

    pageCard.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center bg-light">
            <span>Sayfa ${pageCount}</span>
            <button type="button" class="btn btn-danger btn-sm" onclick="removePage(this)">
                <i class="fas fa-trash-alt"></i>
            </button>
        </div>
        <div class="card-body">
            <textarea class="form-control editor" name="page_content[]" rows="10" required></textarea>
        </div>
    `;

    container.appendChild(pageCard);
    const textarea = pageCard.querySelector('.editor');
    initializeCKEditor(textarea);
}

// Sayfa Silme Fonksiyonu
function removePage(button) {
    const pageCard = button.closest('.page');
    const textarea = pageCard.querySelector('.editor');

    if (textarea && CKEDITOR.instances[textarea.id]) {
        CKEDITOR.instances[textarea.id].destroy();
    }

    pageCard.remove();

    const pages = document.querySelectorAll('.page');
    pageCount = pages.length;
    pages.forEach((page, index) => {
        page.setAttribute('data-page-number', index + 1);
        page.querySelector('.card-header span').textContent = `Sayfa ${index + 1}`;
    });
}

// CKEditor'u Başlatma Fonksiyonu
function initializeCKEditor(textarea) {
    const uniqueId = `editor_${Math.random().toString(36).substr(2, 9)}`;
    textarea.id = uniqueId;

    CKEDITOR.replace(uniqueId, {
        toolbar: [
            { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline'] },
            { name: 'paragraph', items: ['NumberedList', 'BulletedList'] },
            { name: 'insert', items: ['CodeSnippet'] },
            { name: 'styles', items: ['Format'] },
            { name: 'undo', items: ['Undo', 'Redo'] }
        ],
        extraPlugins: 'codesnippet',
        codeSnippet_theme: 'monokai_sublime',
        removePlugins: 'image,link,table,elementspath'
    });

    editors.push(uniqueId);
}

// Sayfa Yüklendiğinde
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.editor').forEach(editor => {
        initializeCKEditor(editor);
    });

    const form = document.getElementById('template-form');
    form.addEventListener('submit', () => {
        editors.forEach(editorId => {
            if (CKEDITOR.instances[editorId]) {
                CKEDITOR.instances[editorId].updateElement();
            }
        });
    });
});