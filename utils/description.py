import html

PLATFORM_EMOJI = {
    "Instagram": "💩",
    "Youtube": "🔴",
    "TikTok": "⚫️",
    "VK": "🔵"
}


def build_info(info: dict) -> str:
    platform = info.get('extractor_key') or 'НЕ УЗНАЛ ПЛАТФОРМУ'

    match platform:
        case "Youtube":
            username = info.get('uploader_id', '')[1:]
            profile_url = info.get("uploader_url")
            caption = info.get('fulltitle')
        case "TikTok":
            username = info.get('uploader', '')
            profile_url = info.get("uploader_url")
            caption = info.get('fulltitle')
        case "Instagram":
            username = info.get('channel', '')
            profile_url = f'https://www.instagram.com/{username}'
            caption = info.get('description', '')
        case _:
            username = info.get('title', '')[9:]
            profile_url = f"https://vk.com/{username}"
            caption = info.get('description', '')

    username = username or 'НЕ НАШЕЛ АВТОРА'
    caption = caption or 'НЕ НАШЕЛ ОПИСАНИЯ'
    profile_url = profile_url or '#'

    header = f"<b>{PLATFORM_EMOJI.get(platform, '')} {platform}</b>"
    blocks = [
        f'👤 <a href="{html.escape(profile_url)}">{html.escape(username)}</a>',
        f"💬 <code>{html.escape(caption)}</code>"
    ]

    formatted = header + "\n\n" + "\n\n".join(blocks)
    return formatted[:1024]
