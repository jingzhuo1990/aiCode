#!/usr/bin/env python
"""测试 RAG 记忆系统"""

def test_rag_basic():
    """基础测试"""
    print("=" * 60)
    print("测试 1: 检查依赖")
    print("=" * 60)

    try:
        import faiss
        import sentence_transformers
        print("✓ FAISS 已安装")
        print("✓ Sentence Transformers 已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("\n请运行: pip install faiss-cpu sentence-transformers")
        return False

    print("\n" + "=" * 60)
    print("测试 2: 初始化 RAG Memory")
    print("=" * 60)

    try:
        from aicode.memory.rag_memory import RAGMemory
        rag = RAGMemory(storage_dir=".test_memory")
        print(f"✓ RAG Memory 初始化成功")
        print(f"  - Embedding 维度: {rag.embedding_dim}")
        print(f"  - 模型: all-MiniLM-L6-v2")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("测试 3: 添加记忆")
    print("=" * 60)

    memories = [
        {
            "key": "error_handling",
            "content": "使用 try-except 捕获异常，记录到日志系统，返回用户友好的错误信息",
            "metadata": {"category": "patterns", "importance": 8}
        },
        {
            "key": "exception_best_practice",
            "content": "捕获特定异常类型，避免使用裸 except，使用 finally 清理资源",
            "metadata": {"category": "patterns", "importance": 8}
        },
        {
            "key": "logging_errors",
            "content": "使用 logging.exception() 记录错误堆栈信息，便于后续调试和分析",
            "metadata": {"category": "patterns", "importance": 7}
        },
        {
            "key": "jwt_authentication",
            "content": "使用 JWT token 实现无状态认证，token 存储在 HTTP-only cookie 中",
            "metadata": {"category": "patterns", "importance": 9}
        },
        {
            "key": "database_connection",
            "content": "使用连接池管理数据库连接，设置合理的超时和最大连接数",
            "metadata": {"category": "patterns", "importance": 8}
        }
    ]

    for mem in memories:
        rag.add(mem["key"], mem["content"], mem["metadata"])
        print(f"✓ 添加: {mem['key']}")

    print(f"\n总共添加了 {len(memories)} 条记忆")

    print("\n" + "=" * 60)
    print("测试 4: 语义搜索")
    print("=" * 60)

    test_queries = [
        ("如何处理错误", "应该找到 error_handling, exception_best_practice, logging_errors"),
        ("用户认证怎么做", "应该找到 jwt_authentication"),
        ("数据库连接管理", "应该找到 database_connection"),
    ]

    for query, expected in test_queries:
        print(f"\n查询: '{query}'")
        print(f"期望: {expected}")
        print("-" * 60)

        results = rag.semantic_search(query, top_k=3)

        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['key']}")
                print(f"   相似度: {result['score']:.3f}")
                print(f"   内容: {result['content'][:60]}...")
        else:
            print("  未找到结果")

    print("\n" + "=" * 60)
    print("测试 5: 统计信息")
    print("=" * 60)

    stats = rag.get_stats()
    print(f"总记忆数: {stats['total_memories']}")
    print(f"分类分布: {stats['categories']}")
    print(f"Embedding 维度: {stats['embedding_dim']}")

    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)

    # 清理测试数据
    import shutil
    try:
        shutil.rmtree(".test_memory")
        print("\n✓ 清理测试数据完成")
    except:
        pass

    return True


if __name__ == "__main__":
    print("\n🧠 RAG 记忆系统测试\n")

    success = test_rag_basic()

    if success:
        print("\n" + "=" * 60)
        print("🎉 测试成功！")
        print("=" * 60)
        print("\n下一步:")
        print("1. pip install faiss-cpu sentence-transformers")
        print("2. python -m aicode.cli_agent remember 'key' 'value' --use-rag")
        print("3. python -m aicode.cli_agent semantic-search '查询'")
    else:
        print("\n" + "=" * 60)
        print("⚠️  测试失败")
        print("=" * 60)
        print("\n请先安装依赖:")
        print("pip install faiss-cpu sentence-transformers")
