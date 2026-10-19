import argparse
import sys
import config
from wda_driver import WDADriver
from agent import IOSAgent

def main():
    parser = argparse.ArgumentParser(description="iOS Autonomous AI Agent - Control iPhone from PC")
    parser.add_argument("goal", nargs="?", help="Task to execute (e.g., 'Open WhatsApp and text Mom')")
    parser.add_argument("--test", action="store_true", help="Test iPhone WDA connection")
    parser.add_argument("--steps", type=int, default=15, help="Maximum number of steps (default: 15)")
    parser.add_argument("--url", default=config.WDA_URL, help="WDA server URL")

    args = parser.parse_args()

    driver = WDADriver(args.url)

    if args.test:
        print(f"[*] Testing connection: {args.url}")
        if driver.is_connected():
            size = driver.get_window_size()
            print(f"[✅] Connection successful! Screen resolution: {size[0]}x{size[1]} points.")
        else:
            print("[❌] Connection failed. Is WebDriverAgent running on the iPhone?")
        return

    goal = args.goal
    if not goal:
        print("=== iOS Autonomous AI Agent ===")
        goal = input("What would you like me to do on your iPhone? > ").strip()

    if not goal:
        print("No goal provided. Exiting.")
        sys.exit(0)

    agent = IOSAgent(wda_url=args.url, max_steps=args.steps)
    agent.run(goal)

if __name__ == "__main__":
    main()
