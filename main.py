import argparse
import sys
import config
from wda_driver import WDADriver
from agent import IOSAgent

def main():
    parser = argparse.ArgumentParser(description="iOS Otonom AI Ajanı - iPhone'u PC'den Kontrol Et")
    parser.add_argument("goal", nargs="?", help="Yapılmasını istediğin görev (örn: 'WhatsApp aç Mehmet'e selam yaz')")
    parser.add_argument("--test", action="store_true", help="iPhone WDA bağlantısını test et")
    parser.add_argument("--steps", type=int, default=15, help="Maksimum adım sayısı (varsayılan: 15)")
    parser.add_argument("--url", default=config.WDA_URL, help="WDA URL adresi")

    args = parser.parse_args()

    driver = WDADriver(args.url)

    if args.test:
        print(f"[*] Bağlantı test ediliyor: {args.url}")
        if driver.is_connected():
            size = driver.get_window_size()
            print(f"[✅] Bağlantı başarılı! Ekran çözünürlüğü: {size[0]}x{size[1]} points.")
        else:
            print("[❌] Bağlantı başarısız. Telefonda WDA açık mı?")
        return

    goal = args.goal
    if not goal:
        print("=== iOS Otonom AI Ajanı ===")
        goal = input("Telefonda ne yapmamı istersin? > ").strip()

    if not goal:
        print("Hedef belirtilmedi. Çıkılıyor.")
        sys.exit(0)

    agent = IOSAgent(wda_url=args.url, max_steps=args.steps)
    agent.run(goal)

if __name__ == "__main__":
    main()
