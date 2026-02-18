"""
增強 API 測試套件
test_enhanced_api.py | @理樞 | 2026-02-18
"""
import sys
sys.path.insert(0, '.')

def test_classical_enhancement():
    """測試 classical_enhancement 模組"""
    print("=== 測試 classical_enhancement ===")
    
    from classical_enhancement import (
        SHISHEN_GLOSSARY, BAGUA_GLOSSARY, GEJU_GLOSSARY, GONGWEI_GLOSSARY,
        get_shishen_glossary, get_bagua_glossary, get_geju_glossary, get_gongwei_glossary
    )
    
    # 計數驗證
    assert len(SHISHEN_GLOSSARY) == 10, f"十神數量錯誤: {len(SHISHEN_GLOSSARY)}"
    assert len(BAGUA_GLOSSARY) == 8, f"八卦數量錯誤: {len(BAGUA_GLOSSARY)}"
    assert len(GEJU_GLOSSARY) == 8, f"格局數量錯誤: {len(GEJU_GLOSSARY)}"
    assert len(GONGWEI_GLOSSARY) == 12, f"宮位數量錯誤: {len(GONGWEI_GLOSSARY)}"
    
    # 十神測試
    g = get_shishen_glossary("七殺")
    assert g is not None, "七殺查詢失敗"
    assert "白話" in g["vernacular"] or len(g["vernacular"]) > 0, "七殺白話為空"
    
    # 八卦測試
    g = get_bagua_glossary("乾")
    assert g is not None, "乾卦查詢失敗"
    assert g["symbol"] == "☰", f"乾卦符號錯誤: {g['symbol']}"
    
    # 格局測試
    g = get_geju_glossary("傷官格")
    assert g is not None, "傷官格查詢失敗"
    assert "才華" in g["vernacular"], f"傷官格白話錯誤: {g['vernacular']}"
    
    # 宮位測試
    g = get_gongwei_glossary("命宮")
    assert g is not None, "命宮查詢失敗"
    assert "核心" in g["field_role"], f"命宮場論錯誤: {g['field_role']}"
    
    print("  ✅ 十神: 10個")
    print("  ✅ 八卦: 8個")
    print("  ✅ 格局: 8個")
    print("  ✅ 宮位: 12個")
    return True

def test_methodology_core():
    """測試 methodology_core 模組"""
    print("\n=== 測試 methodology_core ===")
    
    from methodology_core import (
        ZHIMING_REVELATION, XTF_DAO, FIELD_THEORY_INTERPERSONAL,
        BEIDOU_PRINCIPLES, get_full_methodology
    )
    
    # 揭示層數驗證
    assert len(ZHIMING_REVELATION["layers"]) == 10, "揭示層數錯誤"
    
    # XTF 驗證
    assert len(XTF_DAO["cycle"]) == 3, "XTF週期數錯誤"
    
    # 場論驗證
    assert FIELD_THEORY_INTERPERSONAL["version"] == "v3.6", "場論版本錯誤"
    assert len(FIELD_THEORY_INTERPERSONAL["four_states"]) == 4, "四態數量錯誤"
    
    # 原則驗證
    assert len(BEIDOU_PRINCIPLES) >= 4, "原則數量不足"
    
    # 完整方法論
    full = get_full_methodology()
    assert "revelation" in full, "缺少揭示"
    assert "xtf_dao" in full, "缺少XTF"
    
    print("  ✅ 揭示: 10層")
    print("  ✅ XTF: 3階段")
    print("  ✅ 場論: v3.6")
    print("  ✅ 原則: 5條")
    return True

def test_frontend_components():
    """測試 frontend_components 模組"""
    print("\n=== 測試 frontend_components ===")
    
    from frontend_components import (
        generate_shishen_card_html, generate_bagua_card_html,
        generate_all_shishen_cards, format_for_frontend
    )
    
    # HTML 生成測試
    html = generate_shishen_card_html("正印")
    assert "正印" in html, "十神卡片生成失敗"
    assert "shishen-card" in html, "缺少卡片類名"
    
    html = generate_bagua_card_html("乾")
    assert "乾" in html, "八卦卡片生成失敗"
    assert "☰" in html, "缺少卦符號"
    
    # 批量生成測試
    all_cards = generate_all_shishen_cards()
    assert "shishen-grid" in all_cards, "網格生成失敗"
    
    # 前端數據測試
    data = format_for_frontend("shishen")
    assert data["count"] == 10, f"十神數量錯誤: {data['count']}"
    assert len(data["items"]) == 10, "十神項目數錯誤"
    
    print("  ✅ HTML卡片生成")
    print("  ✅ 批量生成")
    print("  ✅ 前端數據格式")
    return True

def test_pdf_vernacular():
    """測試 pdf_vernacular_section 模組"""
    print("\n=== 測試 pdf_vernacular_section ===")
    
    from pdf_vernacular_section import (
        create_shishen_table_data, create_geju_data,
        create_gongwei_table_data, get_vernacular_report_data
    )
    
    # 十神表格
    data = create_shishen_table_data(["正印", "七殺"])
    assert len(data) == 3, f"十神表格行數錯誤: {len(data)}"  # 標題 + 2行
    
    # 格局數據
    data = create_geju_data("傷官格")
    assert data["name"] == "傷官格", "格局名稱錯誤"
    
    # 宮位表格
    data = create_gongwei_table_data(["命宮", "夫妻宮"])
    assert len(data) == 3, f"宮位表格行數錯誤: {len(data)}"
    
    # 完整報告數據
    report = get_vernacular_report_data(
        shishen_list=["正印"],
        geju_name="正官格",
        gongwei_list=["命宮"]
    )
    assert "methodology" in report, "缺少方法論"
    assert len(report["shishen"]) > 0, "缺少十神"
    
    print("  ✅ 十神表格數據")
    print("  ✅ 格局數據")
    print("  ✅ 宮位表格數據")
    print("  ✅ 完整報告數據")
    return True

def run_all_tests():
    """執行所有測試"""
    print("=" * 50)
    print("  北斗命數 增強 API 測試套件")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(("classical_enhancement", test_classical_enhancement()))
    except Exception as e:
        print(f"  ❌ classical_enhancement: {e}")
        results.append(("classical_enhancement", False))
    
    try:
        results.append(("methodology_core", test_methodology_core()))
    except Exception as e:
        print(f"  ❌ methodology_core: {e}")
        results.append(("methodology_core", False))
    
    try:
        results.append(("frontend_components", test_frontend_components()))
    except Exception as e:
        print(f"  ❌ frontend_components: {e}")
        results.append(("frontend_components", False))
    
    try:
        results.append(("pdf_vernacular_section", test_pdf_vernacular()))
    except Exception as e:
        print(f"  ❌ pdf_vernacular_section: {e}")
        results.append(("pdf_vernacular_section", False))
    
    # 統計結果
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"  測試結果: {passed}/{total} 通過")
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
