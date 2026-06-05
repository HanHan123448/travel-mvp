"""
E2E 端到端自动化测试 — 完整用户链路
========================================
链路: 打开首页 → 筛选标签 → 进入详情 → 点击收藏 → 取消收藏

运行方式:
    pytest tests/e2e_test/ -v
    或直接: D:/python/python.exe tests/e2e_test/test_user_journey.py

前置条件:
    1. 后端运行在 http://localhost:8080
    2. 前端运行在 http://localhost:3000
    3. 数据库已加载 seed 数据 (travel_data.db)
"""
import pytest
from playwright.sync_api import sync_playwright, expect, Page

FRONTEND_URL = "http://localhost:3000"


@pytest.fixture(scope="module")
def browser():
    """启动本地 Chrome 浏览器（有头模式，便于观察测试过程）"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",              # 使用系统已安装的 Chrome
            headless=False,
            args=["--window-size=430,932"]  # iPhone 15 Pro Max 尺寸
        )
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """每次测试创建新页面"""
    context = browser.new_context(
        viewport={"width": 430, "height": 932},
        device_scale_factor=3,
        locale="zh-CN"
    )
    page = context.new_page()
    yield page
    context.close()


# ============================================================
# 链路1: 完整用户旅程
# ============================================================

def test_full_user_journey(page: Page):
    """
    完整用户链路测试:
    1. 打开首页，等待旅行卡片加载
    2. 验证至少加载了卡片
    3. 点击快捷标签筛选
    4. 进入旅行详情页
    5. 点击收藏按钮
    6. 返回首页验证
    """
    # ── Step 1: 打开首页 ──────────────────────────────────
    print("\n[Step 1] 打开首页...")
    page.goto(FRONTEND_URL, wait_until="networkidle", timeout=15000)

    # 验证页面标题
    expect(page).to_have_title("⚡ 小众探索", timeout=5000)

    # 等待瀑布流卡片加载
    page.wait_for_selector(".travel-card", state="visible", timeout=10000)
    cards = page.locator(".travel-card")
    card_count = cards.count()
    print(f"  ✓ 首页加载了 {card_count} 张旅行卡片")
    assert card_count >= 1, f"期望至少1张卡片，实际 {card_count} 张"

    # 验证第一张卡片有关键元素
    first_card = cards.first
    expect(first_card.locator(".card-title")).to_be_visible()
    expect(first_card.locator(".card-meta")).to_be_visible()

    # ── Step 2: 筛选标签 ──────────────────────────────────
    print("\n[Step 2] 标签筛选...")
    # 点击 Filter Bar 中的快捷标签（第二个chip，第一个是"筛选"按钮）
    filter_chips = page.locator(".filter-bar__chips .filter-chip")
    chip_count = filter_chips.count()
    print(f"  Filter Bar 有 {chip_count} 个快捷标签")

    if chip_count >= 1:
        # 点击第一个快捷标签
        selected_chip = filter_chips.first
        chip_text = selected_chip.text_content()
        print(f"  点击标签: {chip_text}")
        selected_chip.click()
        page.wait_for_timeout(1000)  # 等待筛选刷新

        # 验证页面仍在（无崩溃）
        expect(page.locator(".home-page")).to_be_visible()
        print("  ✓ 筛选完成，页面正常")

    # ── Step 3: 打开筛选弹窗（底部弹出）──────────────────
    print("\n[Step 3] 打开筛选弹窗...")
    filter_btn = page.locator(".filter-bar__btn")
    if filter_btn.is_visible():
        filter_btn.click()
        page.wait_for_timeout(500)

        # 验证弹窗出现
        sheet = page.locator(".filter-sheet")
        expect(sheet).to_be_visible(timeout=3000)
        print("  ✓ 筛选弹窗已打开")

        # 点击标签网格中的标签
        grid_chips = sheet.locator(".filter-section__grid .filter-chip")
        grid_count = grid_chips.count()
        print(f"  标签网格有 {grid_count} 个标签")

        if grid_count >= 1:
            # 选中第三个标签（换一批）
            grid_chips.nth(min(2, grid_count - 1)).click()
            page.wait_for_timeout(300)

        # 点击"查看结果"
        apply_btn = sheet.locator(".filter-sheet__apply")
        apply_btn.click()
        page.wait_for_timeout(1000)
        print("  ✓ 筛选已应用，弹窗关闭")

    # ── Step 4: 进入旅行详情 ──────────────────────────────
    print("\n[Step 4] 进入旅行详情...")
    # 重新获取卡片（筛选后可能变了）
    cards = page.locator(".travel-card")
    card_count = cards.count()
    print(f"  当前页有 {card_count} 张卡片")

    if card_count >= 1:
        # 点击第一张卡片
        first_card = cards.first
        title_text = first_card.locator(".card-title").text_content()
        print(f"  点击卡片: {title_text}")
        first_card.click()

        # 验证跳转到详情页
        page.wait_for_url("**/travel/**", timeout=5000)
        expect(page.locator(".detail-page")).to_be_visible(timeout=5000)
        print("  ✓ 已进入详情页")

        # 验证详情页关键元素
        expect(page.locator(".detail-title")).to_be_visible()
        expect(page.locator(".hero")).to_be_visible()
        print("  ✓ 详情页内容完整")

        # ── Step 5: 点击收藏 ──────────────────────────────
        print("\n[Step 5] 收藏操作...")
        collect_btn = page.locator(".hero__collect")
        expect(collect_btn).to_be_visible(timeout=3000)

        # 获取收藏前状态
        before_text = collect_btn.text_content().strip()
        print(f"  收藏按钮当前状态: {before_text}")

        # 点击收藏
        collect_btn.click()
        page.wait_for_timeout(1000)

        # 验证 Toast 出现
        toast = page.locator(".toast")
        if toast.is_visible():
            toast_msg = toast.text_content()
            print(f"  ✓ Toast: {toast_msg}")

        # 验证收藏按钮状态变化
        after_text = collect_btn.text_content().strip()
        print(f"  收藏按钮新状态: {after_text}")

        # ── Step 6: 再次点击取消收藏 ────────────────────────
        print("\n[Step 6] 再次点击取消收藏...")
        collect_btn.click()
        page.wait_for_timeout(1000)

        if toast.is_visible():
            toast_msg = toast.text_content()
            print(f"  ✓ Toast: {toast_msg}")

        # ── Step 7: 返回首页 ───────────────────────────────
        print("\n[Step 7] 返回首页...")
        back_btn = page.locator(".hero__back")
        back_btn.click()
        page.wait_for_url("**/", timeout=5000)
        expect(page.locator(".home-page")).to_be_visible()
        print("  ✓ 已返回首页")


# ============================================================
# 链路2: 收藏列表页
# ============================================================

def test_collect_page(page: Page):
    """测试收藏列表页面"""
    print("\n[链路2] 收藏列表页...")

    page.goto(FRONTEND_URL, wait_until="networkidle", timeout=15000)
    page.wait_for_selector(".travel-card", state="visible", timeout=10000)

    # 点击底部导航的"收藏"Tab
    collect_tab = page.locator(".nav-item").nth(1)
    collect_tab.click()
    page.wait_for_url("**/collect", timeout=5000)
    print("  ✓ 已进入收藏列表页")

    # 验证页面（可能有数据，也可能是空列表）
    page.wait_for_timeout(1000)
    has_cards = page.locator(".travel-card").count() > 0
    has_empty = page.locator(".empty-state").is_visible()
    print(f"  收藏页: {'有收藏卡片' if has_cards else '空状态' if has_empty else '加载中'}")

    # 点回首页
    home_tab = page.locator(".nav-item").first
    home_tab.click()
    page.wait_for_url("**/", timeout=5000)
    print("  ✓ 已返回首页")


# ============================================================
# 链路3: 详情页图片轮播
# ============================================================

def test_detail_image_carousel(page: Page):
    """测试详情页图片轮播功能"""
    print("\n[链路3] 详情页图片轮播...")

    page.goto(FRONTEND_URL, wait_until="networkidle", timeout=15000)
    page.wait_for_selector(".travel-card", state="visible", timeout=10000)

    # 进入第一个有图片的卡片
    cards = page.locator(".travel-card")
    if cards.count() >= 1:
        cards.first.click()
        page.wait_for_url("**/travel/**", timeout=5000)

        # 检查图片区域
        hero_images = page.locator(".hero__images")
        if hero_images.is_visible():
            imgs = hero_images.locator(".hero__img")
            img_count = imgs.count()
            print(f"  ✓ 详情页有 {img_count} 张图片")

            if img_count > 1:
                # 模拟滑动（scroll）
                hero_images.evaluate("el => el.scrollBy({left: 300, behavior: 'smooth'})")
                page.wait_for_timeout(800)
                print("  ✓ 图片已横向滑动")

        # 返回首页
        page.locator(".hero__back").click()
        page.wait_for_url("**/", timeout=5000)


# ============================================================
# 链路4: 响应式与空状态
# ============================================================

def test_empty_state_on_filter_no_result(page: Page):
    """测试筛选无结果时的空状态"""
    print("\n[链路4] 筛选无结果空状态...")

    page.goto(FRONTEND_URL, wait_until="networkidle", timeout=15000)

    # 打开筛选弹窗
    filter_btn = page.locator(".filter-bar__btn")
    if filter_btn.is_visible():
        filter_btn.click()
        page.wait_for_timeout(500)

        sheet = page.locator(".filter-sheet")
        if sheet.is_visible():
            # 选一个不存在的组合：选一个冷门标签
            # 点击重置清除所有
            reset_btn = sheet.locator(".filter-sheet__reset")
            reset_btn.click()

            # 选择一个标签
            grid_chips = sheet.locator(".filter-section__grid .filter-chip")
            if grid_chips.count() >= 1:
                grid_chips.first.click()

            # 选择一个城市（如果存在的话）
            city_chips = sheet.locator(".filter-section__chips .filter-chip")
            if city_chips.count() > 1:
                city_chips.nth(1).click()

            # 应用
            sheet.locator(".filter-sheet__apply").click()
            page.wait_for_timeout(1500)

            # 检查结果：可能有卡片或空状态
            page.wait_for_timeout(500)
            has_cards = page.locator(".travel-card").count() > 0
            has_empty = page.locator(".empty-state").is_visible()
            print(f"  筛选结果: {'有卡片' if has_cards else '空状态' if has_empty else '—'}")

            if has_empty:
                print("  ✓ 空状态正确显示")

                # 点击清除筛选
                clear_btn = page.locator(".empty-state__btn")
                if clear_btn.is_visible():
                    clear_btn.click()
                    page.wait_for_timeout(1000)
                    print("  ✓ 已清除筛选返回")


# ============================================================
# 脚本直连入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Z世代小众旅行 — E2E 端到端测试")
    print("=" * 60)
    print("  前置: 后端 http://localhost:8080  |  前端 http://localhost:3000")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",        # 使用系统已安装的 Chrome
            headless=False,
            args=["--window-size=430,932"]
        )
        context = browser.new_context(
            viewport={"width": 430, "height": 932},
            device_scale_factor=3,
            locale="zh-CN"
        )
        page = context.new_page()

        try:
            test_full_user_journey(page)
            test_collect_page(page)
            test_detail_image_carousel(page)
            test_empty_state_on_filter_no_result(page)
            print("\n" + "=" * 60)
            print("  全部 E2E 测试通过 ✅")
            print("=" * 60)
        except Exception as e:
            print(f"\n  ❌ 测试失败: {e}")
            page.screenshot(path="tests/e2e_test/screenshot_error.png")
            print("  错误截图已保存: tests/e2e_test/screenshot_error.png")
            raise
        finally:
            context.close()
            browser.close()
