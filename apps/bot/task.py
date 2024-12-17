import aiohttp
import asyncio
from asgiref.sync import async_to_sync
from celery import shared_task
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from apps.bot.models import Detection, CarListing
from apps.bot.utils.notifcation import notify_user
import logging
import re

logger = logging.getLogger(__name__)
BASE_URL = "https://avtoelon.uz/avto/"


def clean_url(base_url, relative_url):
    if not relative_url:
        return None
    full_url = urljoin(base_url, relative_url.lstrip("/"))
    return full_url if "avtoelon.uz" in full_url else None


def format_url_for_user(url):
    return url.replace("/avto/", "/") if url else url


async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching {url}: {e}")
            return None


async def parse_listing(listing_html):
    details = {}
    title_elem = listing_html.select_one(".a-el-info-title a")
    if title_elem:
        details["URL"] = clean_url(BASE_URL, title_elem.get("href"))
        details["Title"] = title_elem.get_text(strip=True)

    image_elem = listing_html.select_one(".list-item .a-el-image img")
    if image_elem:
        image_url = image_elem.get("src")
        details["Image"] = clean_url(BASE_URL, image_url) if image_url else None

    price = listing_html.select_one(".price")
    if price:
        details["Price"] = price.get_text(strip=True)

    description = listing_html.select_one(".desc")
    if description:
        mileage_match = re.search(r"(\d[\d\s]*) км", description.get_text(strip=True))
        if mileage_match:
            details["Mileage"] = int(mileage_match.group(1).replace(" ", ""))

        year_match = re.search(r"\b(19|20)\d{2}\b", description.get_text(strip=True))
        if year_match:
            details["Year"] = int(year_match.group(0))

        color_match = re.search(r"(\b[^\s]+(?: цвет|color)\b)", description.get_text(strip=True), re.IGNORECASE)
        if color_match:
            details["Color"] = color_match.group(0)

    return details


async def fetch_listings_for_pages(start_page, end_page):
    all_listings = []
    for page in range(start_page, end_page + 1):
        url = f"{BASE_URL}?page={page}"
        html = await fetch_html(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        listings = soup.select(".list-item")
        for listing in listings:
            parsed_listing = await parse_listing(listing)
            if parsed_listing:
                all_listings.append(parsed_listing)
    return all_listings


async def scrape_all_listings(brand, model, start_page, end_page, color=None, min_price=None, max_price=None,
                              min_year=None, max_year=None):
    listings = await fetch_listings_for_pages(start_page, end_page)

    filtered_listings = []
    for listing in listings:
        if brand.lower() not in listing["Title"].lower() or model.lower() not in listing["Title"].lower():
            continue

        if color and ("Color" in listing) and (color.lower() not in listing["Color"].lower()):
            continue

        if min_price and "Price" in listing and int(re.sub(r"[^\d]", "", listing["Price"])) < min_price:
            continue
        if max_price and "Price" in listing and int(re.sub(r"[^\d]", "", listing["Price"])) > max_price:
            continue

        if min_year and "Year" in listing and listing["Year"] < min_year:
            continue
        if max_year and "Year" in listing and listing["Year"] > max_year:
            continue

        filtered_listings.append(listing)

    return filtered_listings


@shared_task(bind=True)
def scrape_and_save_listings(self, color=None, min_price=None, max_price=None,
                             min_year=None, max_year=None):
    try:
        active_detections = Detection.objects.filter(is_active=True)

        for detection in active_detections:
            brand = detection.brand
            model = detection.model

            start_page = 1
            end_page = 10

            listings = async_to_sync(scrape_all_listings)(
                brand=brand.name,
                model=model.name,
                start_page=start_page,
                end_page=end_page,
                color=color,
                min_price=min_price,
                max_price=max_price,
                min_year=min_year,
                max_year=max_year,
            )

            new_listings = []
            for listing in listings:
                if not CarListing.objects.filter(url=listing["URL"]).exists():
                    car_listing = CarListing.objects.create(
                        title=listing["Title"],
                        mileage=listing.get("Mileage"),
                        url=listing["URL"],
                        brand=brand,
                        model=model,
                        image_url=listing.get("Image"),
                    )
                    new_listings.append(car_listing)

            if new_listings:
                message = "🆕 Yangi e'lonlar topildi:\n\n"
                for listing in new_listings[:10]:
                    user_friendly_url = format_url_for_user(listing.url)
                    message += (
                        f"📌 {listing.title}\n"
                        f"🕏 {listing.mileage} km\n"
                        f"🔗 [Havola]({user_friendly_url})\n"
                        f"🖼️ ![Rasm]({listing.image_url})\n\n"
                    )
                notify_user(message, chat_id=detection.user.telegram_id)

                self.retry(countdown=600)
            else:
                notify_user("❗️ Hozircha yangi e'lonlar topilmadi.", chat_id=detection.user.telegram_id)

    except Exception as e:
        logger.error(f"Error: {e}")
        notify_user(f"❌ Xatolik: {e}", chat_id=detection.user.telegram_id)
