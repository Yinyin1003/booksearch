// 引入配置（需要在 app.js 之前加载）
// <script src="static/js/config.js"></script>

// 全局变量
let books = {};
let currentBook = null;
let imageLoaded = false;
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let selectedRect = null;
let editMode = 'points'; // 只使用四点模式
let points = [null, null, null, null]; // 四个角点
let currentPointIndex = 0; // 当前正在编辑的点

// DOM元素
const bookshelfImage = document.getElementById('bookshelfImage');
const overlayCanvas = document.getElementById('overlayCanvas');
const ctx = overlayCanvas.getContext('2d');
const bookList = document.getElementById('bookList');
const bookEditor = document.getElementById('bookEditor');
const imageUpload = document.getElementById('imageUpload');

// 初始化
async function init() {
    await loadBooks();
    await loadSettings();
    setupEventListeners();
    
    // 等待图片加载完成后再绘制
    if (bookshelfImage.complete) {
        setTimeout(() => {
            resizeCanvas();
            drawBooks();
        }, 100);
    } else {
        bookshelfImage.addEventListener('load', () => {
            setTimeout(() => {
                resizeCanvas();
                drawBooks();
            }, 100);
        }, { once: true });
    }
}

// 加载书籍数据
async function loadBooks() {
    try {
        const response = await apiFetch('/api/books');
        books = await response.json();
        renderBookList();
    } catch (error) {
        console.error('加载书籍失败:', error);
        alert('无法连接到后端 API，请检查配置');
    }
}

// 加载设置
async function loadSettings() {
    try {
        const response = await apiFetch('/api/settings');
        const settings = await response.json();
        updateSettingsUI(settings);
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// ... 其余代码与原 app.js 相同，但所有 fetch 调用改为 apiFetch ...

