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
        const response = await fetch('/api/books');
        books = await response.json();
        renderBookList();
    } catch (error) {
        console.error('加载书籍失败:', error);
    }
}

// 加载设置
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        updateSettingsUI(settings);
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// 渲染书籍列表
function renderBookList() {
    bookList.innerHTML = '';
    Object.keys(books).forEach(key => {
        const book = books[key];
        const item = document.createElement('div');
        item.className = 'book-item';
        item.dataset.key = key;
        item.innerHTML = `
            <h3>${key}</h3>
            <p>${book.full_name}</p>
        `;
        item.addEventListener('click', () => selectBook(key));
        bookList.appendChild(item);
    });
}

// 选择书籍
function selectBook(key) {
    currentBook = key;
    
    // 更新列表高亮
    document.querySelectorAll('.book-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.key === key) {
            item.classList.add('active');
        }
    });
    
    // 显示编辑面板
    bookEditor.style.display = 'block';
    updateEditorUI();
    
    // 确保画布已初始化后再绘制
    if (imageLoaded) {
        resizeCanvas();
    } else {
        // 如果图片还没加载，等待加载完成
        bookshelfImage.addEventListener('load', () => {
            resizeCanvas();
        }, { once: true });
    }
}

// 更新编辑面板UI
function updateEditorUI() {
    if (!currentBook || !books[currentBook]) return;
    
    const book = books[currentBook];
    document.getElementById('bookKey').value = currentBook;
    document.getElementById('bookName').value = book.full_name;
    
    // 如果有四点数据，使用四点；否则从矩形位置计算四点
    if (book.points && book.points.length === 4) {
        // 使用保存的四点数据
        // 处理不同的数据格式：可能是元组列表或数组列表
        points = book.points.map(p => {
            if (Array.isArray(p)) {
                return [p[0], p[1]];
            } else {
                // 如果是元组格式，转换为数组
                return [p[0], p[1]];
            }
        });
        console.log('加载四点数据:', points);
    } else {
        // 从矩形位置计算四个角点
        const [x, y, w, h] = book.position;
        const xMin = x - w / 2;
        const xMax = x + w / 2;
        const yMin = y - h / 2;
        const yMax = y + h / 2;
        
        // 计算四个角点（左上、右上、右下、左下）
        points = [
            [xMin, yMin], // 左上
            [xMax, yMin], // 右上
            [xMax, yMax], // 右下
            [xMin, yMax]  // 左下
        ];
        console.log('从矩形计算四点:', points);
    }
    
    currentPointIndex = 0;
    updatePointsUI();
    drawBooks(); // 重新绘制
}

// 更新设置UI
function updateSettingsUI(settings) {
    document.getElementById('boxWidth').value = settings.box_width || 600;
    document.getElementById('boxHeight').value = settings.box_height || 180;
    document.getElementById('fontScale').value = settings.font_scale || 1.5;
    document.getElementById('fontThickness').value = settings.font_thickness || 3;
}

