import requests
import json
from playwright.sync_api import  sync_playwright
import time
import datetime

with sync_playwright() as p:
    print("Iniciando scrapeo...")
    init = time.time()
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"https://www.walmart.co.cr/cafe?_q=cafe&fuzzy=0&initialMap=ft&initialQuery=cafe&map=category-3,ft&operator=and&query=/cafe-molido/cafe&searchState")
    page.wait_for_selector("div.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.pa4", state="attached")
    # change wait selector for this: div.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.pa4
    len_before = 0
    round_num = 0
    while True:
        cards = page.query_selector_all("div.vtex-search-result-3-x-galleryItem.vtex-search-result-3-x-galleryItem--normal.pa4")            
        print(f"Found: {len(cards)}")
        if len_before == len(cards):
            round_num = round_num + 1
        else:
            round_num = 0
        len_before = len(cards)
        if round_num >= 30: # If the script try to fetch new items 30 times and not find any or if the condition is met
            data = []
            print("Iniciando...")
            init1 = time.time()
            counter = 1
            for card in cards:
                print(f"Usando: {counter}. Progreso: {(counter / len(cards)) * 100}%")
                text = card.query_selector("span.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body")
                combo = card.query_selector("div.vtex-globalPromo-F.not")
                descuento = card.query_selector("span.vtex-product-price-1-x-savingsPercentage")
                price = card.query_selector("span.vtex-store-components-3-x-currencyContainer.vtex-store-components-3-x-currencyContainer--summary")
                img = card.query_selector("img.vtex-product-summary-2-x-imageNormal.vtex-product-summary-2-x-image")
                link = card.query_selector("a.vtex-product-summary-2-x-clearLink.h-100.flex.flex-column")
                if text and price:
                    data.append({
                        "id": counter,
                        "product_name": text.inner_text(),
                        "product_saving": descuento.inner_text() if descuento else "0%",
                        "product_promo":  combo.inner_text() if combo else "0",
                        "price": price.inner_text() if price else '0',
                        "image_src": img.get_attribute("src"),
                        "link": link.get_attribute("href")
                    })       
                    counter = counter + 1
            with open(f"cafe.json", "w", encoding="utf-8") as archivo:
                archivo.write(json.dumps(data, indent=4, ensure_ascii=False))
            end1 = time.time()
            print(f"Tiempo: {end1 - init1}")
            break
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(300)
    browser.close()