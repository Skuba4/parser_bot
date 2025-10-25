from urllib.parse import urlparse

ALLOWED_DOMAINS = [
    "vk.com",
    "vkvideo.ru",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "instagram.com"
]


def link_checking(link: str) -> bool:
    netloc = urlparse(link).netloc.lower()
    path = urlparse(link).path

    match netloc:
        case d if "youtube.com" in d or "youtu.be" in d:
            return "shorts" in path
        case d if any(d.endswith(domain) for domain in ALLOWED_DOMAINS):
            return True
        case _:
            return False

# проверка на суточный лимит скачиваний
# проверка на семейную группу или приобретенная подписка