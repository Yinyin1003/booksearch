// API 配置
// 如果部署到 GitHub Pages，需要设置后端 API 地址
const API_CONFIG = {
    // 检测是否在 GitHub Pages
    isGitHubPages: window.location.hostname.includes('github.io'),
    
    // 后端 API 地址（需要修改为你的实际后端地址）
    backendUrl: 'https://your-backend-url.railway.app',  // 修改这里！
    
    // 获取 API 基础 URL
    getBaseUrl: function() {
        if (this.isGitHubPages) {
            return this.backendUrl;
        }
        // 本地开发使用相对路径
        return '';
    }
};

// 创建带 API 基础 URL 的 fetch 函数
function apiFetch(url, options = {}) {
    const baseUrl = API_CONFIG.getBaseUrl();
    const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
    return fetch(fullUrl, options);
}

