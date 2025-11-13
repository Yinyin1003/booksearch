"""
书籍数据库模块
存储书架上的书籍信息，包括书名和位置坐标
"""

class BookDatabase:
    def __init__(self):
        # 书籍数据库：书名 -> (x, y, width, height, shelf)
        # shelf: 0 = 上排, 1 = 下排
        # 坐标是相对于投影区域的归一化坐标 (0-1)
        self.books = {
            # 上排书籍 (shelf 0)
            "rethinking users": {
                "position": (0.2505, 0.3314, 0.0518, 0.0333),
                "shelf": 0,
                "full_name": "Rethinking Users: The Design Guide to User Ecosystem Thinking"
            },
            "design justice": {
                "position": (0.5493, 0.3739, 0.0247, 0.1852),
                "shelf": 0,
                "full_name": "DESIGN JUSTICE COMMUNITY-LED PRACTICES TO BUILD THE WORLDS WE NEED"
            },
            "do good design": {
                "position": (0.5271, 0.3920, 0.0149, 0.1695),
                "shelf": 0,
                "full_name": "do good design HOW DESIGNERS CAN CHANGE THE WORLD"
            },
            "the social life of information": {
                "position": (0.34, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "THE SOCIAL LIFE OF INFORMATION"
            },
            "lean impact": {
                "position": (0.46, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "LEAN IMPACT"
            },
            "convivial toolbox": {
                "position": (0.58, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "CONVIVIAL TOOLBOX"
            },
            "presentationzen": {
                "position": (0.70, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "presentationzen"
            },
            "good by design": {
                "position": (0.82, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "GOOD BY DESIGN"
            },
            "design by nature": {
                "position": (0.1, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "DESIGN BY NATURE"
            },
            "what's mine is yours": {
                "position": (0.22, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "WHAT'S MINE IS YOURS"
            },
            "life 3.0": {
                "position": (0.34, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "LIFE 3.0: BEING HUMAN IN THE AGE OF ARTIFICIAL INTELLIGENCE"
            },
            "iterate": {
                "position": (0.46, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "ITERATE"
            },
            "rules of play": {
                "position": (0.58, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "Rules of Play: Game Design Fundamentals"
            },
            "universal principles of design": {
                "position": (0.70, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "Universal Principles of Design"
            },
            "design by numbers": {
                "position": (0.82, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "Design By Numbers"
            },
            
            # 下排书籍 (shelf 1)
            "coffee lids": {
                "position": (0.15, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "COFFEE LIDS"
            },
            "code as creative medium": {
                "position": (0.27, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "Code as Creative Medium"
            },
            "graphic design rants and raves": {
                "position": (0.39, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "HELLER GRAPHIC DESIGN RANTS AND RAVES"
            },
            "teaching graphic design": {
                "position": (0.51, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "TEACHING GRAPHIC DESIGN"
            },
            "thinking with type": {
                "position": (0.63, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "thinking with type A CRITICAL GUIDE"
            },
            "brand bible": {
                "position": (0.75, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "BRAND BIBLE"
            },
            "branded interactions": {
                "position": (0.1, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "BRANDED INTERACTIONS"
            },
            "type & image": {
                "position": (0.22, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "TYPE & IMAGE"
            },
            "typography 34": {
                "position": (0.34, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "TYPOGRAPHY 34"
            },
            "guerrilla advertising": {
                "position": (0.46, 0.65, 0.12, 0.12),
                "shelf": 1,
                "full_name": "GUERRILLA ADVERTISING"
            },
        }
    
    def search_book(self, query):
        """
        搜索书籍（改进版：更精确的匹配）
        query: 用户输入的查询字符串
        返回: (book_key, book_info) 或 None
        """
        query_lower = query.lower().strip()
        
        # 移除常见的干扰词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'find', 'search', 'book', 'books'}
        query_words = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]
        query_clean = ' '.join(query_words)
        
        # 1. 精确匹配（最高优先级）
        if query_lower in self.books:
            return query_lower, self.books[query_lower]
        
        # 2. 清理后的精确匹配
        if query_clean and query_clean in self.books:
            return query_clean, self.books[query_clean]
        
        # 3. 检查关键词是否完全匹配书名关键词
        if query_words:
            for key, info in self.books.items():
                key_words = key.split()
                # 如果所有查询词都在书名关键词中
                if all(word in key_words for word in query_words):
                    return key, info
        
        # 4. 检查查询是否包含在书名关键词中（至少2个词匹配）
        if len(query_words) >= 2:
            for key, info in self.books.items():
                key_words = key.split()
                matched_words = sum(1 for word in query_words if word in key_words)
                if matched_words >= 2:  # 至少2个词匹配
                    return key, info
        
        # 5. 检查完整书名（至少2个词匹配）
        if len(query_words) >= 2:
            for key, info in self.books.items():
                full_name_lower = info["full_name"].lower()
                matched_words = sum(1 for word in query_words if word in full_name_lower)
                if matched_words >= 2:  # 至少2个词匹配
                    return key, info
        
        # 6. 单个关键词匹配（仅当查询只有一个词时）
        if len(query_words) == 1:
            query_word = query_words[0]
            # 只匹配长度>=4的词，避免误匹配
            if len(query_word) >= 4:
                for key, info in self.books.items():
                    if query_word in key or query_word in info["full_name"].lower():
                        return key, info
        
        return None, None
    
    def get_all_books(self):
        """获取所有书籍列表"""
        return self.books
    
    def add_book(self, key, position, shelf, full_name):
        """添加新书籍到数据库"""
        self.books[key] = {
            "position": position,
            "shelf": shelf,
            "full_name": full_name
        }

