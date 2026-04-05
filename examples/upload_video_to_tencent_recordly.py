import asyncio
from pathlib import Path

from conf import BASE_DIR
from uploader.tencent_uploader.main import TencentVideo, weixin_setup
from utils.constant import TencentZoneTypes


MATERIAL_DIR = Path(
    "/Users/koffu/Pictures/4-Recordly/output/2026-04-05_02-claude-infograph-prompt/字幕/3_输出"
)
VIDEO_FILE = MATERIAL_DIR / "02-claude-infograph-prompt_cut_字幕.mp4"
LANDSCAPE_COVER_FILE = MATERIAL_DIR / "cover-4_3-1440x1080.png"
PORTRAIT_COVER_FILE = MATERIAL_DIR / "cover-3_4-1080x1440.png"
ACCOUNT_FILE = Path(BASE_DIR / "cookies" / "tencent_uploader" / "creator.json")

TITLE = "这种很火的 Claude 风格信息图，原来是这样生成的"
TAGS = ["AI绘图", "Claude", "Gemini", "提示词", "信息图", "内容创作", "自媒体运营"]
CATEGORY = TencentZoneTypes.TECHNOLOGY.value


def extract_recommended_copy(markdown_path: Path) -> str:
    content = markdown_path.read_text(encoding="utf-8")
    marker = "### 推荐文案"
    if marker not in content:
        return ""

    after_marker = content.split(marker, 1)[1]
    lines: list[str] = []
    for raw_line in after_marker.splitlines()[1:]:
        line = raw_line.rstrip()
        if line.startswith("### ") and line.strip() != marker:
            break
        if line.startswith("### 推荐标签"):
            break
        lines.append(line)

    return "\n".join(lines).strip()


DESCRIPTION = extract_recommended_copy(MATERIAL_DIR / "short-video-copy.md")


async def main() -> None:
    ACCOUNT_FILE.parent.mkdir(parents=True, exist_ok=True)
    await weixin_setup(str(ACCOUNT_FILE), handle=True)
    uploader = TencentVideo(
        title=TITLE,
        file_path=str(VIDEO_FILE),
        tags=TAGS,
        publish_date=0,
        account_file=str(ACCOUNT_FILE),
        category=CATEGORY,
        is_draft=False,
        cover_landscape_path=str(LANDSCAPE_COVER_FILE) if LANDSCAPE_COVER_FILE.exists() else None,
        cover_portrait_path=str(PORTRAIT_COVER_FILE) if PORTRAIT_COVER_FILE.exists() else None,
        description=DESCRIPTION,
    )
    await uploader.main()


if __name__ == "__main__":
    asyncio.run(main())
