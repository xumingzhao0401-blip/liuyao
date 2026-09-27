"""
六爻基础常量与中式木块算筹视觉元数据定义
遵循《火珠林》、《增删卜易》象数体系
"""

# 爻位标准称谓（由下至上，索引 0 到 5 对应初爻至上爻）
YIN_YANG_NAMES = {
    "yang": ["初九", "九二", "九三", "九四", "九五", "上九"],
    "yin":  ["初六", "六二", "六三", "六四", "六五", "上六"]
}

# 掷铜钱数值到爻象与木块形态的映射 (字=2, 背=3)
COIN_SUM_MAP = {
    6: {
        "nature": "old_yin",
        "name": "老阴（交）",
        "symbol_original": "--",
        "symbol_mark": "×",
        "is_moving": True,
        "original_bit": 0,           # 本卦为阴 (左右两截断开木块)
        "transformed_bit": 1,        # 变卦转阳 (左右木块向中拼合为一整块)
        "wood_type": "split_wood",   # 前端渲染：双段木块
        "anim_type": "wood_merge",   # 动画：左右合拢
        "mark_color": "#C9372E"      # 朱砂印记色
    },
    7: {
        "nature": "young_yang",
        "name": "少阳（单）",
        "symbol_original": "—",
        "symbol_mark": " ",
        "is_moving": False,
        "original_bit": 1,           # 阳爻 (单根通长整木块)
        "transformed_bit": 1,
        "wood_type": "solid_wood",   # 前端渲染：整根木块
        "anim_type": "none",
        "mark_color": None
    },
    8: {
        "nature": "young_yin",
        "name": "少阴（拆）",
        "symbol_original": "--",
        "symbol_mark": " ",
        "is_moving": False,
        "original_bit": 0,           # 阴爻 (左右两截断开木块)
        "transformed_bit": 0,
        "wood_type": "split_wood",   # 前端渲染：双段木块
        "anim_type": "none",
        "mark_color": None
    },
    9: {
        "nature": "old_yang",
        "name": "老阳（重）",
        "symbol_original": "—",
        "symbol_mark": "○",
        "is_moving": True,
        "original_bit": 1,           # 本卦为阳 (单根通长整木块)
        "transformed_bit": 0,        # 变卦转阴 (整木从中裂开滑向两侧)
        "wood_type": "solid_wood",   # 前端渲染：整根木块
        "anim_type": "wood_split",   # 动画：从中分裂
        "mark_color": "#C9372E"      # 朱砂印记色
    }
}
