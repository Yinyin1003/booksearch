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
                "position": (0.1794, 0.3617, 0.2181, 0.2169),
                "shelf": 0,
                "full_name": "Rethinking Users: The Design Guide to User Ecosystem Thinking"
            },
            "design justice": {
                "position": (0.5020, 0.3672, 0.0297, 0.2245),
                "shelf": 0,
                "full_name": "DESIGN JUSTICE COMMUNITY-LED PRACTICES TO BUILD THE WORLDS WE NEED"
            },
            "do good design": {
                "position": (0.4707, 0.3792, 0.0235, 0.1946),
                "shelf": 0,
                "full_name": "do good design HOW DESIGNERS CAN CHANGE THE WORLD"
            },
            "the social life of information": {
                "position": (0.4315, 0.3746, 0.0417, 0.2039),
                "shelf": 0,
                "full_name": "THE SOCIAL LIFE OF INFORMATION"
            },
            "lean impact": {
                "position": (0.3983, 0.3650, 0.0387, 0.2165),
                "points": [(0.3829, 0.2582), (0.4177, 0.2567), (0.4048, 0.4725), (0.3790, 0.4732)],
                "shelf": 0,
                "full_name": "LEAN IMPACT"
            },
            "convivial toolbox": {
                "position": (0.5709, 0.3653, 0.0347, 0.2269),
                "shelf": 0,
                "full_name": "CONVIVIAL TOOLBOX"
            },
            "presentationzen": {
                "position": (0.5933, 0.3657, 0.0238, 0.2314),
                "points": [(0.5913, 0.2537), (0.6052, 0.2500), (0.5982, 0.4784), (0.5813, 0.4814)],
                "shelf": 0,
                "full_name": "presentationzen"
            },
            "good by design": {
                "position": (0.5367, 0.3642, 0.0337, 0.2292),
                "points": [(0.5536, 0.2496), (0.5516, 0.4773), (0.5198, 0.4788), (0.5228, 0.2496)],
                "shelf": 0,
                "full_name": "GOOD BY DESIGN"
            },
            "what's mine is yours": {
                "position": (0.6796, 0.3642, 0.0456, 0.2173),
                "shelf": 0,
                "full_name": "WHAT'S MINE IS YOURS"
            },
            "life 3.0": {
                "position": (0.7078, 0.3653, 0.0466, 0.2165),
                "shelf": 0,
                "full_name": "LIFE 3.0: BEING HUMAN IN THE AGE OF ARTIFICIAL INTELLIGENCE"
            },
            "iterate": {
                "position": (0.7341, 0.3631, 0.0536, 0.2188),
                "points": [(0.6845, 0.2571), (0.7063, 0.2571), (0.7312, 0.4736), (0.7083, 0.4728)],
                "shelf": 0,
                "full_name": "ITERATE"
            },
            "rules of play": {
                "position": (0.7728, 0.3642, 0.0655, 0.2195),
                "points": [(0.7401, 0.2574), (0.7837, 0.2545), (0.8056, 0.4732), (0.7679, 0.4740)],
                "shelf": 0,
                "full_name": "Rules of Play: Game Design Fundamentals"
            },
            "universal principles of design": {
                "position": (0.8795, 0.3527, 0.0288, 0.2388),
                "shelf": 0,
                "full_name": "Universal Principles of Design"
            },
            "design by numbers": {
                "position": (0.8562, 0.3574, 0.0256, 0.2332),
                "shelf": 0,
                "full_name": "Design By Numbers"
            },
            
            # 下排书籍 (shelf 1)
            "coffee lids": {
                "position": (0.3110, 0.7917, 0.2093, 0.0670),
                "points": [(0.2063, 0.7716), (0.2371, 0.8251), (0.4157, 0.8110), (0.3720, 0.7582)],
                "shelf": 1,
                "full_name": "COFFEE LIDS"
            },
            "code as creative medium": {
                "position": (0.8517, 0.7303, 0.0625, 0.0513),
                "shelf": 1,
                "full_name": "Code as Creative Medium"
            },
            "graphic design rants and raves": {
                "position": (0.5431, 0.7249, 0.0447, 0.2058),
                "points": [(0.8264, 0.7046), (0.8829, 0.7046), (0.8631, 0.7552), (0.8204, 0.7560)],
                "shelf": 1,
                "full_name": "HELLER GRAPHIC DESIGN RANTS AND RAVES"
            },
            "teaching graphic design": {
                "position": (0.5665, 0.7251, 0.0476, 0.2039),
                "shelf": 1,
                "full_name": "TEACHING GRAPHIC DESIGN"
            },
            "thinking with type": {
                "position": (0.5134, 0.7335, 0.0407, 0.1961),
                "shelf": 1,
                "full_name": "thinking with type A CRITICAL GUIDE"
            },
            "brand bible": {
                "position": (0.5918, 0.7143, 0.0486, 0.2143),
                "points": [(0.5179, 0.6354), (0.5337, 0.6373), (0.5099, 0.8296), (0.4930, 0.8315)],
                "shelf": 1,
                "full_name": "BRAND BIBLE"
            },
            "branded interactions": {
                "position": (0.6245, 0.7013, 0.0685, 0.2374),
                "points": [(0.6200, 0.5833), (0.6587, 0.5826), (0.6220, 0.8199), (0.5903, 0.8192)],
                "shelf": 1,
                "full_name": "BRANDED INTERACTIONS"
            },
            "type & image": {
                "position": (0.6548, 0.6953, 0.0595, 0.2500),
                "points": [(0.6637, 0.5703), (0.6845, 0.5703), (0.6448, 0.8188), (0.6250, 0.8203)],
                "shelf": 1,
                "full_name": "TYPE & IMAGE"
            },
            "typography 34": {
                "position": (0.6835, 0.6908, 0.0694, 0.2582),
                "shelf": 1,
                "full_name": "TYPOGRAPHY 34"
            },
            "guerrilla advertising": {
                "position": (0.7168, 0.6866, 0.0724, 0.2682),
                "points": [(0.6895, 0.5625), (0.7182, 0.5617), (0.6746, 0.8170), (0.6488, 0.8199)],
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

