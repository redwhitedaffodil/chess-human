"""Main entry point for the chess bot."""
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from chess_bot.src.config import Config
from chess_bot.src.game_controller import GameController


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Set up and configure the Selenium WebDriver.
    
    Args:
        headless: Whether to run browser in headless mode
        
    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # Additional options for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set up driver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


def main():
    """Main function to run the chess bot."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s: %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = Config()
    
    # Set up WebDriver
    logger.info("Setting up WebDriver...")
    driver = setup_driver(headless=config.headless)
    
    try:
        # Navigate to chess.com
        logger.info(f"Navigating to {config.chess_url}")
        driver.get(config.chess_url)
        
        # Wait for user to log in and start a game
        logger.info("Please log in and start a game...")
        input("Press Enter when ready to start the bot...")
        
        # Create and run game controller
        controller = GameController(driver, config)
        controller.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
    finally:
        # Clean up
        logger.info("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
