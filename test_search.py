#!/usr/bin/env python3
"""
测试搜索功能
帮助诊断语音识别和搜索匹配问题
"""

from book_database import BookDatabase

def test_search():
    """测试搜索功能"""
    db = BookDatabase()
    
    print("="*60)
    print("书籍搜索测试工具")
    print("="*60)
    
    # 测试用例
    test_queries = [
        "rethinking users",
        "rethinking",
        "lean impact",
        "lean",
        "coffee lids",
        "coffee",
        "design justice",
        "design",
        "the social life of information",
        "social life",
    ]
    
    print("\n测试搜索查询:")
    print("-"*60)
    
    for query in test_queries:
        book_key, book_info = db.search_book(query)
        if book_info:
            print(f"✅ '{query}' -> {book_info['full_name']}")
            print(f"   匹配关键词: {book_key}")
        else:
            print(f"❌ '{query}' -> 未找到")
    
    print("\n" + "="*60)
    print("所有可用的书籍关键词:")
    print("="*60)
    all_books = db.get_all_books()
    for i, key in enumerate(sorted(all_books.keys()), 1):
        info = all_books[key]
        print(f"{i:2d}. {key:30s} -> {info['full_name']}")
    
    print("\n" + "="*60)
    print("交互式测试（输入书名进行测试，输入 'quit' 退出）:")
    print("="*60)
    
    while True:
        try:
            query = input("\n请输入查询: ").strip()
            if query.lower() == 'quit':
                break
            
            if query:
                book_key, book_info = db.search_book(query)
                if book_info:
                    print(f"✅ 找到: {book_info['full_name']}")
                    print(f"   匹配关键词: {book_key}")
                    print(f"   位置: {book_info['position']}")
                else:
                    print(f"❌ 未找到匹配的书籍")
                    print("   提示: 尝试使用更完整的关键词")
        except KeyboardInterrupt:
            break
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_search()