// 设置事件监听
function setupEventListeners() {
    // 图片加载
    bookshelfImage.addEventListener('load', () => {
        imageLoaded = true;
        // 延迟一下确保图片完全渲染
        setTimeout(() => {
            resizeCanvas();
        }, 100);
    });
    
    // 如果图片已经加载完成
    if (bookshelfImage.complete && bookshelfImage.naturalWidth > 0) {
        imageLoaded = true;
        setTimeout(() => {
            resizeCanvas();
        }, 100);
    }
    
    // 窗口大小改变
    window.addEventListener('resize', resizeCanvas);
    
    // 图片上传
    imageUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                bookshelfImage.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // 书名输入
    document.getElementById('bookName').addEventListener('input', (e) => {
        if (currentBook) {
            books[currentBook].full_name = e.target.value;
        }
    });
    
    // 显示设置变化
    ['boxWidth', 'boxHeight', 'fontScale', 'fontThickness'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateSettings);
    });
    
    // 按钮事件
    document.getElementById('updateBookBtn').addEventListener('click', updateBook);
    document.getElementById('deleteBookBtn').addEventListener('click', deleteBook);
    document.getElementById('cancelEditBtn').addEventListener('click', cancelEdit);
    document.getElementById('saveBtn').addEventListener('click', saveAll);
    document.getElementById('previewBtn').addEventListener('click', previewBook);
    
    // 四点输入框变化
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`point${i}X`).addEventListener('input', () => updatePointFromInput(i - 1));
        document.getElementById(`point${i}Y`).addEventListener('input', () => updatePointFromInput(i - 1));
    }
    
    // 画布事件
    overlayCanvas.addEventListener('mousedown', startDrag);
    overlayCanvas.addEventListener('mousemove', onDrag);
    overlayCanvas.addEventListener('mouseup', endDrag);
    overlayCanvas.addEventListener('mouseleave', endDrag);
    overlayCanvas.addEventListener('click', handleCanvasClick);
}

// 调整画布大小
function resizeCanvas() {
    if (!imageLoaded || !bookshelfImage.complete) return;
    
    const rect = bookshelfImage.getBoundingClientRect();
    overlayCanvas.width = rect.width;
    overlayCanvas.height = rect.height;
    
    // 确保画布样式匹配
    overlayCanvas.style.width = rect.width + 'px';
    overlayCanvas.style.height = rect.height + 'px';
    
    drawBooks();
}

// 绘制所有书籍
function drawBooks() {
    if (!imageLoaded) return;
    
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    
    Object.keys(books).forEach(key => {
        const book = books[key];
        const isSelected = key === currentBook;
        drawBookRect(book.position, isSelected, book.full_name);
    });
}

// 绘制书籍矩形（兼容旧格式）
function drawBookRect(position, isSelected, bookName) {
    if (!position || position.length !== 4) return;
    
    const [x, y, w, h] = position;
    
    // 使用归一化坐标（0-1）转换为画布坐标
    const px = x * overlayCanvas.width;
    const py = y * overlayCanvas.height;
    const pw = w * overlayCanvas.width;
    const ph = h * overlayCanvas.height;
    
    const rectX = px - pw / 2;
    const rectY = py - ph / 2;
    
    // 绘制矩形
    ctx.strokeStyle = isSelected ? '#2196f3' : '#4caf50';
    ctx.lineWidth = isSelected ? 3 : 2;
    ctx.strokeRect(rectX, rectY, pw, ph);
    
    // 绘制书名
    if (isSelected && bookName) {
        ctx.fillStyle = 'rgba(33, 150, 243, 0.2)';
        ctx.fillRect(rectX, rectY, pw, ph);
        
        ctx.fillStyle = '#2196f3';
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(bookName.substring(0, 30), px, py);
    }
}

// 绘制书籍多边形（四点模式）
function drawBookPolygon(points, isSelected, bookName) {
    if (!points || points.length !== 4) return;
    
    // 转换为画布坐标
    const canvasPoints = points.map(p => [
        p[0] * overlayCanvas.width,
        p[1] * overlayCanvas.height
    ]);
    
    // 绘制多边形
    ctx.beginPath();
    ctx.moveTo(canvasPoints[0][0], canvasPoints[0][1]);
    for (let i = 1; i < 4; i++) {
        ctx.lineTo(canvasPoints[i][0], canvasPoints[i][1]);
    }
    ctx.closePath();
    
    ctx.strokeStyle = isSelected ? '#2196f3' : '#4caf50';
    ctx.lineWidth = isSelected ? 3 : 2;
    ctx.stroke();
    
    // 绘制书名
    if (isSelected && bookName) {
        ctx.fillStyle = 'rgba(33, 150, 243, 0.2)';
        ctx.fill();
        
        // 计算中心点
        const centerX = canvasPoints.reduce((sum, p) => sum + p[0], 0) / 4;
        const centerY = canvasPoints.reduce((sum, p) => sum + p[1], 0) / 4;
        
        ctx.fillStyle = '#2196f3';
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(bookName.substring(0, 30), centerX, centerY);
    }
}

