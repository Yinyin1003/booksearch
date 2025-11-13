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
                "position": (0.5, 0.25, 0.15, 0.12),
                "shelf": 0,
                "full_name": "Rethinking Users: The Design Guide to User Ecosystem Thinking"
            },
            "design justice": {
                "position": (0.1, 0.25, 0.12, 0.12),
                "shelf": 0,
                "full_name": "DESIGN JUSTICE COMMUNITY-LED PRACTICES TO BUILD THE WORLDS WE NEED"
            },
            "do good design": {
                "position": (0.22, 0.25, 0.12, 0.12),
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
        搜索书籍
        query: 用户输入的查询字符串
        返回: (book_key, book_info) 或 None
        """
        query_lower = query.lower().strip()
        
        # 精确匹配
        if query_lower in self.books:
            return query_lower, self.books[query_lower]
        
        # 模糊匹配 - 检查书名是否包含查询
        for key, info in self.books.items():
            if query_lower in key or key in query_lower:
                return key, info
            # 检查完整书名
            if query_lower in info["full_name"].lower():
                return key, info
        
        # 更宽松的匹配 - 检查关键词
        query_words = query_lower.split()
        for key, info in self.books.items():
            key_words = key.split()
            full_name_words = info["full_name"].lower().split()
            
            # 如果查询中的任何词匹配书名中的词
            if any(word in key_words or word in full_name_words for word in query_words if len(word) > 2):
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