// 鼠标事件处理
function startDrag(e) {
    e.preventDefault(); // 防止默认行为
    e.stopPropagation(); // 阻止事件冒泡
    
    // 四点模式：点击选择书籍或设置点，不拖拽
    const rect = overlayCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 如果选中了书籍，检查是否点击在某个点上（用于编辑）
    if (currentBook) {
        const hitRadius = 15; // 点击检测半径
        let clickedPointIndex = -1;
        
        points.forEach((point, index) => {
            if (!point) return;
            const [px, py] = point;
            const canvasX = px * overlayCanvas.width;
            const canvasY = py * overlayCanvas.height;
            
            const distance = Math.sqrt(
                Math.pow(x - canvasX, 2) + Math.pow(y - canvasY, 2)
            );
            
            if (distance <= hitRadius) {
                clickedPointIndex = index;
            }
        });
        
        // 如果点击在点上，切换到该点进行编辑
        if (clickedPointIndex >= 0) {
            currentPointIndex = clickedPointIndex;
            updatePointsUI();
            drawBooks();
            return;
        }
    }
    
    // 检查是否点击在某个书籍矩形上
    const clickedBook = findBookAtPosition(x, y);
    if (clickedBook) {
        selectBook(clickedBook);
    }
}

function onDrag(e) {
    if (!isDragging || !currentBook) return;
    
    const rect = overlayCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const dx = (x - dragStart.x) / overlayCanvas.width;
    const dy = (y - dragStart.y) / overlayCanvas.height;
    
    const pos = books[currentBook].position;
    books[currentBook].position = [
        Math.max(0, Math.min(1, pos[0] + dx)),
        Math.max(0, Math.min(1, pos[1] + dy)),
        pos[2],
        pos[3]
    ];
    
    updateEditorUI();
    drawBooks();
    
    dragStart = { x, y };
}

function endDrag() {
    isDragging = false;
}

// 查找位置上的书籍
function findBookAtPosition(x, y) {
    const normalizedX = x / overlayCanvas.width;
    const normalizedY = y / overlayCanvas.height;
    
    for (const [key, book] of Object.entries(books)) {
        const [bx, by, bw, bh] = book.position;
        const rectX = bx - bw / 2;
        const rectY = by - bh / 2;
        
        if (normalizedX >= rectX && normalizedX <= rectX + bw &&
            normalizedY >= rectY && normalizedY <= rectY + bh) {
            return key;
        }
    }
    return null;
}

// 从输入框更新位置（已移除矩形模式）

// 更新设置
async function updateSettings() {
    const settings = {
        box_width: parseInt(document.getElementById('boxWidth').value) || 600,
        box_height: parseInt(document.getElementById('boxHeight').value) || 180,
        font_scale: parseFloat(document.getElementById('fontScale').value) || 1.5,
        font_thickness: parseInt(document.getElementById('fontThickness').value) || 3
    };
    
    try {
        await fetch('/api/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
    } catch (error) {
        console.error('更新设置失败:', error);
    }
}

// 更新书籍
async function updateBook() {
    if (!currentBook) {
        alert('请先选择一本书');
        return;
    }
    
    // 确保从输入框获取最新数据
    const book = books[currentBook];
    
    // 检查四点是否都已设置
    if (points.filter(p => p !== null).length !== 4) {
        alert('请先设置四个角点（点击图片上的四个位置）');
        return;
    }
    
    // 更新书名（从输入框读取）
    book.full_name = document.getElementById('bookName').value || book.full_name;
    
    console.log('准备保存:', {
        key: currentBook,
        points: points,
        full_name: book.full_name
    });
    
    try {
        const response = await fetch(`/api/books/${encodeURIComponent(currentBook)}`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                points: points,  // 保存四个点
                full_name: book.full_name
            })
        });
        
        // 检查响应类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('服务器返回的不是JSON:', text.substring(0, 200));
            alert('更新失败: 服务器返回格式错误\n请查看浏览器Console获取详细信息');
            return;
        }
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            alert('书籍更新成功！\n文件已保存到 book_database.py');
            console.log('保存成功:', result);
            
            // 重新加载书籍列表以获取最新数据
            await loadBooks();
            
            // 更新当前书籍的四点数据
            if (currentBook && books[currentBook]) {
                updateEditorUI();
            }
            
            // 重新绘制
            drawBooks();
        } else {
            console.error('保存失败:', result);
            const errorMsg = result.error || result.message || '未知错误';
            alert('更新失败: ' + errorMsg);
        }
    } catch (error) {
        console.error('更新书籍失败:', error);
        console.error('错误详情:', error.stack);
        alert('更新失败: ' + error.message + '\n请查看浏览器Console获取详细信息');
    }
}

// 取消编辑
function cancelEdit() {
    bookEditor.style.display = 'none';
    currentBook = null;
    document.querySelectorAll('.book-item').forEach(item => {
        item.classList.remove('active');
    });
    drawBooks();
}

// 保存所有更改
async function saveAll() {
    let saved = 0;
    let failed = 0;
    
    for (const [key, book] of Object.entries(books)) {
        try {
            const response = await fetch(`/api/books/${key}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    position: book.position,
                    full_name: book.full_name
                })
            });
            
            if (response.ok) {
                saved++;
            } else {
                failed++;
            }
        } catch (error) {
            failed++;
        }
    }
    
    alert(`保存完成！成功: ${saved}, 失败: ${failed}`);
}

// 预览效果（打开语音交互预览页面）
async function previewBook() {
    // 直接打开语音交互预览页面，不需要先选择书籍
    window.open('/preview', '_blank', 'fullscreen=yes');
}

// 切换编辑模式（已移除，只使用四点模式）

// 处理画布点击（四点模式）
function handleCanvasClick(e) {
    e.preventDefault(); // 防止默认行为
    e.stopPropagation(); // 阻止事件冒泡
    
    if (!currentBook) {
        console.log('未选择书籍，无法设置点');
        return;
    }
    
    const rect = overlayCanvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // 检查点击是否在画布范围内
    if (x < 0 || y < 0 || x > overlayCanvas.width || y > overlayCanvas.height) {
        console.log('点击超出画布范围');
        return;
    }
    
    const normalizedX = x / overlayCanvas.width;
    const normalizedY = y / overlayCanvas.height;
    
    console.log(`设置点 ${currentPointIndex + 1}: (${normalizedX.toFixed(4)}, ${normalizedY.toFixed(4)})`);
    
    // 设置当前点
    points[currentPointIndex] = [normalizedX, normalizedY];
    
    // 更新UI
    updatePointsUI();
    
    // 移动到下一个点
    currentPointIndex = (currentPointIndex + 1) % 4;
    
    drawBooks();
}

// 更新四点UI
function updatePointsUI() {
    for (let i = 0; i < 4; i++) {
        const point = points[i];
        if (point) {
            document.getElementById(`point${i + 1}X`).value = point[0].toFixed(4);
            document.getElementById(`point${i + 1}Y`).value = point[1].toFixed(4);
        } else {
            document.getElementById(`point${i + 1}X`).value = '';
            document.getElementById(`point${i + 1}Y`).value = '';
        }
    }
}

// 从输入框更新点
function updatePointFromInput(index) {
    const x = parseFloat(document.getElementById(`point${index + 1}X`).value) || 0;
    const y = parseFloat(document.getElementById(`point${index + 1}Y`).value) || 0;
    points[index] = [x, y];
    drawBooks();
}

// 将四点转换为矩形（已移除，只使用四点模式）

// 删除书籍
async function deleteBook() {
    if (!currentBook) return;
    
    if (!confirm(`确定要删除书籍 "${currentBook}" 吗？此操作不可撤销！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/books/${currentBook}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // 从本地数据中删除
            delete books[currentBook];
            renderBookList();
            cancelEdit();
            alert('书籍删除成功！');
        } else {
            alert('删除失败，请重试');
        }
    } catch (error) {
        console.error('删除书籍失败:', error);
        alert('删除失败: ' + error.message);
    }
}

// 绘制所有书籍
function drawBooks() {
    if (!imageLoaded || overlayCanvas.width === 0 || overlayCanvas.height === 0) {
        console.log('画布未准备好:', { imageLoaded, width: overlayCanvas.width, height: overlayCanvas.height });
        return;
    }
    
    // 清除画布
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    
    // 绘制所有书籍（使用四点或矩形）
    Object.keys(books).forEach(key => {
        const book = books[key];
        if (book && book.position) {
            const isSelected = key === currentBook;
            // 如果有四点数据，使用四点绘制；否则使用矩形
            if (book.points && Array.isArray(book.points) && book.points.length === 4) {
                // 确保points格式正确
                const normalizedPoints = book.points.map(p => {
                    if (Array.isArray(p)) {
                        return [p[0], p[1]];
                    } else {
                        return [p[0], p[1]];
                    }
                });
                drawBookPolygon(normalizedPoints, isSelected, book.full_name);
            } else {
                drawBookRect(book.position, isSelected, book.full_name);
            }
        }
    });
    
    // 如果选中了书籍，绘制四个编辑点
    if (currentBook) {
        drawPoints();
    }
    
    console.log('绘制完成，当前书籍:', currentBook, '书籍数量:', Object.keys(books).length);
    console.log('书籍数据示例:', books[Object.keys(books)[0]]);
}

// 绘制四个点
function drawPoints() {
    const pointRadius = 4; // 缩小点的半径（从8改为4）
    const hitRadius = 15; // 点击检测半径（扩大点击区域）
    
    points.forEach((point, index) => {
        if (!point) return;
        
        const [x, y] = point;
        const px = x * overlayCanvas.width;
        const py = y * overlayCanvas.height;
        
        // 绘制点（缩小）
        ctx.fillStyle = index === currentPointIndex ? '#f44336' : '#2196f3';
        ctx.beginPath();
        ctx.arc(px, py, pointRadius, 0, 2 * Math.PI);
        ctx.fill();
        
        // 绘制外圈（可选，让点更明显）
        ctx.strokeStyle = index === currentPointIndex ? '#f44336' : '#2196f3';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(px, py, pointRadius + 2, 0, 2 * Math.PI);
        ctx.stroke();
        
        // 绘制标签
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${index + 1}`, px, py);
        
        // 绘制连线
        if (index > 0 && points[index - 1]) {
            const prevPoint = points[index - 1];
            const prevX = prevPoint[0] * overlayCanvas.width;
            const prevY = prevPoint[1] * overlayCanvas.height;
            
            ctx.strokeStyle = '#2196f3';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(prevX, prevY);
            ctx.lineTo(px, py);
            ctx.stroke();
            ctx.setLineDash([]);
        }
    });
    
    // 如果四个点都有了，绘制闭合矩形
    if (points.filter(p => p !== null).length === 4) {
        ctx.strokeStyle = '#4caf50';
        ctx.lineWidth = 2;
        ctx.setLineDash([]);
        ctx.beginPath();
        points.forEach((point, index) => {
            const [x, y] = point;
            const px = x * overlayCanvas.width;
            const py = y * overlayCanvas.height;
            if (index === 0) {
                ctx.moveTo(px, py);
            } else {
                ctx.lineTo(px, py);
            }
        });
        ctx.closePath();
        ctx.stroke();
    }
}

// 启动应用
init();

